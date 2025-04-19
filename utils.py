import os
import uuid
import secrets
from datetime import datetime
from werkzeug.utils import secure_filename

from app import app, db
from models import Document


def generate_application_number():
    """Generate a unique application number"""
    prefix = "ADM"
    timestamp = datetime.utcnow().strftime("%Y%m%d")
    random_suffix = secrets.token_hex(4).upper()
    return f"{prefix}{timestamp}{random_suffix}"


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']


def save_document(file_data, application_id, document_type):
    """Save an uploaded document and record it in the database"""
    if file_data and allowed_file(file_data.filename):
        # Create a secure filename with unique identifier
        original_filename = secure_filename(file_data.filename)
        extension = original_filename.rsplit('.', 1)[1].lower()
        unique_filename = f"{document_type}_{uuid.uuid4().hex}.{extension}"
        
        # Save the file
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file_data.save(file_path)
        
        # Check if document of this type already exists
        existing_doc = Document.query.filter_by(
            application_id=application_id, 
            document_type=document_type
        ).first()
        
        if existing_doc:
            # Delete old file if exists
            old_file_path = os.path.join(app.config['UPLOAD_FOLDER'], existing_doc.filename)
            if os.path.exists(old_file_path):
                os.remove(old_file_path)
            
            # Update existing document record
            existing_doc.filename = unique_filename
            existing_doc.uploaded_at = datetime.utcnow()
        else:
            # Create new document record
            new_document = Document(
                application_id=application_id,
                document_type=document_type,
                filename=unique_filename
            )
            db.session.add(new_document)
        
        db.session.commit()
        return True
    return False


def get_document_url(filename):
    """Generate URL for accessing a document"""
    if not filename:
        return None
    return f"/static/uploads/{filename}"
