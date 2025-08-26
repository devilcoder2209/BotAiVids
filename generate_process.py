# This folder looks for files that have been recently uploaded in user_uploads
import os
import time
import subprocess
import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
from text_to_audio import text_to_speech_file

# Load environment variables
load_dotenv()

def cleanup_local_files(folder, output_video_path):
    """
    Clean up local files after successful Cloudinary upload.
    Important for Render's ephemeral storage to avoid disk space issues.
    """
    try:
        # Remove the output video file
        if os.path.exists(output_video_path):
            os.remove(output_video_path)
            print(f"[CLEANUP] Removed local video file: {output_video_path}")
        
        # Remove uploaded images and audio (keeping description.txt and input.txt for debugging)
        user_folder = f"user_uploads/{folder}"
        if os.path.exists(user_folder):
            for file in os.listdir(user_folder):
                file_path = os.path.join(user_folder, file)
                # Keep text files for potential debugging, remove media files
                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.mp3', '.wav')):
                    try:
                        os.remove(file_path)
                        print(f"[CLEANUP] Removed: {file_path}")
                    except Exception as e:
                        print(f"[CLEANUP WARNING] Could not remove {file_path}: {e}")
            
            # If folder is empty (except text files), it will be cleaned up by OS eventually
            remaining_files = [f for f in os.listdir(user_folder) 
                             if not f.lower().endswith(('.txt',))]
            if not remaining_files:
                print(f"[CLEANUP] Folder {user_folder} cleaned of media files")
                
    except Exception as e:
        print(f"[CLEANUP ERROR] Failed to cleanup files: {e}")

# Configure Cloudinary
cloudinary_url = os.getenv('CLOUDINARY_URL')
if cloudinary_url:
    try:
        cloudinary.config(cloudinary_url=cloudinary_url)
        # Verify configuration worked
        if not cloudinary.config().cloud_name:
            raise ValueError("Cloudinary URL parsing failed")
    except Exception as e:
        print(f"[WARNING] Failed to configure Cloudinary with URL: {e}")
        # Fallback to individual parameters
        cloudinary.config(
            cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
            api_key=os.getenv('CLOUDINARY_API_KEY'),
            api_secret=os.getenv('CLOUDINARY_API_SECRET')
        )
else:
    cloudinary.config(
        cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
        api_key=os.getenv('CLOUDINARY_API_KEY'),
        api_secret=os.getenv('CLOUDINARY_API_SECRET')
    )

def update_video_status(folder, status, cloudinary_url=None):
    """Update video status in database"""
    try:
        # Import here to avoid circular imports
        from app import app, db, Video
        with app.app_context():
            video = Video.query.filter_by(uuid=folder).first()
            if video:
                video.status = status
                if cloudinary_url:
                    video.cloudinary_url = cloudinary_url
                db.session.commit()
                print(f"[DATABASE] Updated video {folder} status to {status}")
            else:
                print(f"[WARNING] Video {folder} not found in database")
    except Exception as e:
        print(f"[ERROR] Failed to update database for {folder}: {e}")

def text_to_speech(folder: str):
    print(f"Converting text to speech for {folder}...")
    desc_path = f"user_uploads/{folder}/description.txt"
    if not os.path.exists(desc_path):
        print(f"[ERROR] description.txt not found for {folder}")
        return
    with open(desc_path, "r") as f:
        text = f.read()
    print(text, folder)
    text_to_speech_file(text, folder)
