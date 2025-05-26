from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from datetime import date
from .models import Application, Document

class LoginForm(forms.Form):
    email = forms.EmailField(label='Email', required=True)
    password = forms.CharField(label='Password', widget=forms.PasswordInput, required=True)

class RegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['username']
        if commit:
            user.save()
        return user

from django.forms.widgets import RadioSelect

class SelectApplicationForm(forms.Form):
    application_type = forms.ChoiceField(
        label='Application Type',
        choices=[
            ('undergraduate', 'Undergraduate Program'),
            ('postgraduate', 'Postgraduate Program'),
            ('diploma', 'Diploma Course'),
            ('certificate', 'Certificate Program')
        ],
        widget=RadioSelect,
        required=True
    )

import re
from django.core.exceptions import ValidationError

class PersonalInfoForm(forms.ModelForm):
    aadhar_no = forms.CharField(
        label='Aadhar Number',
        max_length=14,
        required=False,
        help_text='Enter 12 digit Aadhar number with spaces after every 4 digits (e.g. 1234 5678 9012)'
    )
    
    course = forms.ModelChoiceField(
        label='Course',
        queryset=None,
        required=False,
        empty_label='Select a course'
    )
    
    class Meta:
        model = Application
        fields = ['first_name', 'last_name', 'date_of_birth', 'gender', 
                 'phone', 'address', 'city', 'state', 'pincode', 'aadhar_no', 'course']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'gender': forms.Select(choices=[
                ('male', 'Male'),
                ('female', 'Female'),
                ('other', 'Other')
            ]),
            'address': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Course
        if self.instance and self.instance.application_type:
            self.fields['course'].queryset = Course.objects.filter(type=self.instance.application_type)
        else:
            self.fields['course'].queryset = Course.objects.none()
    
    def clean_date_of_birth(self):
        dob = self.cleaned_data.get('date_of_birth')
        if dob and dob >= date.today():
            raise ValidationError('Date of birth must be in the past')
        return dob
    
    def clean_aadhar_no(self):
        aadhar_no = self.cleaned_data.get('aadhar_no')
        if aadhar_no:
            pattern = r'^\d{4} \d{4} \d{4}$'
            if not re.match(pattern, aadhar_no):
                raise ValidationError('Aadhar number must be 12 digits with spaces after every 4 digits (e.g. 1234 5678 9012)')
        return aadhar_no

class EducationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['highest_qualification', 'board_university', 'year_of_passing', 'percentage_marks']
        widgets = {
            'highest_qualification': forms.Select(choices=[
                ('10th', '10th Standard'),
                ('12th', '12th Standard'),
                ('bachelor', 'Bachelor\'s Degree'),
                ('master', 'Master\'s Degree'),
                ('phd', 'PhD'),
                ('other', 'Other')
            ])
        }
    
    def clean_year_of_passing(self):
        year = self.cleaned_data.get('year_of_passing')
        if year and (year < 1950 or year > date.today().year):
            raise ValidationError('Year of passing must be between 1950 and current year')
        return year
    
    def clean_percentage_marks(self):
        marks = self.cleaned_data.get('percentage_marks')
        if marks and (marks < 0 or marks > 100):
            raise ValidationError('Percentage must be between 0 and 100')
        return marks

class DocumentUploadForm(forms.Form):
    photo = forms.ImageField(
        label='Passport Size Photograph', 
        required=False,
        widget=forms.FileInput(attrs={'accept': 'image/*'})
    )
    signature = forms.ImageField(
        label='Signature', 
        required=False,
        widget=forms.FileInput(attrs={'accept': 'image/*'})
    )
    aadhar = forms.FileField(
        label='Aadhar Card', 
        required=False,
        widget=forms.FileInput(attrs={'accept': 'image/*, application/pdf'})
    )
    marksheet = forms.FileField(
        label='Educational Marksheet', 
        required=False,
        widget=forms.FileInput(attrs={'accept': 'image/*, application/pdf'})
    )

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo and photo.size > 16 * 1024 * 1024:
            raise forms.ValidationError("Photo file size must be under 16MB.")
        return photo

    def clean_signature(self):
        signature = self.cleaned_data.get('signature')
        if signature and signature.size > 16 * 1024 * 1024:
            raise forms.ValidationError("Signature file size must be under 16MB.")
        return signature

    def clean_aadhar(self):
        aadhar = self.cleaned_data.get('aadhar')
        if aadhar and aadhar.size > 16 * 1024 * 1024:
            raise forms.ValidationError("Aadhar file size must be under 16MB.")
        return aadhar

    def clean_marksheet(self):
        marksheet = self.cleaned_data.get('marksheet')
        if marksheet and marksheet.size > 16 * 1024 * 1024:
            raise forms.ValidationError("Marksheet file size must be under 16MB.")
        return marksheet

class SubmitApplicationForm(forms.Form):
    confirm = forms.BooleanField(
        label='I confirm that all information provided is correct and complete',
        required=True
    )

class ApplicationStatusForm(forms.Form):
    application_number = forms.CharField(
        label='Application Number',
        required=True,
        max_length=20
    )