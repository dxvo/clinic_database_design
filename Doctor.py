from flask_wtf import FlaskForm
from wtforms import TextField, IntegerField, SelectField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo

class DoctorForm(FlaskForm):
    specialization = SelectField('Specilalization', choices = [('Allergy and Immunology', 'Ansethesiology', 'Dermatology', 
    'Diagonostic Radiology', 'Emergency Medicine', 'Family Medicine', 'General Medicine', 'Internal Medicine', 'Medical Genetics', 'Neurology', 
    'Nuclear Medicine', 'Obstetrics and Gynecology', 'Ophthalmology', 'Pathology', 'Pediatrics', 'Physical Medicine and Rehabili',
    'Preventive Medicine', 'Psychiatry', 'Radiation Oncology', 'Sugery', 'Urology')], validators=[DataRequired()])
