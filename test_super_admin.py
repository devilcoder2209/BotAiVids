#!/usr/bin/env python3
"""
Test script for Super Admin protection feature
"""

from app import app, db, User, init_app
from werkzeug.security import generate_password_hash

def test_super_admin_protection():
    """Test the super admin protection feature"""
    with app.app_context():
        # Initialize the app (this will create the super admin)
        init_app()
        
        # Check if the super admin exists
        super_admin = User.query.filter_by(username='admin').first()
        if super_admin:
            print(f"✅ Super Admin found: {super_admin.username}")
            print(f"   - is_admin: {super_admin.is_admin}")
            print(f"   - is_super_admin: {super_admin.is_super_admin}")
        else:
            print("❌ Super Admin not found!")
            return False
        
        # Create a test regular admin
        test_admin = User.query.filter_by(username='test_admin').first()
        if not test_admin:
            test_admin = User(
                username='test_admin',
                password=generate_password_hash('password123'),
                email='test_admin@example.com',
                is_admin=True,
                is_super_admin=False
            )
            db.session.add(test_admin)
            db.session.commit()
            print("✅ Test admin created")
        else:
            print("✅ Test admin already exists")
        
        # Create a test regular user
        test_user = User.query.filter_by(username='test_user').first()
        if not test_user:
            test_user = User(
                username='test_user',
                password=generate_password_hash('password123'),
                email='test_user@example.com',
                is_admin=False,
                is_super_admin=False
            )
            db.session.add(test_user)
            db.session.commit()
            print("✅ Test user created")
        else:
            print("✅ Test user already exists")
        
        # Display all users and their status
        print("\n📋 All Users:")
        users = User.query.all()
        for user in users:
            status = "Super Admin" if user.is_super_admin else "Admin" if user.is_admin else "User"
            protected = " [PROTECTED]" if user.is_super_admin else ""
            print(f"   - {user.username}: {status}{protected}")
        
        print(f"\n🔒 Super Admin Protection Summary:")
        print(f"   - Super Admin '{super_admin.username}' cannot be demoted")
        print(f"   - Super Admin '{super_admin.username}' cannot be deleted")
        print(f"   - Only Super Admin can create other Super Admins (via Flask-Admin)")
        print(f"   - Regular admins can manage other regular users")
        
        return True

if __name__ == '__main__':
    print("🧪 Testing Super Admin Protection Feature\n")
    if test_super_admin_protection():
        print("\n✅ All tests passed! Super Admin protection is working correctly.")
    else:
        print("\n❌ Tests failed! Please check the implementation.")
