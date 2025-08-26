# 🎬 BotAiVids - Dynamic Short Video Generator

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0.0-green.svg)](https://flask.palletsprojects.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A professional-grade Flask web application that transforms images and text into engaging short videos with AI-powered narration. Perfect for content creators, marketers, and educators looking to automate video production.

## ✨ Features

### 🎯 Core Functionality
- **Multi-Image Upload**: Support for PNG, JPG, and JPEG formats
- **AI Text-to-Speech**: Professional narration using ElevenLabs API
- **Automatic Video Generation**: FFmpeg-powered video compilation
- **Real-time Processing**: Live progress tracking and notifications
- **Gallery Management**: Browse and manage created videos

### 🔐 User Management
- **Secure Authentication**: Flask-Login with password hashing
- **User Registration**: Account creation with email validation
- **Admin Panel**: User management with mobile-responsive interface
- **Session Management**: Secure cookie handling and session timeout

### 📱 Modern UI/UX
- **Glassmorphism Design**: Modern, translucent interface elements
- **Mobile Responsive**: Optimized for all screen sizes
- **Dark Theme**: Professional dark mode interface
- **Interactive Elements**: Smooth animations and transitions

### ☁️ Cloud Integration
- **Cloudinary Storage**: Scalable video hosting and delivery
- **PostgreSQL Database**: Robust data persistence
- **Production Ready**: Configured for Render hosting

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- FFmpeg installed on your system
- ElevenLabs API key
- PostgreSQL database (for production)

### Development Setup

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd BotAiVids_Fresh
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration**
   Create a `.env` file with the following variables:
   ```env
   # Required API Keys
   ELEVENLABS_API_KEY=your_elevenlabs_api_key_here
   CLOUDINARY_CLOUD_NAME=your_cloudinary_cloud_name
   CLOUDINARY_API_KEY=your_cloudinary_api_key
   CLOUDINARY_API_SECRET=your_cloudinary_api_secret
   
   # Flask Configuration
   FLASK_SECRET_KEY=your_super_secret_key_here
   FLASK_ENV=development
   
   # Database (Development - SQLite)
   DATABASE_URL=sqlite:///app.db
   
   # Database (Production - PostgreSQL)
   # DATABASE_URL=postgresql://username:password@host:port/database
   ```

5. **Initialize Database**
   ```bash
   python init_db.py
   ```

6. **Run Development Server**
   ```bash
   python main.py
   ```

   Visit `http://localhost:5000` to access the application.

## 🌐 Production Deployment (Render)

### Render Hosting Setup

1. **Fork/Clone Repository**
   - Ensure your code is in a Git repository
   - Push to GitHub, GitLab, or Bitbucket

2. **Create Render Account**
   - Sign up at [render.com](https://render.com)
   - Connect your Git provider

3. **Database Setup**
   - Create a PostgreSQL database service on Render
   - Note the connection details for environment variables

4. **Web Service Configuration**
   - Create a new Web Service
   - Connect your repository
   - Use the following settings:
     - **Runtime**: Python 3
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:app`

5. **Environment Variables**
   Set the following in Render dashboard:
   ```env
   ELEVENLABS_API_KEY=your_elevenlabs_api_key
   CLOUDINARY_CLOUD_NAME=your_cloudinary_cloud_name
   CLOUDINARY_API_KEY=your_cloudinary_api_key
   CLOUDINARY_API_SECRET=your_cloudinary_api_secret
   FLASK_SECRET_KEY=your_production_secret_key
   DATABASE_URL=your_render_postgresql_url
   FLASK_ENV=production
   ```

6. **Deploy**
   - Render will automatically build and deploy your application
   - The build process includes FFmpeg installation via `render.yaml`

### Manual Deployment Steps

1. **Prepare Environment Variables**
   ```bash
   # Set all required environment variables in your hosting platform
   ```

2. **Database Migration**
   ```bash
   python init_db.py
   ```

3. **Start Production Server**
   ```bash
   gunicorn app:app --bind 0.0.0.0:$PORT
   ```

## 🏗️ Project Structure

```
BotAiVids_Fresh/
├── 📁 static/                 # Static assets
│   ├── 📁 css/               # Stylesheets
│   │   ├── style.css         # Main application styles
│   │   ├── create.css        # Video creation interface
│   │   └── gallery.css       # Gallery view styles
│   ├── 📁 js/                # JavaScript files
│   │   └── effects.js        # UI effects and interactions
│   ├── 📁 reels/             # Generated video files
│   └── 📁 songs/             # Background music library
├── 📁 templates/             # Jinja2 templates
│   ├── base.html             # Base template with navigation
│   ├── index.html            # Homepage
│   ├── create.html           # Video creation interface
│   ├── gallery.html          # Video gallery
│   ├── login.html            # User login
│   └── signup.html           # User registration
├── 📁 user_uploads/          # User-uploaded content storage
├── 📄 app.py                 # Flask application factory
├── 📄 main.py                # Application entry point
├── 📄 generate_process.py    # Video generation logic
├── 📄 text_to_audio.py       # ElevenLabs TTS integration
├── 📄 storage.py             # Cloudinary storage management
├── 📄 init_db.py             # Database initialization
├── 📄 requirements.txt       # Python dependencies
├── 📄 render.yaml            # Render deployment config
├── 📄 Procfile               # Process configuration
└── 📄 README.md              # This file
```

## 🛠️ Technologies Used

### Backend Framework
- **Flask 3.0.0** - Modern Python web framework
- **SQLAlchemy** - SQL toolkit and ORM
- **Flask-Login** - User session management
- **Werkzeug** - WSGI utility library

### Media Processing
- **FFmpeg** - Video processing and compilation
- **Pillow** - Image manipulation and optimization
- **ElevenLabs API** - High-quality text-to-speech

### Cloud Services
- **Cloudinary** - Video hosting and CDN delivery
- **PostgreSQL** - Production database
- **Render** - Hosting and deployment platform

### Frontend Technologies
- **HTML5 & CSS3** - Modern web standards
- **JavaScript ES6+** - Interactive functionality
- **Glassmorphism UI** - Contemporary design patterns
- **Responsive Design** - Mobile-first approach

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| `ELEVENLABS_API_KEY` | ElevenLabs TTS API key | Yes | - |
| `CLOUDINARY_CLOUD_NAME` | Cloudinary cloud name | Yes | - |
| `CLOUDINARY_API_KEY` | Cloudinary API key | Yes | - |
| `CLOUDINARY_API_SECRET` | Cloudinary API secret | Yes | - |
| `FLASK_SECRET_KEY` | Flask session encryption key | Yes | - |
| `DATABASE_URL` | Database connection string | No | `sqlite:///app.db` |
| `FLASK_ENV` | Flask environment mode | No | `development` |

### Database Schema

#### Users Table
- `id`: Primary key (Integer)
- `username`: Unique username (String, 80 chars)
- `email`: User email (String, 120 chars)
- `password_hash`: Hashed password (String, 120 chars)
- `created_at`: Account creation timestamp (DateTime)

#### Videos Table
- `id`: Primary key (Integer)
- `user_id`: Foreign key to Users (Integer)
- `title`: Video title (String, 200 chars)
- `description`: Video description (Text)
- `video_url`: Cloudinary video URL (String, 500 chars)
- `created_at`: Video creation timestamp (DateTime)

## 🔒 Security Features

- **Password Hashing**: Werkzeug-based secure password storage
- **Session Management**: Secure cookie configuration
- **File Upload Validation**: Restricted file types and size limits
- **CSRF Protection**: Built-in Flask security measures
- **Environment-based Configuration**: Separate dev/production settings

## 📱 Mobile Responsiveness

- **Adaptive Layout**: Optimized for all screen sizes
- **Touch-friendly Interface**: Large buttons and gesture support
- **Mobile Navigation**: Collapsible menu and easy access
- **Performance Optimized**: Fast loading on mobile networks

## 🎨 UI Components

### Glassmorphism Design
- Translucent backgrounds with backdrop blur
- Subtle borders and shadows
- Modern color gradients
- Smooth animations and transitions

### Interactive Elements
- Hover effects and state changes
- Loading animations during processing
- Progress indicators for video generation
- Toast notifications for user feedback

## 🚨 Troubleshooting

### Common Issues

1. **FFmpeg Not Found**
   ```bash
   # Install FFmpeg
   # Windows: Download from https://ffmpeg.org/
   # macOS: brew install ffmpeg
   # Ubuntu: sudo apt install ffmpeg
   ```

2. **Database Connection Error**
   ```bash
   # Check DATABASE_URL format
   # PostgreSQL: postgresql://username:password@host:port/database
   # SQLite: sqlite:///path/to/database.db
   ```

3. **ElevenLabs API Issues**
   - Verify API key in environment variables
   - Check API quota and usage limits
   - Ensure network connectivity

4. **Cloudinary Upload Failures**
   - Verify all Cloudinary credentials
   - Check file size limits
   - Ensure stable internet connection

### Debug Mode

Enable debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙋‍♂️ Support

For support, email or create an issue in the repository.

## 🚀 Future Enhancements

- [ ] Multiple voice options and languages
- [ ] Custom background music upload
- [ ] Video templates and themes
- [ ] Batch processing capabilities
- [ ] API endpoints for integration
- [ ] Advanced video editing features
- [ ] Social media integration
- [ ] Analytics and usage metrics

---

**Made with ❤️ using Flask and modern web technologies**
