# SocialSphere - Social Media Platform

SocialSphere is a full-featured social media web application built with **Django** and **Django REST Framework**. It offers user authentication, profile customization, interactive feeds, image sharing, commenting, likes, social following, notifications, and REST APIs.

---

## 🚀 Features

### 👤 Authentication & Profiles
- **User Registration & Login**: Secure authentication with session management and password validation.
- **Custom User Profiles**: Edit display name, bio, website, location, and upload avatars/profile pictures.
- **Public Profile Pages**: View user profiles, bio information, and their published posts.

### 📸 Feed & Post Management
- **Media Posts**: Create posts with image uploads and text captions.
- **Dynamic Feed**: Browse recent posts from users in chronological order.
- **Interactive Likes**: Like and unlike posts with real-time like counts.
- **Comments**: Engage in discussions on individual posts.

### 🌐 Social Interactions & Discovery
- **Follow System**: Follow and unfollow users to stay connected.
- **Search**: Search for registered users by username or full name.
- **Notifications**: In-app notifications when users like your posts, leave comments, or follow you.

### 🔌 RESTful API
- Built with **Django REST Framework**.
- Endpoints for listing, creating, and retrieving posts:
  - `GET /api/posts/` - List all posts (paginated)
  - `POST /api/posts/` - Create a new post
  - `GET /api/posts/<id>/` - Retrieve post details

---

## 🛠️ Tech Stack

- **Backend**: Python, Django 5.x
- **API**: Django REST Framework (DRF)
- **Image Processing**: Pillow
- **Database**: SQLite (default, easily switchable to PostgreSQL/MySQL)
- **Frontend**: HTML5, CSS3, JavaScript, SVG Icons

---

## 📁 Project Structure

```text
social-media-platform/
├── accounts/               # User authentication, profiles, signals, views
├── config/                 # Project settings, URL routing, ASGI/WSGI
├── posts/                  # Post creation, likes, comments, REST API views & serializers
├── social/                 # Follow system, search, and notification models & views
├── static/                 # Static assets (CSS, JS, SVG icons)
│   ├── css/style.css
│   ├── js/main.js
│   └── images/
├── templates/              # Django HTML templates
│   ├── accounts/
│   ├── posts/
│   ├── social/
│   └── includes/
├── media/                  # User-uploaded profile pictures and post images
├── manage.py               # Django management utility
└── requirements.txt        # Python package dependencies
```

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.10+ installed
- Git installed

### 1. Clone the Repository
```bash
git clone https://github.com/gokul3844c/social-media.git
cd social-media
```

### 2. Set Up a Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create a Superuser (Admin)
```bash
python manage.py createsuperuser
```

### 6. Start the Development Server
```bash
python manage.py runserver
```

Open your browser and navigate to:
- **Application**: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)
- **Django Admin**: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
- **REST API**: [http://127.0.0.1:8000/api/posts/](http://127.0.0.1:8000/api/posts/)

---

## 🧪 Running Tests

```bash
python manage.py test
```

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
