import os
import requests
import shutil
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

ELEVENLABS_API_KEY = os.environ.get('ELEVENLABS_API_KEY')
if not ELEVENLABS_API_KEY:
    print("[ERROR] No ElevenLabs API key found in environment variables")
    ELEVENLABS_API_KEY = None


def get_fallback_audio(folder_path: str) -> str:
    """
    Copy a background music file as fallback when TTS fails
    """
    try:
        # List of available background music files
        background_music_files = [
            "static/songs/1.mp3",
            "static/songs/2.mp3", 
            "static/songs/3.mp3"
        ]
        
        # Find the first available background music file
        for music_file in background_music_files:
            if os.path.exists(music_file):
                fallback_path = os.path.join(folder_path, "audio.mp3")
                shutil.copy2(music_file, fallback_path)
                print(f"[INFO] Using fallback background music: {music_file}")
                return fallback_path
        
        print("[WARNING] No background music files found in static/songs/")
        return ""
        
    except Exception as e:
        print(f"[ERROR] Failed to copy background music: {e}")
        return ""


def text_to_speech_file(text: str, folder: str) -> str:
    try:
        print(f"[DEBUG] text_to_speech_file called for folder: {folder}")
        
        folder_path = os.path.join("user_uploads", folder)
        if not os.path.exists(folder_path):
            print(f"[DEBUG] Folder {folder_path} does not exist. Creating...")
            os.makedirs(folder_path, exist_ok=True)
        
        if not ELEVENLABS_API_KEY:
            print("[INFO] ElevenLabs API key not found, using background music fallback")
            return get_fallback_audio(folder_path)
            
        # ElevenLabs API endpoint
        voice_id = "pNInz6obpgDQGcFmaJgB"  # Adam voice
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
        
        headers = {
            "Accept": "audio/mpeg",
            "Content-Type": "application/json",
            "xi-api-key": ELEVENLABS_API_KEY
        }
        
        data = {
            "text": text,
            "model_id": "eleven_turbo_v2_5",
            "voice_settings": {
                "stability": 0.0,
                "similarity_boost": 1.0,
                "style": 0.0,
                "use_speaker_boost": True,
                "speed": 1.0
            },
            "output_format": "mp3_22050_32"
        }
        
        print(f"[DEBUG] Making API request to ElevenLabs...")
        response = requests.post(url, json=data, headers=headers)
        
        if response.status_code == 200:
            save_file_path = os.path.join(folder_path, "audio.mp3")
            print(f"[DEBUG] Saving audio to: {save_file_path}")
            
            with open(save_file_path, "wb") as f:
                f.write(response.content)
                
            print(f"{save_file_path}: A new audio file was saved successfully!")
            return save_file_path
        else:
            print(f"[ERROR] ElevenLabs API error: {response.status_code} - {response.text}")
            
            # Check for specific API errors and provide fallback
            if response.status_code == 401:
                print("[INFO] API key issue detected, falling back to background music")
            elif response.status_code == 429:
                print("[INFO] Rate limit exceeded, falling back to background music") 
            else:
                print("[INFO] API error occurred, falling back to background music")
                
            return get_fallback_audio(folder_path)
            
    except Exception as e:
        print(f"[ERROR] Exception in text_to_speech_file: {e}")
        print("[INFO] Exception occurred, falling back to background music")
        return get_fallback_audio(folder_path)

