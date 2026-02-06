"""
Configuration settings for VAANI backend
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Base configuration"""
    # Flask settings
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # Database - SQLAlchemy
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Email settings
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SENDER_EMAIL = os.getenv("SENDER_EMAIL", "vaani.isl@gmail.com")
    SENDER_PASSWORD = os.getenv("SENDER_PASSWORD", "")
    
    # Model paths
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    MODELS_DIR = os.path.join(BASE_DIR, "models")
    
    # Static files
    STATIC_DIR = os.path.join(BASE_DIR, "static")
    ISL_WORDS_DIR = os.path.join(STATIC_DIR, "isl_words")


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False


# Select configuration based on environment
config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig
}

def get_config():
    env = os.getenv("FLASK_ENV", "development")
    return config_by_name.get(env, DevelopmentConfig)
