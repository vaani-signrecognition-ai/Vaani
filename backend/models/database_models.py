"""
Database models for VAANI application using SQLAlchemy
"""
from datetime import datetime
from extensions import db


class SignDictionary(db.Model):
    """Sign language dictionary table"""
    __tablename__ = 'sign_dictionary'
    
    sign_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    word = db.Column(db.String(100), nullable=False)
    starting_letter = db.Column(db.String(1), nullable=False)
    video_path = db.Column(db.String(255), nullable=True)
    image_path = db.Column(db.String(255), nullable=True)
    
    def to_dict(self):
        return {
            'sign_id': self.sign_id,
            'word': self.word,
            'starting_letter': self.starting_letter,
            'video_path': self.video_path,
            'image_path': self.image_path
        }


class NGO(db.Model):
    """NGO organizations table"""
    __tablename__ = 'ngos'
    
    ngo_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ngo_name = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15))
    city = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    events = db.relationship('Event', backref='ngo', lazy=True)
    
    def to_dict(self):
        return {
            'ngo_id': self.ngo_id,
            'ngo_name': self.ngo_name,
            'email': self.email,
            'phone': self.phone,
            'city': self.city,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }


class Event(db.Model):
    """Events table"""
    __tablename__ = 'events'
    
    event_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    ngo_id = db.Column(db.Integer, db.ForeignKey('ngos.ngo_id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    event_date = db.Column(db.Date, nullable=False)
    location = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'event_id': self.event_id,
            'ngo_id': self.ngo_id,
            'title': self.title,
            'description': self.description,
            'event_date': self.event_date.isoformat() if self.event_date else None,
            'location': self.location,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'ngo_name': self.ngo.ngo_name if self.ngo else None
        }


class NGORequest(db.Model):
    """NGO partnership requests table"""
    __tablename__ = 'ngo_requests'
    
    request_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    org_name = db.Column(db.String(200), nullable=False)
    contact_person = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(15), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    purpose = db.Column(db.String(500), nullable=False)
    description = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(20), default='PENDING')  # PENDING, APPROVED, REJECTED
    submitted_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'request_id': self.request_id,
            'org_name': self.org_name,
            'contact_person': self.contact_person,
            'email': self.email,
            'phone': self.phone,
            'city': self.city,
            'purpose': self.purpose,
            'description': self.description,
            'status': self.status,
            'submitted_at': self.submitted_at.isoformat() if self.submitted_at else None
        }


class NGOAccount(db.Model):
    """NGO login accounts table"""
    __tablename__ = 'ngo_accounts'
    
    account_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    request_id = db.Column(db.Integer, db.ForeignKey('ngo_requests.request_id'), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationship
    request = db.relationship('NGORequest', backref='account', uselist=False)
    
    def to_dict(self):
        return {
            'account_id': self.account_id,
            'request_id': self.request_id,
            'email': self.email,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }
