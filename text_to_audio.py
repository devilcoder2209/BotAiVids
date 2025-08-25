import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

ELEVENLABS_API_KEY = os.environ.get('ELEVENLABS_API_KEY')
if not ELEVENLABS_API_KEY:
    try:
        from config import ELEVENLABS_API_KEY as ELEVENLABS_API_KEY_FALLBACK
        ELEVENLABS_API_KEY = ELEVENLABS_API_KEY_FALLBACK
    except Exception:
        print("[ERROR] No ElevenLabs API key found in environment or config")
        ELEVENLABS_API_KEY = None


def text_to_speech_file(text: str, folder: str) -> str:
    try:
        print(f"[DEBUG] text_to_speech_file called for folder: {folder}")
        
        if not ELEVENLABS_API_KEY:
            print("[ERROR] ElevenLabs API key not found")
            return ""
        
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
            return ""
            
    except Exception as e:
        print(f"[ERROR] Exception in text_to_speech_file: {e}")
        return ""

