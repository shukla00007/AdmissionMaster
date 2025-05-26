from django.shortcuts import render, redirect, get_object_or_404

# Existing imports and views...

# Removed contact view as per user request to revert changes
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.contrib import messages
from django.utils import timezone
from django.http import HttpResponse, FileResponse
from django.conf import settings

import os
import io
import uuid
from datetime import datetime

from .models import Application, Document, ApplicationStatus, User
from .forms import (LoginForm, RegistrationForm, SelectApplicationForm,
                   PersonalInfoForm, EducationForm, DocumentUploadForm,
                   SubmitApplicationForm, ApplicationStatusForm)
from .utils import generate_application_number, allowed_file, save_document

try:
    import pdfkit
    PDF_ENABLED = True
except ImportError:
    PDF_ENABLED = False

def home(request):
    return render(request, 'applications/home.html', {'title': 'Home'})

@csrf_protect
def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            password = form.cleaned_data.get('password')
            
            # Find user by email
            users = User.objects.filter(email=email)
            if not users.exists():
                messages.error(request, 'Invalid email or password')
            else:
                user_obj = users.first()
                user = authenticate(request, username=user_obj.username, password=password)
                
                if user is not None:
                    login(request, user)
                    next_page = request.GET.get('next')
                    return redirect(next_page) if next_page else redirect('dashboard')
                else:
                    messages.error(request, 'Invalid email or password')
    else:
        form = LoginForm()
    
    return render(request, 'applications/login.html', {'title': 'Login', 'form': form})

