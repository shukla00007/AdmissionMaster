from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import StringField, PasswordField, SubmitField, SelectField, DateField
from wtforms import TextAreaField, IntegerField, FloatField, BooleanField, HiddenField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Optional, NumberRange, ValidationError
from datetime import date

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=25)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')

class SelectApplicationForm(FlaskForm):
    application_type = SelectField('Application Type', choices=[
        ('undergraduate', 'Undergraduate Program'),
        ('postgraduate', 'Postgraduate Program'),
        ('diploma', 'Diploma Course'),
        ('certificate', 'Certificate Program')
    ], validators=[DataRequired()])
    submit = SubmitField('Start Application')

class PersonalInfoForm(FlaskForm):
    first_name = StringField('First Name', validators=[DataRequired(), Length(max=100)])
    last_name = StringField('Last Name', validators=[DataRequired(), Length(max=100)])
    date_of_birth = DateField('Date of Birth', validators=[DataRequired()])
    gender = SelectField('Gender', choices=[
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=15)])
    address = TextAreaField('Address', validators=[DataRequired()])
    city = StringField('City', validators=[DataRequired()])
    state = StringField('State', validators=[DataRequired()])
    pincode = StringField('PIN Code', validators=[DataRequired(), Length(min=6, max=10)])
    submit = SubmitField('Save & Continue')

    def validate_date_of_birth(self, field):
        if field.data >= date.today():
            raise ValidationError('Date of birth must be in the past')

class EducationForm(FlaskForm):
    highest_qualification = SelectField('Highest Qualification', choices=[
        ('10th', '10th Standard'),
        ('12th', '12th Standard'),
        ('bachelor', 'Bachelor\'s Degree'),
        ('master', 'Master\'s Degree'),
        ('phd', 'PhD'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    board_university = StringField('Board/University', validators=[DataRequired()])
    year_of_passing = IntegerField('Year of Passing', validators=[
        DataRequired(),
        NumberRange(min=1950, max=date.today().year)
    ])
    percentage_marks = FloatField('Percentage/CGPA', validators=[
        DataRequired(),
        NumberRange(min=0, max=100)
    ])
    submit = SubmitField('Save & Continue')

class DocumentUploadForm(FlaskForm):
    photo = FileField('Passport Size Photograph', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ])
    signature = FileField('Signature', validators=[
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ])
    aadhar = FileField('Aadhar Card', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'pdf'], 'Images or PDF only!')
    ])
    marksheet = FileField('Educational Marksheet', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'pdf'], 'Images or PDF only!')
    ])
    submit = SubmitField('Save & Continue')

class SubmitApplicationForm(FlaskForm):
    confirm = BooleanField('I confirm that all information provided is correct and complete', validators=[DataRequired()])
    submit = SubmitField('Submit Application')

class ApplicationStatusForm(FlaskForm):
    application_number = StringField('Application Number', validators=[DataRequired()])
    submit = SubmitField('Check Status')
