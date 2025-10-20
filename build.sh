#!/bin/bash
set -e

echo "🔧 Starting build process..."

# Update package list
echo "📦 Updating package list..."
apt-get update -qq

# Install FFmpeg with error handling
echo "🎬 Installing FFmpeg..."
if apt-get install -y ffmpeg; then
    echo "✅ FFmpeg installed successfully via apt"
    ffmpeg -version | head -1
elif command -v snap >/dev/null 2>&1; then
    echo "⚠️  apt failed, trying snap..."
    snap install ffmpeg
    echo "✅ FFmpeg installed via snap"
else
    echo "⚠️  System package managers failed, downloading static binary..."
    # Download static FFmpeg binary as last resort
    wget -q https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz
    tar -xf ffmpeg-release-amd64-static.tar.xz
    # Find the extracted directory (name varies)
    FFMPEG_DIR=$(find . -name "ffmpeg-*-amd64-static" -type d | head -1)
    if [ -n "$FFMPEG_DIR" ]; then
        cp "$FFMPEG_DIR/ffmpeg" /usr/local/bin/
        chmod +x /usr/local/bin/ffmpeg
        echo "✅ FFmpeg static binary installed to /usr/local/bin/"
        rm -rf ffmpeg-*-amd64-static*
    else
        echo "❌ Failed to download static FFmpeg binary"
    fi
fi

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Initialize database
echo "🗄️  Initializing database..."
python init_db.py

echo "🎉 Build process completed!"

# Test FFmpeg availability
echo "🧪 Testing FFmpeg..."
if command -v ffmpeg >/dev/null 2>&1; then
    echo "✅ FFmpeg is available in PATH"
    ffmpeg -version | head -1
else
    echo "❌ FFmpeg is NOT available in PATH"
    echo "📍 Checking common locations..."
    ls -la /usr/bin/ffmpeg 2>/dev/null || echo "  - Not in /usr/bin/"
    ls -la /usr/local/bin/ffmpeg 2>/dev/null || echo "  - Not in /usr/local/bin/"
    which ffmpeg 2>/dev/null || echo "  - Not found with 'which'"
fi
