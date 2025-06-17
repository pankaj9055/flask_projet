import os
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key-change-in-production")

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///oxin.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

with app.app_context():
    # Import models to ensure tables are created
    import models
    db.create_all()
    
    # Create admin user if it doesn't exist
    from models import AdminUser, PaymentSettings
    from werkzeug.security import generate_password_hash
    
    admin = AdminUser.query.filter_by(email='admin@oxin.com').first()
    if not admin:
        admin = AdminUser(
            email='admin@oxin.com',
            password_hash=generate_password_hash('admin123')
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin user created: admin@oxin.com / admin123")
    
    # Create default payment settings if not exists
    payment_settings = PaymentSettings.query.first()
    if not payment_settings:
        payment_settings = PaymentSettings()
        db.session.add(payment_settings)
        db.session.commit()
        print("Default payment settings created")

# Import routes
import routes
