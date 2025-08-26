from app import app, db, User, Video

def test_relationships():
    with app.app_context():
        # Get admin user
        admin = User.query.filter_by(username='admin').first()
        if admin:
            print(f'Admin user: {admin.username}, ID: {admin.id}')
            print(f'Admin videos: {len(admin.videos)}')
        
        # Get all videos
        videos = Video.query.all()
        print(f'\nTotal videos: {len(videos)}')
        
        for video in videos:
            user_name = video.user.username if video.user else "No user"
            print(f'Video {video.uuid}: User={user_name}, Status={video.status}')

if __name__ == "__main__":
    test_relationships()
