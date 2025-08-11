# This folder looks for files that have been recently uploaded in user_uploads
import os
import time
import subprocess
from text_to_audio import text_to_speech_file

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
    input_txt_path = f"user_uploads/{folder}/input.txt"
    print(f"[DEBUG] Reading {input_txt_path}...")
    if not os.path.exists(input_txt_path):
        print(f"[ERROR] input.txt not found for {folder}")
        return
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
        return
    if invalid_images:
        print(f"[ERROR] The following files are not valid images: {invalid_images}")
        return
    # Check audio.mp3 exists and is not empty
    audio_path = f"user_uploads/{folder}/audio.mp3"
    if not os.path.exists(audio_path) or os.path.getsize(audio_path) == 0:
        print(f"[ERROR] audio.mp3 is missing or empty for {folder}")
        return
    command = f'''ffmpeg -y -f concat -safe 0 -i user_uploads/{folder}/input.txt -i user_uploads/{folder}/audio.mp3 -c:v libx264 -c:a aac -strict experimental static/reels/{folder}.mp4'''
    print(f"[DEBUG] Running ffmpeg command: {command}")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        print(f"[FFMPEG STDOUT]:\n{result.stdout}")
        print(f"[FFMPEG STDERR]:\n{result.stderr}")
        if result.returncode != 0:
            print(f"[ERROR] ffmpeg failed with exit code {result.returncode}")
            return
        print(f"Creating reel for {folder}...")
    except Exception as e:
        print(f"[ERROR] Exception running ffmpeg: {e}")
    
    

if __name__ == "__main__":
    while True:
        print("Processing queue...")
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