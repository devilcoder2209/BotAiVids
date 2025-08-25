import os
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Flask app and config
load_dotenv()
app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'devsecretkey')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# User model and user loader here to avoid circular import
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)

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

from main import *

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
