import os
import uuid
from datetime import datetime
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

def generate_application_number():
    """Generate a unique application number"""
    # Format: YEAR-MONTH-RANDOM
    year = datetime.now().strftime("%Y")
    month = datetime.now().strftime("%m")
    random_str = str(uuid.uuid4())[:8]
    return f"{year}-{month}-{random_str}"

def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in settings.ALLOWED_EXTENSIONS

def save_document(file_data, application_id, document_type):
    """Save an uploaded document and record it in the database"""
    from .models import Document, Application
    
    if file_data and file_data.name:
        # Generate a unique filename
        ext = file_data.name.rsplit('.', 1)[1].lower() if '.' in file_data.name else ''
        unique_filename = f"{document_type}_{application_id}_{uuid.uuid4().hex}.{ext}"
        
        # Save the file using Django's file storage
        file_path = f'documents/{unique_filename}'
        path = default_storage.save(file_path, ContentFile(file_data.read()))
        
        # Get the application object
        try:
            application = Application.objects.get(id=application_id)
            
            # Delete existing document of the same type if exists
            Document.objects.filter(
                application=application,
                document_type=document_type
            ).delete()
            
            # Create document record in database
            document = Document(
                application=application,
                document_type=document_type,
                file=path
            )
            document.save()
            
            return document
        except Application.DoesNotExist:
            return None
    
    return None

def get_document_path(document):
    """Get the full path to a document file"""
    if document and document.file:
        return document.file.path
    return None