def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f'Account created for {user.username}!')
            return redirect('dashboard')
    else:
        form = RegistrationForm()
    
    return render(request, 'applications/register.html', {'title': 'Register', 'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')

@login_required
def dashboard(request):
    applications = Application.objects.filter(user=request.user).order_by('-created_at')
    draft_applications_count = applications.filter(status='draft').count()
    submitted_applications_count = applications.filter(status='submitted').count()
    return render(request, 'applications/dashboard.html', {
        'title': 'Dashboard',
        'applications': applications,
        'draft_applications_count': draft_applications_count,
        'submitted_applications_count': submitted_applications_count,
    })

@login_required
def select_application(request):
    if request.method == 'POST':
        form = SelectApplicationForm(request.POST)
        if form.is_valid():
            application_type = form.cleaned_data.get('application_type')
            
            from .utils import generate_application_number
            
            # Create new application
            application = Application(
                user=request.user,
                application_type=application_type,
                status=ApplicationStatus.DRAFT,
                application_number=generate_application_number()
            )
            application.save()
            
            messages.success(request, 'Application started successfully!')
            return redirect('personal_info', application_id=application.id)
        else:
            import logging
            logger = logging.getLogger(__name__)
            logger.debug(f"SelectApplicationForm errors: {form.errors}")
            logger.debug(f"POST data: {request.POST}")
            messages.error(request, 'Please select a program to continue.')
    else:
        form = SelectApplicationForm(initial={'application_type': 'undergraduate'})
    
    return render(request, 'applications/select_application.html', {
        'title': 'Select Application Type',
        'form': form
    })

@login_required
def personal_info(request, application_id):
    application = get_object_or_404(Application, id=application_id, user=request.user)
    
    if application.status != ApplicationStatus.DRAFT:
        messages.warning(request, 'Cannot edit application after submission.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = PersonalInfoForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            messages.success(request, 'Personal information saved successfully!')
            return redirect('education_info', application_id=application.id)
    else:
        form = PersonalInfoForm(instance=application)
    
    # Get photo document if exists
    photo_document = application.documents.filter(document_type='photo').first()
    
    return render(request, 'applications/personal_info.html', {
        'title': 'Personal Information',
        'form': form,
        'application': application,
        'photo_document': photo_document
    })

@login_required
def education_info(request, application_id):
    application = get_object_or_404(Application, id=application_id, user=request.user)
    
    if application.status != ApplicationStatus.DRAFT:
        messages.warning(request, 'Cannot edit application after submission.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = EducationForm(request.POST, instance=application)
        if form.is_valid():
            form.save()
            messages.success(request, 'Education information saved successfully!')
            return redirect('documents_upload', application_id=application.id)
    else:
        form = EducationForm(instance=application)
    
    return render(request, 'applications/education_info.html', {
        'title': 'Education Information',
        'form': form,
        'application': application
    })

@login_required
def documents_upload(request, application_id):
    application = get_object_or_404(Application, id=application_id, user=request.user)
    
    if application.status != ApplicationStatus.DRAFT:
        messages.warning(request, 'Cannot edit application after submission.')
        return redirect('dashboard')
    
    # Get existing documents
    existing_documents = {doc.document_type: doc for doc in application.documents.all()}
    
    if request.method == 'POST':
        form = DocumentUploadForm(request.POST, request.FILES)
        if form.is_valid():
            # Process each file upload
            for doc_type in ['photo', 'signature', 'aadhar', 'marksheet']:
                if doc_type in request.FILES:
                    file = request.FILES[doc_type]
                    if file and allowed_file(file.name):
                        try:
                            save_document(file, application.id, doc_type)
                        except Exception as e:
                            import logging
                            logger = logging.getLogger(__name__)
                            logger.error(f"Error saving document {doc_type} for application {application.id}: {e}")
                            messages.error(request, f"Failed to save {doc_type} document. Please try again.")
                            return redirect('documents_upload', application_id=application.id)
            
            messages.success(request, 'Documents uploaded successfully!')
            if 'save_continue' in request.POST:
                return redirect('preview_application', application_id=application.id)
            else:
                return redirect('documents_upload', application_id=application.id)
        else:
            # Form is invalid, redisplay with errors
            messages.error(request, 'Please correct the errors below.')
    else:
        form = DocumentUploadForm()
    
    return render(request, 'applications/documents_upload.html', {
        'title': 'Upload Documents',
        'form': form,
        'application': application,
        'existing_documents': existing_documents
    })

@login_required
def preview_application(request, application_id):
    application = get_object_or_404(Application, id=application_id, user=request.user)
    documents_qs = application.documents.all()
    documents = {doc.document_type: doc for doc in documents_qs}
    
    if request.method == 'POST':
        return redirect('submit_application', application_id=application.id)
    
    completion_status = application.get_completion_status()
    
    return render(request, 'applications/preview_application.html', {
        'title': 'Preview Application',
        'application': application,
        'documents': documents,
        'completion_status': completion_status
    })

@login_required
def submit_application(request, application_id):
    application = get_object_or_404(Application, id=application_id, user=request.user)
    
    if application.status != ApplicationStatus.DRAFT:
        messages.warning(request, 'Application has already been submitted.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = SubmitApplicationForm(request.POST)
        if form.is_valid() and form.cleaned_data.get('confirm'):
            # Update application status
            application.status = ApplicationStatus.SUBMITTED
            if not application.application_number:
                application.application_number = generate_application_number()
            application.submitted_at = timezone.now()
            application.save()
            
            messages.success(request, 'Application submitted successfully!')
            return redirect('dashboard')
    else:
        form = SubmitApplicationForm()
    
    completion_status = application.get_completion_status()
    
    return render(request, 'applications/submit_application.html', {
        'title': 'Submit Application',
        'form': form,
        'application': application,
        'completion_status': completion_status
    })

def check_status(request):
    if request.method == 'POST':
        form = ApplicationStatusForm(request.POST)
        if form.is_valid():
            application_number = form.cleaned_data.get('application_number')
            
            try:
                application = Application.objects.get(application_number=application_number)
                return render(request, 'applications/status_result.html', {
                    'title': 'Application Status',
                    'application': application
                })
            except Application.DoesNotExist:
                messages.error(request, 'Application not found with the given number.')
    else:
        form = ApplicationStatusForm()
    
    return render(request, 'applications/check_status.html', {
        'title': 'Check Application Status',
        'form': form
    })

from pdfkit.configuration import Configuration
import pdfkit

@login_required
@csrf_exempt
def download_application(request, application_id):
    application = get_object_or_404(Application, id=application_id)
    
    # Check if user is authorized to view this application
    if application.user != request.user and not request.user.is_staff:
        return HttpResponse('Unauthorized', status=401)
    
    # Generate PDF if PDFKit is available, otherwise show HTML version
    if PDF_ENABLED:
        try:
            # Prepare documents dictionary keyed by document_type
            documents_qs = application.documents.all()
            documents = {}
            for doc in documents_qs:
                if doc.file and hasattr(doc.file, 'url'):
                    # Build absolute URL for wkhtmltopdf
                    doc.file_url = f"{request.scheme}://{request.get_host()}{settings.MEDIA_URL}{doc.file.name}"
                else:
                    doc.file_url = ''
                documents[doc.document_type] = doc
            
            # Remove base64 photo embedding since it causes protocol error
            photo_base64 = ''
            
            html = render(request, 'applications/application_pdf_minimal.html', {
                'application': application,
                'documents': documents,
                'photo_base64': photo_base64
            }).content.decode('utf-8')
            
            # Attempt to find wkhtmltopdf executable path
            import shutil
            wkhtmltopdf_path = shutil.which('wkhtmltopdf')
            
            if wkhtmltopdf_path is None:
                # Fallback to user provided path if executable not found in PATH
                wkhtmltopdf_path = r'F:\wkhtmltopdf\bin\wkhtmltopdf.exe'
            
            from pdfkit.configuration import Configuration
            config = Configuration(wkhtmltopdf=wkhtmltopdf_path)
            
            try:
                # Convert to PDF with options to enable local file access and prevent network errors
                options = {
                    'enable-local-file-access': None,
                    'no-stop-slow-scripts': None,
                    'debug-javascript': None,
                    'no-images': False,
                    'load-error-handling': 'ignore',
                    'load-media-error-handling': 'ignore',
                }
                pdf = pdfkit.from_string(html, False, options=options, configuration=config)
            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"PDF generation error: {e}")
                from django.contrib import messages
                messages.error(request, f'PDF generation failed: {e}. Please try again later.')
                return redirect('preview_application', application_id=application.id)
            
            # Save PDF to file
            filename = f"Application_{application.application_number}.pdf"
            file_path = os.path.join(settings.MEDIA_ROOT, filename)
            with open(file_path, 'wb') as f:
                f.write(pdf)
            
            # Prepare response
            response = HttpResponse(pdf, content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
        except OSError as e:
            # Handle missing wkhtmltopdf executable gracefully by showing error message
            from django.contrib import messages
            messages.error(request, 'PDF generation failed: wkhtmltopdf executable not found. Please install wkhtmltopdf to enable PDF downloads.')
            return redirect('preview_application', application_id=application.id)
    else:
        # If PDFKit not available, show HTML version
        return render(request, 'applications/application_pdf.html', {
            'application': application
        })
