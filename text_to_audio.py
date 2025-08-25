import os
import uuid
from dotenv import load_dotenv
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
import os
ELEVENLABS_API_KEY = os.environ.get('ELEVENLABS_API_KEY')
if not ELEVENLABS_API_KEY:
    try:
        from config import ELEVENLABS_API_KEY as ELEVENLABS_API_KEY_FALLBACK
        ELEVENLABS_API_KEY = ELEVENLABS_API_KEY_FALLBACK
    except Exception:
        ELEVENLABS_API_KEY = None

elevenlabs = ElevenLabs(api_key=ELEVENLABS_API_KEY) if ELEVENLABS_API_KEY else None


def text_to_speech_file(text: str, folder: str) -> str:
    try:
        print(f"[DEBUG] text_to_speech_file called for folder: {folder}")
        folder_path = os.path.join("user_uploads", folder)
        if not os.path.exists(folder_path):
            print(f"[DEBUG] Folder {folder_path} does not exist. Creating...")
            os.makedirs(folder_path, exist_ok=True)
        response = elevenlabs.text_to_speech.convert(
            voice_id="pNInz6obpgDQGcFmaJgB",
            output_format="mp3_22050_32",
            text=text,
            model_id="eleven_turbo_v2_5",
            voice_settings=VoiceSettings(
                stability=0.0,
                similarity_boost=1.0,
                style=0.0,
                use_speaker_boost=True,
                speed=1.0,
            ),
        )
        save_file_path = os.path.join(folder_path, "audio.mp3")
        print(f"[DEBUG] Saving audio to: {save_file_path}")
        with open(save_file_path, "wb") as f:
            chunk_written = False
            for chunk in response:
                if chunk:
                    f.write(chunk)
                    chunk_written = True
        if chunk_written:
            print(f"{save_file_path}: A new audio file was saved successfully!")
        else:
            print(f"[ERROR] No audio data was written for {save_file_path}!")
        return save_file_path
    except Exception as e:
        print(f"[ERROR] Exception in text_to_speech_file: {e}")
        return ""

#text_to_speech_file("THis is testing.", "b4d9d1cc-76c9-11f0-9036-8c6e3e2c6535")

