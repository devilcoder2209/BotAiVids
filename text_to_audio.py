import os
import requests
import subprocess
import random
from dotenv import load_dotenv

# Load environment variables (for local development only)
load_dotenv()

ELEVENLABS_API_KEY = os.environ.get('ELEVENLABS_API_KEY')
print(f"[DEBUG] API Key loaded: {'Yes' if ELEVENLABS_API_KEY else 'No'}")
print(f"[DEBUG] API Key length: {len(ELEVENLABS_API_KEY) if ELEVENLABS_API_KEY else 0}")
if not ELEVENLABS_API_KEY:
    print("[ERROR] No ElevenLabs API key found in environment variables")
    print("[DEBUG] Available env vars:", [k for k in os.environ.keys() if 'ELEVEN' in k])
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
        print(f"[DEBUG] URL: {url}")
        print(f"[DEBUG] Headers: {dict(headers)}")
        print(f"[DEBUG] Text length: {len(text)} characters")
        
        try:
            response = requests.post(url, json=data, headers=headers, timeout=30)
            print(f"[DEBUG] Response status: {response.status_code}")
            print(f"[DEBUG] Response headers: {dict(response.headers)}")
        except requests.exceptions.Timeout:
            print("[ERROR] Request timeout - network connectivity issue")
            print("[FALLBACK] Creating background audio instead...")
            return create_fallback_audio(folder, 3.0)
        except requests.exceptions.ConnectionError:
            print("[ERROR] Connection error - cannot reach ElevenLabs API")
            print("[FALLBACK] Creating background audio instead...")
            return create_fallback_audio(folder, 3.0)
        except Exception as req_error:
            print(f"[ERROR] Request exception: {req_error}")
            print("[FALLBACK] Creating background audio instead...")
            return create_fallback_audio(folder, 3.0)
        
        if response.status_code == 200:
            save_file_path = os.path.join(folder_path, "audio.mp3")
            print(f"[DEBUG] Saving audio to: {save_file_path}")
            print(f"[DEBUG] Audio content size: {len(response.content)} bytes")
            
            with open(save_file_path, "wb") as f:
                f.write(response.content)
                
            # Verify file was created and has content
            if os.path.exists(save_file_path) and os.path.getsize(save_file_path) > 0:
                print(f"[SUCCESS] Audio file saved successfully: {save_file_path}")
                print(f"[SUCCESS] File size: {os.path.getsize(save_file_path)} bytes")
                return save_file_path
            else:
                print(f"[ERROR] Audio file not created or empty")
                print("[FALLBACK] Creating background audio instead...")
                return create_fallback_audio(folder, 3.0)
        else:
            print(f"[ERROR] ElevenLabs API error: {response.status_code}")
            print(f"[ERROR] Response text: {response.text}")
            if response.status_code == 401:
                print("[ERROR] Authentication failed - check API key")
            elif response.status_code == 429:
                print("[ERROR] Rate limit exceeded - too many requests")
            elif response.status_code >= 500:
                print("[ERROR] Server error on ElevenLabs side")
            print("[FALLBACK] Creating background audio instead...")
            return create_fallback_audio(folder, 3.0)
            
    except Exception as e:
        print(f"[ERROR] Exception in text_to_speech_file: {e}")
        print("[FALLBACK] Creating background audio instead...")
        return create_fallback_audio(folder, 3.0)

