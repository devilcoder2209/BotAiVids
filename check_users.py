from app import app, db, User
from werkzeug.security import check_password_hash

with app.app_context():
    users = User.query.all()
    print(f"Total users in database: {len(users)}")
    
    for user in users:
        print(f"User: {user.username}, Email: {user.email}, Admin: {user.is_admin}")
        
        # Test password verification for admin user
        if user.username == 'admin':
            test_password = 'admin123'
            password_check = check_password_hash(user.password, test_password)
            print(f"Password check for admin with 'admin123': {password_check}")
            print(f"Stored password hash: {user.password[:50]}...")
