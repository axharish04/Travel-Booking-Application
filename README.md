# Travel Lykkr - Indian Travel Booking Platform

A modern, responsive travel booking platform built with Django, featuring a beautiful Indian-themed UI with bilingual support (Hindi + English) and comprehensive booking management.

## Features

### Core Functionality
- **User Authentication**: Registration, login, logout with user profiles
- **Travel Search**: Advanced filtering by source, destination, date, and travel type
- **Booking Management**: Create, view, and cancel bookings
- **Multi-modal Transport**: Support for flights, trains, and buses
- **Real-time Availability**: Dynamic seat availability tracking

### Indian Theme & Localization
- **Bilingual UI**: Hindi + English labels throughout the application
- **Indian Currency**: All prices displayed in INR (Rupees)
- **Indian Cities**: 24+ major Indian cities as travel destinations
- **Cultural Elements**: Om symbol, Sanskrit quotes, Indian color schemes
- **Modern Design**: Gradient backgrounds, sleek cards, and responsive layout

### Technical Features
- **Django 5.2.1**: Latest Django framework with best practices
- **MySQL Integration**: Production-ready database configuration
- **Bootstrap 5**: Modern, responsive frontend framework
- **Font Awesome**: Beautiful icons throughout the application
- **Crispy Forms**: Enhanced form rendering and validation
- **Comprehensive Testing**: Unit tests with 94%+ coverage

## Live Demo

**Deployed Application**: https://aravindtravel.pythonanywhere.com

**Demo Credentials**:
- Username: demo
- Password: demo123

## Prerequisites

- Python 3.8 or higher
- MySQL 8.0 or higher (for production)
- Git

## Local Setup Instructions

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/travel-lykkr.git
cd travel-lykkr
```

### 2. Create Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Database Setup

#### Option A: SQLite (Development)
```bash
python manage.py migrate
python manage.py populate_sample_data --count 50
```

#### Option B: MySQL (Production-like)
1. Create MySQL database
2. Update settings.py with database credentials
3. Run migrations

### 5. Create Superuser

```bash
python manage.py createsuperuser
```

### 6. Run Development Server

```bash
python manage.py runserver
```

Visit http://127.0.0.1:8000 to access the application.

## Project Highlights

### Backend Excellence
- Django 5.2.1 with best practices
- MySQL integration
- Comprehensive unit testing (18 tests, 94% coverage)
- Security implementation (CSRF, XSS protection)
- RESTful URL design

### Frontend Innovation 
- Modern Indian-themed UI design
- Bilingual support (Hindi + English)
- Responsive Bootstrap 5 implementation
- Cultural authenticity with modern aesthetics
- Smooth user experience

### Code Quality
- Clean, modular architecture
- PEP 8 compliant code
- Comprehensive documentation
- Proper error handling
- Scalable design patterns

### Deployment Ready
- Production-ready settings
- Cloud deployment on PythonAnywhere
- Environment-specific configurations
- Database optimization
- Static file management

**Made with love in India**

