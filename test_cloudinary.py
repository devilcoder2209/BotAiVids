import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get Cloudinary URL
cloudinary_url = os.getenv('CLOUDINARY_URL')
print(f"Cloudinary URL: {cloudinary_url}")

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

# Print configuration to debug
print(f"Cloud name: {cloudinary.config().cloud_name}")
print(f"API key: {cloudinary.config().api_key}")
print(f"API secret: {'*' * len(cloudinary.config().api_secret) if cloudinary.config().api_secret else 'None'}")

# Test upload
try:
    result = cloudinary.uploader.upload(
        'static/reels/a394185a-81ee-11f0-9c67-b40ede3fddf5.mp4',
        resource_type='video',
        public_id='videos/a394185a-81ee-11f0-9c67-b40ede3fddf5',
        folder='bot_ai_vids'
    )
    print(f'Upload successful: {result.get("secure_url")}')
except Exception as e:
    print(f'Upload failed: {e}')
