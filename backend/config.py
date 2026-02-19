"""
Configuration settings for VAANI backend
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(override=True)

class Config:
    """Base configuration"""
    # Flask settings
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-key")
    DEBUG = os.getenv("DEBUG", "False").lower() == "true"
    
    # Database - SQLAlchemy (Use absolute path for local)
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    DEFAULT_DB_PATH = os.path.join(BASE_DIR, "vaani.db")
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{DEFAULT_DB_PATH}"
    
    if SQLALCHEMY_DATABASE_URI.startswith("postgres://"):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Engine options for PostgreSQL (like SSL requirement)
    SQLALCHEMY_ENGINE_OPTIONS = {
        "connect_args": {
            "sslmode": "require"
        }
    } if SQLALCHEMY_DATABASE_URI and SQLALCHEMY_DATABASE_URI.startswith("postgresql") else {}
    
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
    config_class = config_by_name.get(env, DevelopmentConfig)
    
    # Force SQLite for development if needed
    if env == "development":
        print(f"[DEBUG] Development mode: forcing local SQLite")
        # You can also set it directly on the class if you want
        
    return config_class
