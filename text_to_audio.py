import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

ELEVENLABS_API_KEY = os.environ.get('ELEVENLABS_API_KEY')
if not ELEVENLABS_API_KEY:
    print("[ERROR] No ElevenLabs API key found in environment variables")
    ELEVENLABS_API_KEY = None


def create_silence_audio(folder: str, duration: float = 5.0) -> str:
    """
    Create a silent audio file as fallback when TTS fails
    """
    try:
        folder_path = os.path.join("user_uploads", folder)
        os.makedirs(folder_path, exist_ok=True)
        
        save_file_path = os.path.join(folder_path, "audio.mp3")
        
        # Create silent audio using FFmpeg
        import subprocess
        command = f'ffmpeg -y -f lavfi -i "anullsrc=r=22050:cl=mono" -t {duration} -acodec mp3 -ar 22050 "{save_file_path}"'
        
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[INFO] Created silent audio file: {save_file_path}")
            return save_file_path
        else:
            print(f"[ERROR] Failed to create silent audio: {result.stderr}")
            return ""
    except Exception as e:
        print(f"[ERROR] Exception creating silent audio: {e}")
        return ""


def text_to_speech_file(text: str, folder: str) -> str:
    try:
        print(f"[DEBUG] text_to_speech_file called for folder: {folder}")
        
        if not ELEVENLABS_API_KEY:
            print("[ERROR] ElevenLabs API key not found - using silent audio fallback")
            return create_silence_audio(folder)
        
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
        response = requests.post(url, json=data, headers=headers, timeout=30)
        
        if response.status_code == 200:
            save_file_path = os.path.join(folder_path, "audio.mp3")
            print(f"[DEBUG] Saving audio to: {save_file_path}")
            
            with open(save_file_path, "wb") as f:
                f.write(response.content)
                
            print(f"{save_file_path}: A new audio file was saved successfully!")
            return save_file_path
        else:
            print(f"[ERROR] ElevenLabs API error: {response.status_code} - {response.text}")
            
            # Check for specific errors and provide fallback
            if response.status_code == 401:
                print("[INFO] ElevenLabs API access denied - likely free tier suspended or invalid key")
                print("[INFO] Creating silent audio as fallback...")
                return create_silence_audio(folder)
            elif response.status_code == 429:
                print("[INFO] ElevenLabs API rate limit exceeded - creating silent audio as fallback...")
                return create_silence_audio(folder)
            else:
                print("[INFO] ElevenLabs API error - creating silent audio as fallback...")
                return create_silence_audio(folder)
            
    except requests.exceptions.Timeout:
        print("[ERROR] ElevenLabs API timeout - creating silent audio as fallback...")
        return create_silence_audio(folder)
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Network error with ElevenLabs API: {e} - creating silent audio as fallback...")
        return create_silence_audio(folder)
    except Exception as e:
        print(f"[ERROR] Exception in text_to_speech_file: {e} - creating silent audio as fallback...")
        return create_silence_audio(folder)