def create_reel(folder):
    """
    Creates a video reel from images and audio for a given folder.
    
    Args:
        folder (str): The folder name in user_uploads containing the images and audio
        
    Returns:
        str or None: URL/path to the created video, or None if creation failed
        
    Note: The scale filter 'scale=trunc(iw/2)*2:trunc(ih/2)*2' is essential to ensure
    both width and height are even numbers, which is required by the H.264 encoder.
    Without this, you'll get "height not divisible by 2" errors.
    """
    input_txt_path = f"user_uploads/{folder}/input.txt"
    print(f"[DEBUG] Reading {input_txt_path}...")
    if not os.path.exists(input_txt_path):
        print(f"[ERROR] input.txt not found for {folder}")
        return None
    with open(input_txt_path, "r") as f:
        lines = f.readlines()
    print(f"[DEBUG] input.txt contents:\n{''.join(lines)}")
    
    # Check that all referenced files exist and are valid images
    import imghdr
    missing_files = []
    invalid_images = []
    for line in lines:
        if line.startswith("file "):
            img_file = line.split("'")[1]
            img_path = os.path.join(f"user_uploads/{folder}", img_file)
            if not os.path.exists(img_path):
                missing_files.append(img_file)
            else:
                if imghdr.what(img_path) is None:
                    invalid_images.append(img_file)
    if missing_files:
        print(f"[ERROR] The following files referenced in input.txt are missing: {missing_files}")
        return None
    if invalid_images:
        print(f"[ERROR] The following files are not valid images: {invalid_images}")
        return None
    
    # Check audio.mp3 exists and is not empty
    audio_path = f"user_uploads/{folder}/audio.mp3"
    if not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
        print(f"[ERROR] audio.mp3 is missing or empty for {folder}")
        return None
    
    # Calculate total video duration from input.txt
    video_duration = 0
    for line in lines:
        if line.strip().startswith("duration "):
            video_duration += float(line.strip().split()[1])
    
    print(f"[DEBUG] Total video duration: {video_duration} seconds")
    
    # Create output directory for reels if it doesn't exist
    os.makedirs("static/reels", exist_ok=True)
    output_video_path = f"static/reels/{folder}.mp4"
    
    # Enhanced ffmpeg command to loop audio to match video duration
    # This ensures all images are shown even if audio is shorter
    command = f'''ffmpeg -y \
-f concat -safe 0 -i user_uploads/{folder}/input.txt \
-stream_loop -1 -i user_uploads/{folder}/audio.mp3 \
-vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" \
-c:v libx264 -pix_fmt yuv420p -c:a aac \
-t {video_duration} {output_video_path}'''
    
    print(f"[DEBUG] Running ffmpeg command: {command}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print(f"[FFMPEG STDOUT]:\n{result.stdout}")
        if result.stderr:
            print(f"[FFMPEG STDERR]:\n{result.stderr}")
        if result.returncode != 0:
            print(f"[ERROR] ffmpeg failed with exit code {result.returncode}")
            # Check for common errors and provide helpful messages
            if "height not divisible by 2" in result.stderr or "width not divisible by 2" in result.stderr:
                print("[ERROR] Image dimensions issue - this should be fixed by the scale filter")
            elif "No such file or directory" in result.stderr:
                print("[ERROR] Input file not found - check if all referenced files exist")
            elif "Invalid argument" in result.stderr:
                print("[ERROR] Invalid FFmpeg parameters - check input format and codec settings")
            # Update database with failed status
            update_video_status(folder, 'failed')
            return None
        
        # Check if output file was actually created and has content
        if not os.path.exists(output_video_path) or os.path.getsize(output_video_path) == 0:
            print(f"[ERROR] Output video file was not created or is empty: {output_video_path}")
            update_video_status(folder, 'failed')
            return None
            
        print(f"[SUCCESS] Video created successfully: {output_video_path} ({os.path.getsize(output_video_path)} bytes)")
        print(f"Creating reel for {folder}...")
        
        # Upload to Cloudinary
        try:
            print(f"[DEBUG] Uploading {output_video_path} to Cloudinary...")
            upload_result = cloudinary.uploader.upload(
                output_video_path,
                resource_type="video",
                public_id=f"videos/{folder}",
                folder="bot_ai_vids"
            )
            cloudinary_url = upload_result.get('secure_url')
            print(f"[SUCCESS] Video uploaded to Cloudinary: {cloudinary_url}")
            
            # Update database with Cloudinary URL
            update_video_status(folder, 'completed', cloudinary_url)
            
            # Clean up local files after successful upload (important for Render)
            cleanup_local_files(folder, output_video_path)
                
            return cloudinary_url
        except Exception as e:
            print(f"[ERROR] Failed to upload to Cloudinary: {e}")
            # Return local path as fallback and update database
            local_url = f"/static/reels/{folder}.mp4"
            update_video_status(folder, 'completed', local_url)
            return local_url
            
    except Exception as e:
        print(f"[ERROR] Exception running ffmpeg: {e}")
        # Update database with failed status
        update_video_status(folder, 'failed')
        return None
    
    

if __name__ == "__main__":
    while True:
        print("Processing queue...")
        
        # Get processing videos from database instead of done.txt
        try:
            from app import app, db, Video
            with app.app_context():
                # Find videos that need processing
                pending_videos = Video.query.filter_by(status='processing').all()
                
                for video in pending_videos:
                    folder = video.uuid
                    folder_path = f"user_uploads/{folder}"
                    
                    # Check if folder exists and has required files
                    if not os.path.exists(folder_path):
                        print(f"[WARNING] Folder {folder_path} not found, marking as failed")
                        update_video_status(folder, 'failed')
                        continue
                    
                    # Check if description.txt exists
                    desc_path = f"{folder_path}/description.txt"
                    if not os.path.exists(desc_path):
                        print(f"[WARNING] description.txt not found for {folder}, skipping")
                        continue
                    
                    print(f"[INFO] Processing video: {folder}")
                    try:
                        # Set status to processing in case it's not already
                        update_video_status(folder, 'processing')
                        
                        # Process the video
                        text_to_speech(folder)  # convert from text to audio   
                        result = create_reel(folder)  # create a reel from the audio and images
                        
                        if result:
                            print(f"[SUCCESS] Completed processing for {folder}")
                        else:
                            print(f"[ERROR] Failed processing for {folder}")
                            
                    except Exception as e:
                        print(f"[ERROR] Exception processing {folder}: {e}")
                        update_video_status(folder, 'failed')
                        
        except Exception as e:
            print(f"[ERROR] Database query failed: {e}")
            # Fallback to old method if database fails
            with open ("done.txt", "r") as f:
                done_folders = f.readlines()
            done_folders = [line.strip() for line in done_folders]   
            folders = os.listdir("user_uploads")
            for folder in folders:
                if folder not in done_folders:
                    text_to_speech(folder)  # convert from text to audio   
                    create_reel(folder) # create a reel from the audio and images
                    with open("done.txt", "a") as f:
                        f.write(folder + "\n")
                        
        time.sleep(5)