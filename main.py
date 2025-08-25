import os
import uuid
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from sqlalchemy import or_

from app import app, db, login_manager, User, Video
from generate_process import text_to_speech, create_reel

UPLOAD_FOLDER = 'user_uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER



@app.route("/")
def home():
    return render_template("index.html")

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
                    file.save(os.path.join(upload_path, filename))
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
            
            # Write input.txt
            with open(os.path.join(upload_path, "input.txt"), "w") as fl:
                for f in input_files:
                    fl.write(f"file '{f}'\nduration 3\n")
            
            # Call processing functions
            try:
                print(f"[DEBUG] Starting processing for {rec_id}")
                text_to_speech(rec_id)
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


