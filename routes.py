import os
from datetime import datetime
import secrets
import uuid
from flask import render_template, redirect, url_for, flash, request, abort, jsonify, send_from_directory
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.utils import secure_filename
import pdfkit

from app import app, db
from models import User, Application, ApplicationStatus, Document
from forms import (LoginForm, RegistrationForm, SelectApplicationForm, PersonalInfoForm,
                  EducationForm, DocumentUploadForm, SubmitApplicationForm, ApplicationStatusForm)
from utils import generate_application_number, allowed_file, save_document


def register_routes(app):
    @app.route('/')
    @app.route('/home')
    def home():
        return render_template('home.html', title='Home')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and user.check_password(form.password.data):
                login_user(user)
                next_page = request.args.get('next')
                return redirect(next_page) if next_page else redirect(url_for('dashboard'))
            else:
                flash('Login Unsuccessful. Please check email and password', 'danger')
        
        return render_template('login.html', title='Login', form=form)

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        
        form = RegistrationForm()
        if form.validate_on_submit():
            user = User(username=form.username.data, email=form.email.data)
            user.set_password(form.password.data)
            db.session.add(user)
            db.session.commit()
            flash('Your account has been created! You can now log in', 'success')
            return redirect(url_for('login'))
        
        return render_template('register.html', title='Register', form=form)

    @app.route('/logout')
    def logout():
        logout_user()
        return redirect(url_for('home'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        applications = Application.query.filter_by(user_id=current_user.id).all()
        return render_template('dashboard.html', title='Dashboard', applications=applications)

    @app.route('/application/select', methods=['GET', 'POST'])
    @login_required
    def select_application():
        form = SelectApplicationForm()
        if form.validate_on_submit():
            # Create a new application
            application = Application(
                user_id=current_user.id,
                application_type=form.application_type.data,
                status=ApplicationStatus.DRAFT,
                application_number=generate_application_number()
            )
            db.session.add(application)
            db.session.commit()
            flash('Application started successfully!', 'success')
            return redirect(url_for('personal_info', application_id=application.id))
        
        return render_template('application/select.html', title='Select Application Type', form=form)

    @app.route('/application/<int:application_id>/personal', methods=['GET', 'POST'])
    @login_required
    def personal_info(application_id):
        application = Application.query.get_or_404(application_id)
        
        # Check if application belongs to current user
        if application.user_id != current_user.id:
            abort(403)
        
        form = PersonalInfoForm()
        
        if request.method == 'GET':
            # Pre-fill form with existing data if available
            if application.first_name:
                form.first_name.data = application.first_name
                form.last_name.data = application.last_name
                form.date_of_birth.data = application.date_of_birth
                form.gender.data = application.gender
                form.phone.data = application.phone
                form.address.data = application.address
                form.city.data = application.city
                form.state.data = application.state
                form.pincode.data = application.pincode
        
        if form.validate_on_submit():
            # Update application with form data
            application.first_name = form.first_name.data
            application.last_name = form.last_name.data
            application.date_of_birth = form.date_of_birth.data
            application.gender = form.gender.data
            application.phone = form.phone.data
            application.address = form.address.data
            application.city = form.city.data
            application.state = form.state.data
            application.pincode = form.pincode.data
            
            db.session.commit()
            flash('Personal information saved successfully!', 'success')
            return redirect(url_for('education_info', application_id=application.id))
        
        return render_template('application/personal_info.html', title='Personal Information', 
                              form=form, application=application)

    @app.route('/application/<int:application_id>/education', methods=['GET', 'POST'])
    @login_required
    def education_info(application_id):
        application = Application.query.get_or_404(application_id)
        
        # Check if application belongs to current user
        if application.user_id != current_user.id:
            abort(403)
        
        form = EducationForm()
        
        if request.method == 'GET':
            # Pre-fill form with existing data if available
            if application.highest_qualification:
                form.highest_qualification.data = application.highest_qualification
                form.board_university.data = application.board_university
                form.year_of_passing.data = application.year_of_passing
                form.percentage_marks.data = application.percentage_marks
        
        if form.validate_on_submit():
            # Update application with form data
            application.highest_qualification = form.highest_qualification.data
            application.board_university = form.board_university.data
            application.year_of_passing = form.year_of_passing.data
            application.percentage_marks = form.percentage_marks.data
            
            db.session.commit()
            flash('Education information saved successfully!', 'success')
            return redirect(url_for('documents_upload', application_id=application.id))
        
        return render_template('application/education.html', title='Education Information', 
                              form=form, application=application)

    @app.route('/application/<int:application_id>/documents', methods=['GET', 'POST'])
    @login_required
    def documents_upload(application_id):
        application = Application.query.get_or_404(application_id)
        
        # Check if application belongs to current user
        if application.user_id != current_user.id:
            abort(403)
        
        form = DocumentUploadForm()
        
        if form.validate_on_submit():
            if form.photo.data:
                save_document(form.photo.data, application.id, 'photo')
            
            if form.signature.data:
                save_document(form.signature.data, application.id, 'signature')
            
            if form.aadhar.data:
                save_document(form.aadhar.data, application.id, 'aadhar')
            
            if form.marksheet.data:
                save_document(form.marksheet.data, application.id, 'marksheet')
            
            flash('Documents uploaded successfully!', 'success')
            return redirect(url_for('preview_application', application_id=application.id))
        
        # Get existing documents
        documents = Document.query.filter_by(application_id=application.id).all()
        document_dict = {doc.document_type: doc for doc in documents}
        
        return render_template('application/documents.html', title='Document Upload', 
                              form=form, application=application, documents=document_dict)

    @app.route('/application/<int:application_id>/preview', methods=['GET'])
    @login_required
    def preview_application(application_id):
        application = Application.query.get_or_404(application_id)
        
        # Check if application belongs to current user
        if application.user_id != current_user.id:
            abort(403)
        
        # Get documents
        documents = Document.query.filter_by(application_id=application.id).all()
        document_dict = {doc.document_type: doc for doc in documents}
        
        return render_template('application/preview.html', title='Application Preview', 
                              application=application, documents=document_dict)

    @app.route('/application/<int:application_id>/submit', methods=['GET', 'POST'])
    @login_required
    def submit_application(application_id):
        application = Application.query.get_or_404(application_id)
        
        # Check if application belongs to current user
        if application.user_id != current_user.id:
            abort(403)
        
        # Check if all required fields are filled
        completion_status = application.get_completion_status()
        if not all([completion_status['personal'], completion_status['education'], completion_status['documents']]):
            flash('Please complete all sections before submitting the application.', 'danger')
            return redirect(url_for('preview_application', application_id=application.id))
        
        form = SubmitApplicationForm()
        
        if form.validate_on_submit():
            application.status = ApplicationStatus.SUBMITTED
            application.submitted_at = datetime.utcnow()
            db.session.commit()
            flash('Application submitted successfully!', 'success')
            return redirect(url_for('dashboard'))
        
        return render_template('application/submit.html', title='Submit Application', 
                              form=form, application=application)

    @app.route('/application/status', methods=['GET', 'POST'])
    def check_status():
        form = ApplicationStatusForm()
        application = None
        
        if form.validate_on_submit():
            application = Application.query.filter_by(application_number=form.application_number.data).first()
            if not application:
                flash('Application not found. Please check the application number.', 'danger')
        
        return render_template('application/status.html', title='Application Status', 
                              form=form, application=application)

    @app.route('/application/<int:application_id>/download', methods=['GET'])
    @login_required
    def download_application(application_id):
        application = Application.query.get_or_404(application_id)
        
        # Check if application belongs to current user or if user provided correct application number for public access
        if current_user.is_authenticated and application.user_id != current_user.id:
            abort(403)
        
        # Get documents
        documents = Document.query.filter_by(application_id=application.id).all()
        document_dict = {doc.document_type: doc for doc in documents}
        
        # Generate PDF
        rendered = render_template('application/preview.html', 
                                 application=application, 
                                 documents=document_dict,
                                 print_view=True)
        
        pdf = pdfkit.from_string(rendered, False)
        
        # Create a unique filename
        filename = f"application_{application.application_number}.pdf"
        
        # Return the PDF as a downloadable file
        return send_from_directory(
            directory=app.config['UPLOAD_FOLDER'],
            path=filename,
            as_attachment=True,
            download_name=filename
        )

    # Error handlers
    @app.errorhandler(404)
    def not_found_error(error):
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        return render_template('errors/500.html'), 500
