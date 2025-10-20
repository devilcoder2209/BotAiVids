import os
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Flask app and config
load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'devsecretkey')

# Use PostgreSQL database
database_url = os.environ.get('DATABASE_URL')
if database_url and database_url.startswith('postgres://'):
    database_url = database_url.replace('postgres://', 'postgresql://', 1)

app.config['SQLALCHEMY_DATABASE_URI'] = database_url or 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

# Session configuration for Flask-Login
app.config['REMEMBER_COOKIE_DURATION'] = 60 * 60 * 24 * 7  # 7 days
app.config['SESSION_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'  # HTTPS in production
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_NAME'] = 'botaivids_session'
app.config['REMEMBER_COOKIE_NAME'] = 'botaivids_remember'
app.config['REMEMBER_COOKIE_SECURE'] = os.environ.get('FLASK_ENV') == 'production'  # HTTPS in production
app.config['REMEMBER_COOKIE_HTTPONLY'] = True


# User model and user loader here to avoid circular import
from flask_login import UserMixin
from datetime import datetime

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.now)  # Use local time instead of UTC
    is_admin = db.Column(db.Boolean, default=False)
    is_super_admin = db.Column(db.Boolean, default=False)  # New field for super admin protection
    
    # Relationship with videos
    videos = db.relationship('Video', backref='user', lazy=True)

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    cloudinary_public_id = db.Column(db.String(255), nullable=True)
    cloudinary_url = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default='processing')
    created_at = db.Column(db.DateTime, default=datetime.now)  # Use local time
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)  # Use local time
    duration = db.Column(db.Float, nullable=True)
    size = db.Column(db.Integer, nullable=True)
    format = db.Column(db.String(10), nullable=True)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Import routes after model definition to avoid circular import

# --- Flask-Admin setup ---
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

class SecureModelView(ModelView):
    # Enhanced security and styling
    def is_accessible(self):
        from flask_login import current_user
        return current_user.is_authenticated and current_user.is_admin
    
    def inaccessible_callback(self, name, **kwargs):
        from flask import redirect, url_for, flash
        flash('Admin access required.', 'danger')
        return redirect(url_for('login'))
    
    # Better column formatting
    can_view_details = True
    can_export = True
    can_set_page_size = True
    page_size = 25
    
    # Enable search
    column_searchable_list = ['id']
    column_filters = ['created_at']
    
    # Better form display
    form_widget_args = {
        'description': {
            'rows': 4,
            'style': 'min-height: 120px;'
        }
    }

class UserModelView(SecureModelView):
    # User-specific configurations
    column_list = ['id', 'username', 'email', 'is_admin', 'is_super_admin', 'created_at']
    column_searchable_list = ['username', 'email']
    column_filters = ['is_admin', 'is_super_admin', 'created_at']
    column_labels = {
        'is_admin': 'Admin Status',
        'is_super_admin': 'Super Admin',
        'created_at': 'Registered'
    }
    
    # Form configurations
    form_columns = ['username', 'email', 'is_admin', 'is_super_admin']
    form_widget_args = {
        'password': {
            'placeholder': 'Leave blank to keep current password'
        }
    }

class VideoModelView(SecureModelView):
    # Video-specific configurations
    column_list = ['id', 'uuid', 'user_id', 'description', 'status', 'created_at', 'updated_at']
    column_searchable_list = ['uuid', 'description']
    column_filters = ['status', 'created_at', 'user_id']
    column_labels = {
        'uuid': 'Video ID',
        'user_id': 'User ID',
        'cloudinary_url': 'Video URL',
        'created_at': 'Created',
        'updated_at': 'Updated'
    }
    
    # Format columns
    column_formatters = {
        'description': lambda v, c, m, p: m.description[:50] + '...' if m.description and len(m.description) > 50 else m.description,
        'status': lambda v, c, m, p: f'<span class="badge badge-{"success" if m.status == "completed" else "warning" if m.status == "processing" else "danger"}">{m.status.title()}</span>'
    }
    
    # Form configurations - removed 'user' field since it doesn't exist
    form_columns = ['user_id', 'description', 'status', 'cloudinary_url']

# Initialize admin with custom base template
admin = Admin(
    app, 
    name='BotAiVids Admin', 
    template_mode='bootstrap5',  # Changed to Bootstrap 5
    base_template='admin/master.html',  # Use our custom master template
    index_view=None
)

admin.add_view(UserModelView(User, db.session, name='Users', category='Management'))
admin.add_view(VideoModelView(Video, db.session, name='Videos', category='Management'))

from main import *

# Add request logging
@app.before_request
def log_request_info():
    print(f"[REQUEST] {request.method} {request.url} from {request.remote_addr}")

def init_app():
    """Initialize database and create admin user"""
    with app.app_context():
        try:
            db.create_all()
            
            # Create admin user if doesn't exist
            admin_user = User.query.filter_by(username='admin').first()
            if not admin_user:
                from werkzeug.security import generate_password_hash
                hashed_password = generate_password_hash('admin123')
                admin_user = User(
                    username='admin',
                    password=hashed_password,
                    email='admin@botaivids.com',
                    is_admin=True,
                    is_super_admin=True  # Mark original admin as super admin
                )
                db.session.add(admin_user)
                db.session.commit()
                print("[INFO] Super Admin user created (username: admin, password: admin123)")
            else:
                # If admin exists but isn't marked as super admin, mark them
                if not admin_user.is_super_admin:
                    admin_user.is_super_admin = True
                    db.session.commit()
                    print("[INFO] Existing admin user marked as super admin")
            
            print("[INFO] Database initialization successful")
            return True
        except Exception as e:
            print(f"[ERROR] Database initialization failed: {e}")
            return False

# Initialize database on startup (works with both Flask dev server and Gunicorn)
try:
    init_app()
except Exception as e:
    print(f"[WARNING] Database initialization had an issue: {e}")
    print("[INFO] App will continue running, database might need manual setup")

if __name__ == '__main__':
    print("[INFO] Starting Flask application on http://127.0.0.1:5000")
    app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
