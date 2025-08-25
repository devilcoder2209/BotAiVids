#!/usr/bin/env python3
"""
FFmpeg Diagnostic Script
Tests FFmpeg availability and basic functionality in the production environment.
"""

import subprocess
import sys
import os
from pathlib import Path

def test_ffmpeg_availability():
    """Test if FFmpeg is available and working"""
    print("=" * 50)
    print("FFMPEG DIAGNOSTIC TEST")
    print("=" * 50)
    
    # Test 1: Check if FFmpeg binary exists
    print("\n1. Testing FFmpeg binary availability...")
    try:
        result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ FFmpeg is available!")
            version_line = result.stdout.split('\n')[0]
            print(f"   Version: {version_line}")
        else:
            print("❌ FFmpeg binary exists but returned error:")
            print(f"   Return code: {result.returncode}")
            print(f"   STDERR: {result.stderr}")
            return False
    except FileNotFoundError:
        print("❌ FFmpeg binary not found in PATH")
        print("   This means FFmpeg is not installed or not in system PATH")
        return False
    except subprocess.TimeoutExpired:
        print("❌ FFmpeg command timed out")
        return False
    except Exception as e:
        print(f"❌ Error running FFmpeg: {e}")
        return False
    
    # Test 2: Check available codecs
    print("\n2. Testing available codecs...")
    try:
        result = subprocess.run(['ffmpeg', '-codecs'], capture_output=True, text=True, timeout=10)
        if 'libx264' in result.stdout:
            print("✅ H.264 encoder (libx264) is available")
        else:
            print("❌ H.264 encoder (libx264) is NOT available")
            
        if 'aac' in result.stdout:
            print("✅ AAC audio encoder is available")
        else:
            print("❌ AAC audio encoder is NOT available")
    except Exception as e:
        print(f"❌ Error checking codecs: {e}")
    
    # Test 3: Test basic functionality
    print("\n3. Testing basic FFmpeg functionality...")
    try:
        # Create a simple test
        test_cmd = ['ffmpeg', '-f', 'lavfi', '-i', 'testsrc=duration=1:size=320x240:rate=1', 
                   '-f', 'null', '-']
        result = subprocess.run(test_cmd, capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            print("✅ Basic FFmpeg video processing works")
        else:
            print("❌ Basic FFmpeg test failed:")
            print(f"   STDERR: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print("❌ FFmpeg test timed out")
        return False
    except Exception as e:
        print(f"❌ Error in basic test: {e}")
        return False
    
    # Test 4: Check system info
    print("\n4. System Information...")
    print(f"   Python version: {sys.version}")
    print(f"   Current working directory: {os.getcwd()}")
    print(f"   PATH: {os.environ.get('PATH', 'Not found')[:200]}...")
    
    # Test 5: Check if running on Render
    if os.environ.get('RENDER'):
        print("   Environment: Render.com deployment")
    else:
        print("   Environment: Local development")
    
    print("\n" + "=" * 50)
    print("FFMPEG DIAGNOSTIC COMPLETE")
    print("=" * 50)
    return True

if __name__ == "__main__":
    success = test_ffmpeg_availability()
    if success:
        print("\n🎉 FFmpeg appears to be working correctly!")
        exit(0)
    else:
        print("\n🚨 FFmpeg has issues that need to be resolved")
        exit(1)
