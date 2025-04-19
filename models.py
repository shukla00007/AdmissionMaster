import enum
from datetime import datetime
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

from app import db, login_manager


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship with applications
    applications = db.relationship('Application', backref='applicant', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def __repr__(self):
        return f'<User {self.username}>'


class ApplicationStatus(enum.Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    application_type = db.Column(db.String(50), nullable=False)
    status = db.Column(db.Enum(ApplicationStatus), default=ApplicationStatus.DRAFT)
    
    # Personal Information
    first_name = db.Column(db.String(100))
    last_name = db.Column(db.String(100))
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(20))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    pincode = db.Column(db.String(10))
    
    # Education Information
    highest_qualification = db.Column(db.String(100))
    board_university = db.Column(db.String(100))
    year_of_passing = db.Column(db.Integer)
    percentage_marks = db.Column(db.Float)
    
    # Application Metadata
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    submitted_at = db.Column(db.DateTime)
    application_number = db.Column(db.String(20), unique=True)
    
    # Relationships
    documents = db.relationship('Document', backref='application', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<Application #{self.application_number} - {self.status.value}>'
    
    def get_completion_status(self):
        """
        Calculate how complete the application is
        """
        steps = {
            'personal': bool(self.first_name and self.last_name and self.date_of_birth and self.gender and 
                           self.phone and self.address),
            'education': bool(self.highest_qualification and self.board_university and self.year_of_passing),
            'documents': self.has_required_documents()
        }
        
        return {
            'personal': steps['personal'],
            'education': steps['education'],
            'documents': steps['documents'],
            'completion_percentage': (sum(1 for step in steps.values() if step) / len(steps)) * 100
        }
    
    def has_required_documents(self):
        """Check if all required documents are uploaded"""
        required_types = {'photo', 'signature', 'aadhar'}
        uploaded_types = {doc.document_type for doc in self.documents}
        return required_types.issubset(uploaded_types)


class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    application_id = db.Column(db.Integer, db.ForeignKey('application.id'), nullable=False)
    document_type = db.Column(db.String(50), nullable=False)
    filename = db.Column(db.String(100), nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Document {self.document_type} for Application {self.application_id}>'
