# Oxin Cryptocurrency Mining Platform

## Overview

Oxin is a web-based cryptocurrency mining platform built with Flask that allows users to register, mine OXC tokens, manage their wallets, and track referrals. The platform features a sleek, cyberpunk-inspired design with neon themes and provides both user and admin dashboards.

## System Architecture

### Backend Architecture
- **Framework**: Flask (Python 3.11)
- **ORM**: SQLAlchemy with Flask-SQLAlchemy
- **Database**: SQLite (default), PostgreSQL (production-ready)
- **Authentication**: Session-based authentication with Werkzeug password hashing
- **Application Structure**: Modular design with separated concerns (app.py, models.py, routes.py)

### Frontend Architecture
- **Templates**: Jinja2 templating with Bootstrap 5
- **Styling**: Custom CSS with cyberpunk/neon theme
- **JavaScript**: Vanilla JavaScript for interactivity
- **Icons**: Font Awesome for UI elements
- **Fonts**: Google Fonts (Orbitron for headings, Poppins for body text)

### Database Schema
The application uses SQLAlchemy models with the following key entities:
- **User**: Main user accounts with authentication and mining capabilities
- **AdminUser**: Administrative accounts for platform management
- **MiningSession**: Tracks active and completed mining sessions
- **Deposit**: Records user deposits and transactions
- **Announcement**: System announcements (referenced but not fully implemented)

## Key Components

### User Management
- User registration with email validation
- Referral system with unique referral codes
- Password hashing with Werkzeug security
- Session-based authentication
- User profiles with mining statistics

### Mining System
- 24-hour mining sessions
- Daily reward system (0.5 OXC default)
- Plan-based mining (free/paid tiers)
- Mining progress tracking
- Balance accumulation

### Wallet System
- OXC token balance management
- Transaction history (planned)
- Deposit tracking
- Exchange functionality (placeholder)

### Admin Panel
- User management dashboard
- Mining session monitoring
- Deposit oversight
- System announcements

## Data Flow

1. **User Registration**: New users create accounts with referral code support
2. **Authentication**: Session-based login/logout system
3. **Mining Process**: Users start 24-hour mining sessions to earn OXC
4. **Reward Distribution**: Automatic balance updates upon mining completion
5. **Referral System**: Bonus rewards for referred users
6. **Admin Oversight**: Administrative monitoring and management

## External Dependencies

### Python Packages
- **Flask**: Web framework
- **Flask-SQLAlchemy**: Database ORM
- **Werkzeug**: Security utilities
- **Gunicorn**: WSGI HTTP Server
- **email-validator**: Email validation
- **psycopg2-binary**: PostgreSQL adapter

### Frontend Dependencies
- **Bootstrap 5**: CSS framework
- **Font Awesome**: Icon library
- **Google Fonts**: Typography

### Development Tools
- **uv**: Python package manager
- **Nix**: Development environment

## Deployment Strategy

### Production Setup
- **Server**: Gunicorn WSGI server
- **Database**: PostgreSQL (configured but defaults to SQLite)
- **Deployment**: Replit autoscale deployment
- **Environment**: Containerized with Nix

### Configuration
- Environment variables for database URL and session secrets
- Automatic database initialization with admin user creation
- SSL and production security considerations

### Scalability
- Database connection pooling
- Session management
- Prepared for horizontal scaling

## Changelog

- June 17, 2025: Initial setup
- June 17, 2025: Performance optimization - Fixed JavaScript lag issues, optimized database queries, improved template rendering
- June 17, 2025: Added paid plan features - QR code payment system, USDT BEP20 address integration, admin plan management controls

## User Preferences

Preferred communication style: Simple, everyday language.