# User Management Features Documentation

## Overview
The BotAiVids application now includes comprehensive user management and filtering capabilities for both regular users and administrators.

## New Features Added

### 1. Admin User Management
- **User Management Panel**: Accessible via `/manage/users` for admin users
- **User Statistics**: Dashboard showing total users, admin users, regular users, and total videos
- **User Search & Filter**: Search by username or email, filter by user type (admin/regular)
- **User Actions**:
  - View detailed user information
  - Toggle admin privileges
  - Delete users (with cascade delete of their videos)
  - View user's videos

### Note: Flask-Admin Integration
The application includes both:
- **Flask-Admin Panel** at `/admin` - Built-in database administration interface
- **Custom User Management** at `/manage/users` - Enhanced user management with filtering and analytics

### 2. Enhanced Gallery with Filters
- **Search Functionality**: Search videos by description content
- **Status Filter**: Filter by video status (completed, processing, failed)
- **User Filter**: Admin users can filter videos by specific users
- **Video Management**: Admin users can delete videos directly from gallery

### 3. User Profile Integration
- **User-Video Relationships**: Videos are now properly linked to their creators
- **User Information Display**: Shows who created each video
- **Video Count Tracking**: Displays video count for each user

## Admin Access

### Default Admin User
- **Username**: admin
- **Password**: admin123
- **Email**: admin@botaivids.com

### Admin Features
- Access to user management panel
- Ability to delete any video
- User privilege management
- Comprehensive filtering and search

## Database Schema Updates

### User Model Enhancements
```python
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    videos = db.relationship('Video', backref='user', lazy=True)
```

### Video Model Relationships
- Videos are linked to users via `user_id` foreign key
- Cascade delete: when a user is deleted, their videos are also deleted
- Backref allows accessing user info from video objects

## API Endpoints

### User Management Routes
- `GET /manage/users` - User management dashboard
- `GET /manage/user/<id>` - User detail view
- `POST /manage/user/<id>/delete` - Delete user
- `POST /manage/user/<id>/toggle_admin` - Toggle admin privileges
- `POST /manage/video/<id>/delete` - Delete video
- `GET /api/users/search` - Search users API

### Flask-Admin Routes (Built-in)
- `GET /admin` - Flask-Admin dashboard
- Database models accessible through Flask-Admin interface

### Gallery Enhancement
- `GET /gallery?search=<query>` - Search videos
- `GET /gallery?status=<status>` - Filter by status
- `GET /gallery?user_id=<id>` - Filter by user (admin only)

## Security Features

### Access Control
- Admin-only routes protected with `@login_required` and admin check
- Users cannot delete their own admin account
- Cascade deletion prevents orphaned data
- CSRF protection on all forms

### Data Protection
- User passwords are properly hashed
- Admin privileges cannot be self-revoked
- Confirmation dialogs for destructive actions

## Usage Instructions

### For Admin Users
1. Login with admin credentials
2. Access "User Management" from navigation (or Flask-Admin from `/admin`)
3. Use search and filters to find specific users
4. Click "View" to see user details and videos
5. Use "Make Admin"/"Remove Admin" to manage privileges
6. Use "Delete" to remove users (with confirmation)

### For Regular Users
1. Create videos normally through the interface
2. View all videos in the enhanced gallery
3. Use search and filters to find specific content
4. Videos display creator information

## Deployment Notes

### Environment Variables
No additional environment variables required. The existing database configuration supports all new features.

### Database Migration
The application automatically creates new tables and relationships on startup. No manual migration required.

### Production Considerations
- Ensure admin credentials are changed from defaults
- Consider implementing rate limiting for admin actions
- Monitor database size if allowing user-generated content
- Implement proper backup strategy for user data

## Future Enhancements

### Potential Additions
- User profile pages with avatars
- Video sharing and collaboration features
- User activity logs and analytics
- Bulk user operations
- Export user/video data functionality
- Email notifications for admin actions

## Technical Implementation

### Key Components
- SQLAlchemy relationships for data integrity
- Flask-Login for authentication
- Bootstrap-based responsive UI
- AJAX search capabilities
- Form validation and CSRF protection

### File Structure
```
templates/
├── admin_users.html          # User management dashboard
├── admin_user_detail.html    # Individual user details
├── gallery.html              # Enhanced gallery with filters
└── base.html                 # Updated navigation

main.py                       # Enhanced with user management routes
app.py                        # Updated database models
```

This comprehensive user management system provides a solid foundation for scaling the application and managing user-generated content effectively.
