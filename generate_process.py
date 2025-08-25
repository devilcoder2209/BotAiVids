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
def create_reel_with_python_ffmpeg(folder):
    """
    Alternative video creation using ffmpeg-python library
    This is a fallback when system FFmpeg is not available
    """
    try:
        import ffmpeg
        print(f"[INFO] Using ffmpeg-python library for video creation...")
        
        input_txt_path = f"user_uploads/{folder}/input.txt"
        audio_path = f"user_uploads/{folder}/audio.mp3"
        output_video_path = f"static/reels/{folder}.mp4"
        
        # Create output directory
        os.makedirs("static/reels", exist_ok=True)
        
        # Read input.txt to get image list
        if not os.path.exists(input_txt_path):
            print(f"[ERROR] input.txt not found for {folder}")
            update_video_status(folder, 'failed')
            return None
            
        with open(input_txt_path, "r") as f:
            lines = f.readlines()
        
        # Extract image paths
        image_paths = []
        for line in lines:
            if line.startswith("file "):
                img_file = line.split("'")[1]
                img_path = os.path.join(f"user_uploads/{folder}", img_file)
                if os.path.exists(img_path):
                    image_paths.append(img_path)
        
        if not image_paths:
            print(f"[ERROR] No valid images found for {folder}")
            update_video_status(folder, 'failed')
            return None
        
        # Create video using ffmpeg-python
        # Create input stream from images
        input_stream = ffmpeg.input(f'user_uploads/{folder}/input.txt', 
                                  f='concat', safe=0)
        audio_stream = ffmpeg.input(audio_path)
        
        # Process video with scaling and encoding
        video = input_stream.video.filter('scale', 'trunc(iw/2)*2', 'trunc(ih/2)*2')
        
        # Combine video and audio
        output = ffmpeg.output(
            video, audio_stream,
            output_video_path,
            vcodec='libx264',
            pix_fmt='yuv420p',
            acodec='aac',
            shortest=None
        )
        
        # Run the ffmpeg command
        ffmpeg.run(output, overwrite_output=True, quiet=True)
        
        # Check if output was created
        if os.path.exists(output_video_path) and os.path.getsize(output_video_path) > 0:
            print(f"[SUCCESS] Video created with ffmpeg-python: {output_video_path}")
            
            # Upload to Cloudinary
            try:
                upload_result = cloudinary.uploader.upload(
                    output_video_path,
                    resource_type="video",
                    public_id=f"videos/{folder}",
                    folder="bot_ai_vids"
                )
                cloudinary_url = upload_result.get('secure_url')
                print(f"[SUCCESS] Video uploaded to Cloudinary: {cloudinary_url}")
                
                update_video_status(folder, 'completed', cloudinary_url)
                
                # Clean up local file
                if os.path.exists(output_video_path):
                    os.remove(output_video_path)
                    
                return cloudinary_url
            except Exception as e:
                print(f"[ERROR] Failed to upload to Cloudinary: {e}")
                local_url = f"/static/reels/{folder}.mp4"
                update_video_status(folder, 'completed', local_url)
                return local_url
        else:
            print(f"[ERROR] ffmpeg-python failed to create video")
            update_video_status(folder, 'failed')
            return None
            
    except ImportError:
        print("[ERROR] ffmpeg-python library not available")
        update_video_status(folder, 'failed')
        return None
    except Exception as e:
        print(f"[ERROR] ffmpeg-python error: {e}")
        update_video_status(folder, 'failed')
        return None

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
    
    # Create output directory for reels if it doesn't exist
    os.makedirs("static/reels", exist_ok=True)
    output_video_path = f"static/reels/{folder}.mp4"
    
    # Fix the ffmpeg command to use dynamic folder paths and ensure even dimensions
    # The scale filter ensures both width and height are even numbers (required for H.264)
    command = f'''ffmpeg -y -f concat -safe 0 -i user_uploads/{folder}/input.txt \
-i user_uploads/{folder}/audio.mp3 \
-vf "scale=trunc(iw/2)*2:trunc(ih/2)*2" \
-c:v libx264 -pix_fmt yuv420p -c:a aac -shortest {output_video_path}'''
    
    print(f"[DEBUG] Running ffmpeg command: {command}")
    
    # First, check if FFmpeg is available
    try:
        ffmpeg_check = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True)
        if ffmpeg_check.returncode != 0:
            print(f"[ERROR] FFmpeg not available or not working properly")
            print(f"[FFMPEG CHECK STDERR]: {ffmpeg_check.stderr}")
            update_video_status(folder, 'failed')
            return None
        else:
            print(f"[DEBUG] FFmpeg is available: {ffmpeg_check.stdout.split('version')[1].split('Copyright')[0].strip()}")
    except FileNotFoundError:
        print("[ERROR] FFmpeg binary not found in system PATH")
        print("[INFO] Trying alternative ffmpeg-python approach...")
        return create_reel_with_python_ffmpeg(folder)
    except Exception as e:
        print(f"[ERROR] Error checking FFmpeg availability: {e}")
        print("[INFO] Trying alternative ffmpeg-python approach...")
        return create_reel_with_python_ffmpeg(folder)
    
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
            elif "ffmpeg: not found" in result.stderr or "command not found" in result.stderr:
                print("[ERROR] FFmpeg binary not found - check if FFmpeg is properly installed")
            else:
                print("[ERROR] Unknown FFmpeg error - check the stderr output above")
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
            
            # Clean up local file after upload
            if os.path.exists(output_video_path):
                os.remove(output_video_path)
                print(f"[DEBUG] Local video file {output_video_path} removed")
                
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