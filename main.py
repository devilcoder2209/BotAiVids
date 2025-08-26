import os
import uuid
import sys
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import or_

# Safety check for Python version and deprecated modules
print(f"[SYSTEM] Python version: {sys.version}")
print(f"[SYSTEM] Python version info: {sys.version_info}")

# Check for deprecated imghdr module
try:
    import imghdr
    print("[WARNING] imghdr module is still available but deprecated")
except ImportError:
    print("[INFO] imghdr module not available (expected in Python 3.13+)")

# Verify mimetypes is working
try:
    import mimetypes
    print("[INFO] mimetypes module loaded successfully")
except ImportError as e:
    print(f"[ERROR] mimetypes module failed to load: {e}")
    sys.exit(1)

# Try to import PIL for image optimization, fallback if not available
try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("[WARNING] PIL not available - image optimization disabled")

from app import app, db, login_manager, User, Video
from generate_process import text_to_speech, create_reel

UPLOAD_FOLDER = 'user_uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def optimize_image_size(image_path, max_size_mb=5, max_dimension=1280):
    """
    Optimize image size to prevent server memory issues.
    Reduces file size and dimensions while maintaining quality.
    Aggressive optimization for 256MB server limits.
    """
    if not PIL_AVAILABLE:
        print(f"[WARNING] PIL not available, skipping optimization for {image_path}")
        return image_path
        
    try:
        import psutil
        import gc
        
        # Monitor memory before processing
        process = psutil.Process()
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        print(f"[MEMORY] Before processing: {memory_before:.1f}MB")
        
        file_size_mb = os.path.getsize(image_path) / (1024 * 1024)
        print(f"[OPTIMIZE] Processing image: {image_path} ({file_size_mb:.2f}MB)")
        
        # Always optimize for server memory constraints
        with Image.open(image_path) as img:
            # Get original info
            original_size = img.size
            original_mode = img.mode
            print(f"[OPTIMIZE] Original: {original_size[0]}x{original_size[1]} {original_mode}")
            
            # Convert to RGB (reduces memory and file size)
            if img.mode in ('RGBA', 'P', 'LA'):
                background = Image.new('RGB', img.size, (255, 255, 255))
                if img.mode == 'P':
                    img = img.convert('RGBA')
                if 'transparency' in img.info:
                    # Handle transparency
                    background.paste(img, mask=img.split()[-1] if img.mode == 'RGBA' else None)
                else:
                    background.paste(img)
                img = background
                print(f"[OPTIMIZE] Converted {original_mode} to RGB")
            
            # Aggressive resizing for memory constraints
            width, height = img.size
            if max(width, height) > max_dimension:
                ratio = max_dimension / max(width, height)
                new_size = (int(width * ratio), int(height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
                print(f"[OPTIMIZE] Resized from {width}x{height} to {new_size[0]}x{new_size[1]}")
            
            # Save with aggressive compression
            quality = 70 if file_size_mb > 1 else 80
            img.save(image_path, 'JPEG', quality=quality, optimize=True, progressive=True)
            
            # Force garbage collection
            del img
            gc.collect()
            
        # Check memory after processing
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        new_size_mb = os.path.getsize(image_path) / (1024 * 1024)
        print(f"[MEMORY] After processing: {memory_after:.1f}MB (diff: {memory_after - memory_before:+.1f}MB)")
        print(f"[OPTIMIZE] Final size: {new_size_mb:.2f}MB (saved: {file_size_mb - new_size_mb:.2f}MB)")
        
        return image_path
        
    except ImportError:
        print("[WARNING] psutil not available, basic optimization only")
        # Fallback without memory monitoring
        return basic_optimize_image(image_path, max_size_mb, max_dimension)
    except Exception as e:
        print(f"[ERROR] Image optimization failed: {e}")
        return image_path

def basic_optimize_image(image_path, max_size_mb=5, max_dimension=1280):
    """Basic image optimization without memory monitoring"""
    try:
        with Image.open(image_path) as img:
            if img.mode in ('RGBA', 'P'):
                img = img.convert('RGB')
            
            width, height = img.size
            if max(width, height) > max_dimension:
                ratio = max_dimension / max(width, height)
                new_size = (int(width * ratio), int(height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            img.save(image_path, 'JPEG', quality=70, optimize=True)
        
        return image_path
    except Exception as e:
        print(f"[ERROR] Basic image optimization failed: {e}")
        return image_path



@app.route("/")
def home():
    return render_template("index.html")

@app.route("/debug-env")
def debug_env():
    """Debug route to check environment variables in production"""
    import os
    return {
        "elevenlabs_key_present": bool(os.environ.get('ELEVENLABS_API_KEY')),
        "elevenlabs_key_length": len(os.environ.get('ELEVENLABS_API_KEY', '')),
        "cloudinary_present": bool(os.environ.get('CLOUDINARY_CLOUD_NAME')),
        "database_url_present": bool(os.environ.get('DATABASE_URL')),
        "env_vars_count": len([k for k in os.environ.keys() if any(x in k.upper() for x in ['ELEVEN', 'CLOUDINARY', 'DATABASE', 'SECRET'])]),
        "python_version": os.sys.version,
        "platform": os.name
    }

@app.route("/debug-auth")
def debug_auth():
    from flask import session
    return {
        "authenticated": current_user.is_authenticated,
        "user": current_user.username if current_user.is_authenticated else None,
        "user_id": current_user.id if current_user.is_authenticated else None,
        "session_keys": list(session.keys())
    }

@app.route("/debug-users")
def debug_users():
    try:
        users = User.query.all()
        user_list = []
        for user in users:
            user_list.append({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "is_admin": user.is_admin,
                "created_at": user.created_at.isoformat() if user.created_at else None
            })
        return {
            "total_users": len(users),
            "users": user_list
        }
    except Exception as e:
        return {"error": str(e)}

@app.route("/debug-elevenlabs")
def debug_elevenlabs():
    """Test ElevenLabs API connectivity and authentication"""
    import requests
    
    api_key = os.environ.get('ELEVENLABS_API_KEY')
    
    if not api_key:
        return {
            "error": "No API key found",
            "api_key_present": False,
            "api_key_length": 0
        }
    
    # Test basic API connectivity
    try:
        headers = {
            "xi-api-key": api_key,
            "Accept": "application/json"
        }
        
        # Get user info from ElevenLabs (lightweight test)
        response = requests.get(
            "https://api.elevenlabs.io/v1/user", 
            headers=headers, 
            timeout=10
        )
        
        return {
            "api_key_present": True,
            "api_key_length": len(api_key),
            "api_status_code": response.status_code,
            "api_response_size": len(response.content),
            "api_accessible": response.status_code == 200,
            "response_headers": dict(response.headers),
            "error": None if response.status_code == 200 else response.text[:200]
        }
        
    except requests.exceptions.Timeout:
        return {
            "api_key_present": True,
            "api_key_length": len(api_key),
            "error": "API timeout - network connectivity issue",
            "api_accessible": False
        }
    except requests.exceptions.ConnectionError:
        return {
            "api_key_present": True,
            "api_key_length": len(api_key),
            "error": "Connection error - cannot reach ElevenLabs API",
            "api_accessible": False
        }
    except Exception as e:
        return {
            "api_key_present": True,
            "api_key_length": len(api_key),
            "error": f"Exception: {str(e)}",
            "api_accessible": False
        }

@app.route("/debug-tts")
def debug_tts():
    """Test the actual text-to-speech generation process"""
    import tempfile
    import shutil
    from text_to_audio import text_to_speech_file
    
    # Create a temporary test folder
    test_id = "debug-test-" + str(uuid.uuid4())[:8]
    test_folder = os.path.join("user_uploads", test_id)
    
    try:
        # Create test folder
        os.makedirs(test_folder, exist_ok=True)
        
        # Test text-to-speech generation
        test_text = "Hello, this is a debug test for audio generation."
        
        result = text_to_speech_file(test_text, test_id)
        
        response_data = {
            "test_id": test_id,
            "test_text": test_text,
            "result_path": result,
            "generation_successful": bool(result),
            "folder_exists": os.path.exists(test_folder)
        }
        
        # Check if audio file was created
        if result:
            audio_path = os.path.join(test_folder, "audio.mp3")
            response_data.update({
                "audio_file_exists": os.path.exists(audio_path),
                "audio_file_size": os.path.getsize(audio_path) if os.path.exists(audio_path) else 0,
                "audio_file_path": audio_path
            })
        
        # List files in test folder
        if os.path.exists(test_folder):
            response_data["folder_contents"] = os.listdir(test_folder)
        
        return response_data
        
    except Exception as e:
        return {
            "test_id": test_id,
            "error": str(e),
            "error_type": type(e).__name__,
            "generation_successful": False
        }
    finally:
        # Cleanup test folder
        try:
            if os.path.exists(test_folder):
                shutil.rmtree(test_folder)
        except:
            pass

@app.route("/debug-ffmpeg")
def debug_ffmpeg():
    """Test FFmpeg availability and basic functionality"""
    import subprocess
    
    try:
        # Test FFmpeg version
        version_result = subprocess.run(['ffmpeg', '-version'], capture_output=True, text=True, timeout=10)
        ffmpeg_available = version_result.returncode == 0
        
        response_data = {
            "ffmpeg_available": ffmpeg_available,
            "ffmpeg_version_output": version_result.stdout[:500] if ffmpeg_available else None,
            "ffmpeg_error": version_result.stderr[:200] if not ffmpeg_available else None
        }
        
        if ffmpeg_available:
            # Test basic audio generation capability
            test_output = "/tmp/test_audio.mp3" if os.name == "posix" else "test_audio.mp3"
            test_command = [
                'ffmpeg', '-y', '-f', 'lavfi', '-i', 'sine=frequency=440:duration=1',
                '-ar', '44100', '-ac', '1', '-b:a', '128k', test_output
            ]
            
            test_result = subprocess.run(test_command, capture_output=True, text=True, timeout=10)
            response_data.update({
                "audio_generation_test": test_result.returncode == 0,
                "test_command": ' '.join(test_command),
                "test_output": test_result.stdout[:200],
                "test_error": test_result.stderr[:200],
                "test_file_created": os.path.exists(test_output),
                "test_file_size": os.path.getsize(test_output) if os.path.exists(test_output) else 0
            })
            
            # Cleanup test file
            try:
                if os.path.exists(test_output):
                    os.remove(test_output)
            except:
                pass
        
        return response_data
        
    except subprocess.TimeoutExpired:
        return {"ffmpeg_available": False, "error": "FFmpeg command timed out"}
    except FileNotFoundError:
        return {"ffmpeg_available": False, "error": "FFmpeg not found in PATH"}
    except Exception as e:
        return {"ffmpeg_available": False, "error": str(e), "error_type": type(e).__name__}

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        if not username or not email or not password or not confirm:
            flash("All fields are required.", "danger")
            return redirect(url_for("signup"))
        if password != confirm:
            flash("Passwords do not match.", "danger")
            return redirect(url_for("signup"))
        if User.query.filter_by(username=username).first():
            flash("Username already exists.", "danger")
            return redirect(url_for("signup"))
        hashed_pw = generate_password_hash(password)
        user = User(username=username, password=hashed_pw, email=email)
        db.session.add(user)
        db.session.commit()
        flash("Signup successful. Please log in.", "success")
        return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    print(f"[DEBUG] Login route accessed with method: {request.method}")
    
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        print(f"[DEBUG] Login attempt: username={username}, password={'*' * len(password) if password else 'None'}")
        
        if not username or not password:
            print("[DEBUG] Missing username or password")
            flash("Please provide both username and password.", "danger")
            return render_template("login.html")
        
        try:
            user = User.query.filter_by(username=username).first()
            if user:
                print(f"[DEBUG] User found: {user.username}, admin: {user.is_admin}")
                print(f"[DEBUG] Password hash check: {check_password_hash(user.password, password)}")
                if check_password_hash(user.password, password):
                    login_user(user, remember=True)
                    print(f"[DEBUG] Login successful for {username}")
                    print(f"[DEBUG] Current user authenticated: {current_user.is_authenticated}")
                    flash("Logged in successfully!", "success")
                    return redirect(url_for("home"))
                else:
                    print(f"[DEBUG] Password mismatch for {username}")
                    flash("Invalid username or password.", "danger")
            else:
                print(f"[DEBUG] User not found: {username}")
                flash("Invalid username or password.", "danger")
        except Exception as e:
            print(f"[DEBUG] Database error during login: {e}")
            flash("Login failed due to database error.", "danger")
    
    return render_template("login.html")

@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("Logged out.", "info")
    return redirect(url_for("home"))

@app.route("/create", methods=["GET", "POST"])
@login_required
def create():
    print(f"[DEBUG] Create route accessed by user: {current_user.username if current_user.is_authenticated else 'Anonymous'}")
    myid = uuid.uuid1()
    if request.method == "POST":
        try:
            rec_id = request.form.get("uuid")
            desc = request.form.get("text")
            duration = int(request.form.get("duration", 3))  # Default to 3 seconds
            
            print(f"[DEBUG] User selected duration: {duration} seconds per image")
            
            if not rec_id or not desc:
                flash("Missing required fields.", "error")
                return redirect(url_for("create"))
            
            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], rec_id)
            if not os.path.exists(upload_path):
                os.makedirs(upload_path)
            
            input_files = []
            files = request.files.getlist("files")
            if not files or not any(f.filename for f in files):
                flash("Please upload at least one image.", "error")
                return redirect(url_for("create"))
                
            for file in files:
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    file_path = os.path.join(upload_path, filename)
                    
                    # Save and immediately check file size
                    file.save(file_path)
                    file_size_mb = os.path.getsize(file_path) / (1024 * 1024)
                    
                    # Reject files that are too large even before processing
                    if file_size_mb > 50:  # 50MB limit per file
                        os.remove(file_path)
                        flash(f"File {filename} is too large ({file_size_mb:.1f}MB). Maximum size is 50MB.", "error")
                        return redirect(url_for("create"))
                    
                    print(f"[UPLOAD] File {filename}: {file_size_mb:.2f}MB")
                    
                    # Check memory before processing each image
                    try:
                        import psutil
                        process = psutil.Process()
                        memory_mb = process.memory_info().rss / 1024 / 1024
                        print(f"[MEMORY] Before image {filename}: {memory_mb:.1f}MB")
                        
                        # If memory is getting high, force garbage collection
                        if memory_mb > 200:  # 200MB threshold
                            import gc
                            gc.collect()
                            print(f"[MEMORY] Forced garbage collection")
                            
                    except ImportError:
                        pass
                    
                    # Optimize image size to prevent server memory issues
                    optimized_path = optimize_image_size(file_path)
                    if optimized_path != file_path:
                        filename = os.path.basename(optimized_path)
                    
                    input_files.append(filename)
                
            # Save description
            with open(os.path.join(upload_path, "description.txt"), "w", encoding='utf-8') as desc_file:
                desc_file.write(desc)
            
            # Create video entry in database
            video = Video(
                uuid=rec_id,
                user_id=current_user.id,
                description=desc,
                status='processing'
            )
            db.session.add(video)
            db.session.commit()
            
            # Write input.txt with user-selected duration
            with open(os.path.join(upload_path, "input.txt"), "w") as fl:
                for f in input_files:
                    fl.write(f"file '{f}'\nduration {duration}\n")
            
            # Call processing functions
            try:
                print(f"[DEBUG] Starting processing for {rec_id}")
                
                # Check memory before processing
                try:
                    import psutil
                    process = psutil.Process()
                    memory_mb = process.memory_info().rss / 1024 / 1024
                    print(f"[MEMORY] Before processing: {memory_mb:.1f}MB")
                    
                    # If memory usage is already high, force cleanup
                    if memory_mb > 180:  # Leave 70MB headroom
                        import gc
                        gc.collect()
                        print(f"[MEMORY] High memory usage detected, forcing cleanup")
                        
                except ImportError:
                    print("[WARNING] psutil not available for memory monitoring")
                
                audio_success = text_to_speech(rec_id)
                if not audio_success:
                    print(f"[WARNING] Audio generation failed for {rec_id}, but continuing with video creation")
                
                video_url = create_reel(rec_id)
                
                # Update video with completion status
                if video_url:
                    video.status = 'completed'
                    video.cloudinary_url = video_url
                    db.session.commit()
                    flash("Reel created successfully! View it in the gallery.", "success")
                else:
                    video.status = 'failed'
                    db.session.commit()
                    flash("Error creating video. Please try again.", "error")
                    
            except Exception as e:
                video.status = 'failed'
                db.session.commit()
                print(f"[ERROR] Processing failed for {rec_id}: {e}")
                flash(f"Error creating reel: {str(e)}", "error")
                
        except Exception as e:
            print(f"[ERROR] Upload failed: {e}")
            flash(f"Upload failed: {str(e)}", "error")
            
    return render_template("create.html", myid=myid)

@app.route("/gallery")
def gallery():
    # Get filter parameters
    status_filter = request.args.get('status', 'all')
    search_query = request.args.get('search', '')
    user_filter = request.args.get('user_id', '')
    
    # Build query
    query = Video.query
    
    # Apply status filter
    if status_filter != 'all':
        query = query.filter_by(status=status_filter)
    
    # Apply search filter (search in description)
    if search_query:
        query = query.filter(Video.description.contains(search_query))
    
    # Apply user filter
    if user_filter and user_filter.isdigit():
        query = query.filter_by(user_id=int(user_filter))
    
    # Get videos with user information
    videos = query.order_by(Video.created_at.desc()).all()
    
    # Get all users for filter dropdown
    users = User.query.all()
    
    return render_template("gallery.html", videos=videos, users=users, 
                         status_filter=status_filter, search_query=search_query, 
                         user_filter=user_filter)

# User Management Routes
@app.route("/admin/dashboard")
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        flash("Admin access required.", "danger")
        return redirect(url_for("home"))
    
    # Get comprehensive statistics
    total_users = User.query.count()
    admin_users = User.query.filter_by(is_admin=True).count()
    regular_users = total_users - admin_users
    
    total_videos = Video.query.count()
    completed_videos = Video.query.filter_by(status='completed').count()
    processing_videos = Video.query.filter_by(status='processing').count()
    failed_videos = Video.query.filter_by(status='failed').count()
    
    # Recent activities
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    recent_videos = Video.query.order_by(Video.created_at.desc()).limit(10).all()
    
    # User with most videos
    from sqlalchemy import func
    top_users = db.session.query(
        User, func.count(Video.id).label('video_count')
    ).outerjoin(Video).group_by(User.id).order_by(func.count(Video.id).desc()).limit(5).all()
    
    # Monthly statistics (last 6 months)
    from datetime import datetime, timedelta
    import calendar
    
    monthly_stats = []
    for i in range(6):
        month_start = datetime.now().replace(day=1) - timedelta(days=30*i)
        month_end = month_start + timedelta(days=32)
        month_end = month_end.replace(day=1) - timedelta(days=1)
        
        month_users = User.query.filter(
            User.created_at >= month_start,
            User.created_at <= month_end
        ).count()
        
        month_videos = Video.query.filter(
            Video.created_at >= month_start,
            Video.created_at <= month_end
        ).count()
        
        monthly_stats.append({
            'month': calendar.month_name[month_start.month],
            'year': month_start.year,
            'users': month_users,
            'videos': month_videos
        })
    
    monthly_stats.reverse()
    
    return render_template("admin_dashboard.html",
                         total_users=total_users,
                         admin_users=admin_users,
                         regular_users=regular_users,
                         total_videos=total_videos,
                         completed_videos=completed_videos,
                         processing_videos=processing_videos,
                         failed_videos=failed_videos,
                         recent_users=recent_users,
                         recent_videos=recent_videos,
                         top_users=top_users,
                         monthly_stats=monthly_stats)

@app.route("/manage/users")
@login_required
def manage_users():
    if not current_user.is_admin:
        flash("Admin access required.", "danger")
        return redirect(url_for("home"))
    
    # Get filter parameters
    search_query = request.args.get('search', '')
    status_filter = request.args.get('status', 'all')
    
    # Build query
    query = User.query
    
    # Apply search filter
    if search_query:
        query = query.filter(or_(
            User.username.contains(search_query),
            User.email.contains(search_query)
        ))
    
    # Apply status filter
    if status_filter == 'admin':
        query = query.filter_by(is_admin=True)
    elif status_filter == 'regular':
        query = query.filter_by(is_admin=False)
    
    users = query.order_by(User.created_at.desc()).all()
    
    # Add video count for each user
    for user in users:
        user.video_count = Video.query.filter_by(user_id=user.id).count()
    
    return render_template("admin_users.html", users=users, 
                         search_query=search_query, status_filter=status_filter)

@app.route("/manage/user/<int:user_id>")
@login_required
def manage_user_detail(user_id):
    if not current_user.is_admin:
        flash("Admin access required.", "danger")
        return redirect(url_for("home"))
    
    user = User.query.get_or_404(user_id)
    videos = Video.query.filter_by(user_id=user_id).order_by(Video.created_at.desc()).all()
    
    return render_template("admin_user_detail.html", user=user, videos=videos)

@app.route("/manage/user/<int:user_id>/delete", methods=["POST"])
@login_required
def manage_delete_user(user_id):
    if not current_user.is_admin:
        flash("Admin access required.", "danger")
        return redirect(url_for("home"))
    
    user = User.query.get_or_404(user_id)
    
    # Prevent deleting the current admin user
    if user.id == current_user.id:
        flash("Cannot delete your own account.", "error")
        return redirect(url_for("manage_users"))
    
    # Delete user's videos first (cascade delete)
    Video.query.filter_by(user_id=user_id).delete()
    
    # Delete user
    db.session.delete(user)
    db.session.commit()
    
    flash(f"User '{user.username}' and all their videos have been deleted.", "success")
    return redirect(url_for("manage_users"))

@app.route("/manage/user/<int:user_id>/toggle_admin", methods=["POST"])
@login_required
def manage_toggle_user_admin(user_id):
    if not current_user.is_admin:
        flash("Admin access required.", "danger")
        return redirect(url_for("home"))
    
    user = User.query.get_or_404(user_id)
    
    # Prevent removing admin from current user
    if user.id == current_user.id and user.is_admin:
        flash("Cannot remove admin privileges from your own account.", "error")
        return redirect(url_for("manage_users"))
    
    user.is_admin = not user.is_admin
    db.session.commit()
    
    status = "granted" if user.is_admin else "revoked"
    flash(f"Admin privileges {status} for user '{user.username}'.", "success")
    return redirect(url_for("manage_users"))

@app.route("/manage/video/<int:video_id>/delete", methods=["POST"])
@login_required
def manage_delete_video(video_id):
    if not current_user.is_admin:
        flash("Admin access required.", "danger")
        return redirect(url_for("home"))
    
    video = Video.query.get_or_404(video_id)
    
    # Delete video file if it exists locally
    local_path = f"static/reels/{video.uuid}.mp4"
    if os.path.exists(local_path):
        os.remove(local_path)
    
    # Delete video folder if it exists
    video_folder = f"user_uploads/{video.uuid}"
    if os.path.exists(video_folder):
        import shutil
        shutil.rmtree(video_folder)
    
    # Delete from database
    db.session.delete(video)
    db.session.commit()
    
    flash("Video deleted successfully.", "success")
    return redirect(request.referrer or url_for("gallery"))

@app.route("/api/users/search")
@login_required
def api_search_users():
    if not current_user.is_admin:
        return jsonify({"error": "Admin access required"}), 403
    
    query = request.args.get('q', '')
    if len(query) < 2:
        return jsonify([])
    
    users = User.query.filter(or_(
        User.username.contains(query),
        User.email.contains(query)
    )).limit(10).all()
    
    return jsonify([{
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'is_admin': user.is_admin
    } for user in users])


