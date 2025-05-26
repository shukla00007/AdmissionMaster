from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password

class ApplicationStatus(models.TextChoices):
    DRAFT = "draft", "Draft"
    SUBMITTED = "submitted", "Submitted"
    UNDER_REVIEW = "under_review", "Under Review"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"

class Course(models.Model):
    COURSE_TYPE_CHOICES = [
        ('undergraduate', 'Undergraduate'),
        ('postgraduate', 'Postgraduate'),
        ('diploma', 'Diploma'),
        ('certificate', 'Certificate'),
    ]

    name = models.CharField(max_length=200, unique=True)
    type = models.CharField(max_length=20, choices=COURSE_TYPE_CHOICES, default='undergraduate')

    def __str__(self):
        return self.name

class Application(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    application_type = models.CharField(max_length=50)
    status = models.CharField(
        max_length=20,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.DRAFT
    )
    
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='applications')
    
    # Personal Information
    first_name = models.CharField(max_length=100, blank=True, null=True)
    last_name = models.CharField(max_length=100, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=20, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    state = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    aadhar_no = models.CharField(max_length=14, blank=True, null=True)
    
    # Education Information
    highest_qualification = models.CharField(max_length=100, blank=True, null=True)
    board_university = models.CharField(max_length=100, blank=True, null=True)
    year_of_passing = models.IntegerField(blank=True, null=True)
    percentage_marks = models.FloatField(blank=True, null=True)
    
    # Application Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    submitted_at = models.DateTimeField(blank=True, null=True)
    application_number = models.CharField(max_length=20, unique=True, blank=True, null=True)
    
    def __str__(self):
        return f"Application #{self.application_number or 'New'} - {self.get_status_display()}"
    
    def get_completion_status(self):
        """
        Calculate how complete the application is
        """
        steps = {
            'personal': bool(self.first_name and self.last_name and self.date_of_birth and 
                         self.gender and self.phone and self.address),
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
        uploaded_types = set(self.documents.values_list('document_type', flat=True))
        return required_types.issubset(uploaded_types)
    
    def save(self, *args, **kwargs):
        # Generate application number if not exists (regardless of status)
        if not self.application_number:
            import uuid
            import datetime
            
            # Format: YEAR-MONTH-RANDOM
            year = datetime.datetime.now().strftime("%Y")
            month = datetime.datetime.now().strftime("%m")
            random_str = str(uuid.uuid4())[:8]
            self.application_number = f"{year}-{month}-{random_str}"
            
            # Set submitted timestamp if status is submitted
            if self.status == ApplicationStatus.SUBMITTED and not self.submitted_at:
                self.submitted_at = timezone.now()
            
        super().save(*args, **kwargs)

class Document(models.Model):
    application = models.ForeignKey(
        Application, 
        on_delete=models.CASCADE, 
        related_name='documents'
    )
    document_type = models.CharField(max_length=50)
    file = models.FileField(upload_to='documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.document_type} for {self.application}"
    
    def image_preview(self):
        if self.file and hasattr(self.file, 'url'):
            if self.file.url.lower().endswith(('.jpg', '.jpeg', '.png', '.gif')):
                return f'<img src="{self.file.url}" style="max-height: 150px;" />'
        return ''
    image_preview.allow_tags = True
