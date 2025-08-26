import os
import requests
import subprocess
import random
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

ELEVENLABS_API_KEY = os.environ.get('ELEVENLABS_API_KEY')
if not ELEVENLABS_API_KEY:
    print("[ERROR] No ElevenLabs API key found in environment variables")
    ELEVENLABS_API_KEY = None

def create_fallback_audio(folder: str, duration: float = 3.0) -> str:
    """
    Create a fallback audio file when ElevenLabs API fails.
    This creates a pleasant ambient background tone.
    """
    try:
        folder_path = os.path.join("user_uploads", folder)
        audio_path = os.path.join(folder_path, "audio.mp3")
        
        # Create a pleasant ambient background with multiple tones
        # Using a combination of frequencies to create a more pleasant sound
        command = f'''ffmpeg -y \
-f lavfi -i "sine=frequency=220:duration={duration}" \
-f lavfi -i "sine=frequency=330:duration={duration}" \
-f lavfi -i "sine=frequency=440:duration={duration}" \
-filter_complex "[0:a][1:a][2:a]amix=inputs=3:duration=first:weights=0.3 0.2 0.1,volume=0.1" \
-ar 44100 -ac 1 -b:a 128k "{audio_path}"'''
        
        print(f"[FALLBACK] Creating ambient background audio with FFmpeg...")
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0 and os.path.exists(audio_path):
            print(f"[SUCCESS] Fallback audio created: {audio_path}")
            return audio_path
        else:
            print(f"[ERROR] Failed to create fallback audio: {result.stderr}")
            # Try simpler fallback
            simple_command = f'ffmpeg -y -f lavfi -i "sine=frequency=440:duration={duration}" -ar 44100 -ac 1 -b:a 128k -af "volume=0.1" "{audio_path}"'
            simple_result = subprocess.run(simple_command, shell=True, capture_output=True, text=True)
            if simple_result.returncode == 0 and os.path.exists(audio_path):
                print(f"[SUCCESS] Simple fallback audio created: {audio_path}")
                return audio_path
            return ""
            
    except Exception as e:
        print(f"[ERROR] Exception creating fallback audio: {e}")
        return ""


def text_to_speech_file(text: str, folder: str) -> str:
    try:
        print(f"[DEBUG] text_to_speech_file called for folder: {folder}")
        
        if not ELEVENLABS_API_KEY:
            print("[ERROR] ElevenLabs API key not found - using fallback audio")
            return create_fallback_audio(folder, 3.0)
        
        folder_path = os.path.join("user_uploads", folder)
        if not os.path.exists(folder_path):
            print(f"[DEBUG] Folder {folder_path} does not exist. Creating...")
            os.makedirs(folder_path, exist_ok=True)
            
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
            print("[FALLBACK] Creating background audio instead...")
            return create_fallback_audio(folder, 3.0)
            
    except Exception as e:
        print(f"[ERROR] Exception in text_to_speech_file: {e}")
        print("[FALLBACK] Creating background audio instead...")
        return create_fallback_audio(folder, 3.0)

