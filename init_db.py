"""
Database initialization script for Render deployment
Run this once to create tables and admin user
"""
from app import app, db, User
from werkzeug.security import generate_password_hash

def init_database():
    """Initialize database with tables and admin user"""
    with app.app_context():
        try:
            print("[INFO] Starting database initialization...")
            
            # Create all tables
            db.create_all()
            print("[INFO] Database tables created successfully")
            
            # Check if admin user already exists
            admin_user = User.query.filter_by(username='admin').first()
            
            if not admin_user:
                # Create super admin user
                hashed_password = generate_password_hash('admin123')
                admin_user = User(
                    username='admin',
                    password=hashed_password,
                    email='admin@botaivids.com',
                    is_admin=True,
                    is_super_admin=True
                )
                db.session.add(admin_user)
                db.session.commit()
                print("[INFO] ✅ Super Admin user created successfully")
                print("[INFO]    Username: admin")
                print("[INFO]    Password: admin123")
                print("[INFO]    ⚠️  CHANGE THIS PASSWORD IMMEDIATELY!")
            else:
                print("[INFO] Admin user already exists")
                # Ensure existing admin is marked as super admin
                if not admin_user.is_super_admin:
                    admin_user.is_super_admin = True
                    db.session.commit()
                    print("[INFO] Existing admin marked as super admin")
            
            # Print database stats
            user_count = User.query.count()
            print(f"[INFO] Database initialized successfully!")
            print(f"[INFO] Total users in database: {user_count}")
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Database initialization failed: {e}")
            import traceback
            traceback.print_exc()
            return False

if __name__ == '__main__':
    success = init_database()
    if success:
        print("\n[SUCCESS] Database is ready to use!")
    else:
        print("\n[FAILED] Database initialization failed. Check errors above.")
        exit(1)
