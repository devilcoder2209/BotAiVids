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
    def is_accessible(self):
        from flask_login import current_user
        return current_user.is_authenticated and current_user.username == 'admin'
    def inaccessible_callback(self, name, **kwargs):
        from flask import redirect, url_for, flash
        flash('Admin access required.', 'danger')
        return redirect(url_for('login'))

admin = Admin(app, name='Admin Portal', template_mode='bootstrap4')
admin.add_view(SecureModelView(User, db.session))
admin.add_view(SecureModelView(Video, db.session))

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
                    is_admin=True
                )
                db.session.add(admin_user)
                db.session.commit()
                print("[INFO] Admin user created (username: admin, password: admin123)")
            
            print("[INFO] Database initialization successful")
            return True
        except Exception as e:
            print(f"[ERROR] Database initialization failed: {e}")
            return False

if __name__ == '__main__':
    if init_app():
        print("[INFO] Starting Flask application on http://127.0.0.1:5000")
        app.run(host='0.0.0.0', port=5000, debug=True, use_reloader=False)
    else:
        print("[ERROR] Failed to initialize application")
