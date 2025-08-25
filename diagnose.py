#!/usr/bin/env python3
"""
Diagnostic script to check Render environment for BotAiVids
Run this in Render shell to diagnose reel creation issues
"""

import os
import sys

def check_environment():
    """Check environment variables and dependencies"""
    print("=== BotAiVids Environment Diagnostic ===\n")
    
    print("1. Python Version:")
    print(f"   {sys.version}\n")
    
    print("2. Environment Variables:")
    env_vars = [
        'ELEVENLABS_API_KEY',
        'CLOUDINARY_CLOUD_NAME', 
        'CLOUDINARY_API_KEY',
        'CLOUDINARY_API_SECRET',
        'FLASK_SECRET_KEY',
        'DATABASE_URL',
        'FLASK_ENV'
    ]
    
    for var in env_vars:
        value = os.environ.get(var)
        if value:
            # Mask sensitive values
            if 'KEY' in var or 'SECRET' in var or 'URL' in var:
                masked = value[:8] + '...' + value[-4:] if len(value) > 12 else '***'
                print(f"   ✅ {var}: {masked}")
            else:
                print(f"   ✅ {var}: {value}")
        else:
            print(f"   ❌ {var}: NOT SET")
    
    print("\n3. Required Packages:")
    packages = [
        'flask', 'flask_login', 'flask_sqlalchemy', 'flask_admin',
        'gunicorn', 'psycopg2', 'requests', 'cloudinary', 'PIL'
    ]
    
    for package in packages:
        try:
            if package == 'PIL':
                import PIL
                print(f"   ✅ Pillow: {PIL.__version__}")
            else:
                module = __import__(package)
                version = getattr(module, '__version__', 'Unknown')
                print(f"   ✅ {package}: {version}")
        except ImportError:
            print(f"   ❌ {package}: NOT INSTALLED")
    
    print("\n4. System Commands:")
    commands = ['ffmpeg']
    
    for cmd in commands:
        if os.system(f"which {cmd} > /dev/null 2>&1") == 0:
            print(f"   ✅ {cmd}: Available")
        else:
            print(f"   ❌ {cmd}: NOT FOUND")
    
    print("\n5. File System:")
    paths = ['/opt/render/project/src', '/tmp', '/app']
    
    for path in paths:
        if os.path.exists(path):
            print(f"   ✅ {path}: Exists")
            try:
                test_file = os.path.join(path, 'test_write.tmp')
                with open(test_file, 'w') as f:
                    f.write('test')
                os.remove(test_file)
                print(f"      - Write permission: ✅")
            except:
                print(f"      - Write permission: ❌")
        else:
            print(f"   ❌ {path}: Does not exist")
    
    print("\n6. User Uploads Directory:")
    uploads_dir = 'user_uploads'
    if os.path.exists(uploads_dir):
        print(f"   ✅ {uploads_dir}: Exists")
        print(f"      - Contents: {os.listdir(uploads_dir)}")
    else:
        print(f"   ❌ {uploads_dir}: Does not exist")
        try:
            os.makedirs(uploads_dir, exist_ok=True)
            print(f"   ✅ Created {uploads_dir}")
        except Exception as e:
            print(f"   ❌ Failed to create {uploads_dir}: {e}")

def test_apis():
    """Test API connections"""
    print("\n7. API Tests:")
    
    # Test ElevenLabs
    api_key = os.environ.get('ELEVENLABS_API_KEY')
    if api_key:
        try:
            import requests
            headers = {"xi-api-key": api_key}
            response = requests.get("https://api.elevenlabs.io/v1/voices", headers=headers, timeout=10)
            if response.status_code == 200:
                print("   ✅ ElevenLabs API: Connected")
            else:
                print(f"   ❌ ElevenLabs API: Error {response.status_code}")
        except Exception as e:
            print(f"   ❌ ElevenLabs API: {e}")
    else:
        print("   ❌ ElevenLabs API: No API key")
    
    # Test Cloudinary
    try:
        import cloudinary
        cloud_name = os.environ.get('CLOUDINARY_CLOUD_NAME')
        if cloud_name:
            cloudinary.config(
                cloud_name=cloud_name,
                api_key=os.environ.get('CLOUDINARY_API_KEY'),
                api_secret=os.environ.get('CLOUDINARY_API_SECRET')
            )
            # Simple config test
            if cloudinary.config().cloud_name:
                print("   ✅ Cloudinary: Configured")
            else:
                print("   ❌ Cloudinary: Configuration failed")
        else:
            print("   ❌ Cloudinary: No cloud name")
    except Exception as e:
        print(f"   ❌ Cloudinary: {e}")

def test_database():
    """Test database connection"""
    print("\n8. Database Test:")
    try:
        from app import app, db, User, Video
        with app.app_context():
            # Test database connection
            user_count = User.query.count()
            video_count = Video.query.count()
            print(f"   ✅ Database: Connected")
            print(f"      - Users: {user_count}")
            print(f"      - Videos: {video_count}")
    except Exception as e:
        print(f"   ❌ Database: {e}")

if __name__ == "__main__":
    check_environment()
    test_apis()
    test_database()
    print("\n=== Diagnostic Complete ===")
