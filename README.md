# Dynamic Short Video Generator

This Flask app allows users to upload images and a description, then automatically generates a short video (reel) with AI-generated audio narration.

## Features
- Upload images and a description to create a video reel
- AI text-to-speech using ElevenLabs API
- Automatic video generation with ffmpeg
- Gallery of generated reels

## Setup
1. **Clone the repository**
2. **Install dependencies**:
   ```sh
   pip install -r requirements.txt
   ```
3. **Configure environment variables**:
   - Copy `.env` and set your `ELEVENLABS_API_KEY` and `FLASK_SECRET_KEY`.
4. **Install ffmpeg** (required for video processing)
5. **Run the app (development)**:
   ```sh
   python main.py
   ```
6. **Run in production** (example with Waitress):
   ```sh
   pip install waitress
   waitress-serve --port=5000 wsgi:app
   ```

## Security Notes
- Never commit your real API keys to version control.
- File uploads are restricted to images (png, jpg, jpeg).
- Always use a strong `FLASK_SECRET_KEY` in production.

## Folder Structure
- `main.py` - Flask app
- `generate_process.py` - Audio and video processing
- `text_to_audio.py` - ElevenLabs TTS integration
- `user_uploads/` - User-uploaded files
- `static/reels/` - Generated videos

## License
MIT
