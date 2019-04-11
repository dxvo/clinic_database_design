from flask_wtf import FlaskForm
from wtforms import StringField,IntegerField,SelectField,PasswordField,SubmitField,BooleanField,DateField,widgets, SelectMultipleField
from wtforms.validators import DataRequired,Length,Email,EqualTo,NumberRange,Optional
from wtforms.widgets import PasswordInput, CheckboxInput, ListWidget
from QueryEngine import QueryEngine
import string
qe = QueryEngine()
qe.setup_default()

class MultiCheckboxField(SelectMultipleField):
	widget			= widgets.ListWidget(prefix_label=False)
	option_widget	= widgets.CheckboxInput()

class LoginForm(FlaskForm):
    user = StringField('Username',
                        validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class RegistrationForm(FlaskForm):
    firstname = StringField('FirstName',validators=[DataRequired(),Length(min = 1,max = 15)])
    lastname = StringField('LastName',validators=[DataRequired(),Length(min = 1, max = 20)])
    middleinitial = StringField('M.I',validators = [Optional(),Length(max=1)])
    iam = SelectField('I Am..', 
        choices = [('',''),('PA','Patient'),('DR','Doctor'),('ST','Staff')],
        validators=[DataRequired(),Length(min = 1)])

    dob = StringField('Date of Birth',validators=[DataRequired(),Length(min = 10,max = 10)],
        render_kw={"placeholder": "yyyy-mm-dd"})

    streetnumber = IntegerField('Street Number',validators=[DataRequired()])
    streetname = StringField('Street Name',validators=[DataRequired(),Length(min = 1,max = 35)])
    aptnumber = IntegerField('Apt-Number',validators = [Optional()], default = None)
    city = StringField('City',validators = [DataRequired(),Length(min = 1,max = 20)])
    statename = SelectField('State',
        choices = [('AL','Alabama'),('AK','Alaska'),
        ('AZ','Arizona'),('AR','Arkansas'),('CA','California'),
        ('CO','Colorado'),('CT','Connecticut'),('DE','Delaware'),
        ('DC','District Of Columbia'),('FL','Florida'),('GA','Georgia'),
        ('HI','Hawaii'),('ID','Idaho'),('IL','Illinois'),('IN','Indiana'),
        ('IA','Iowa'),('KS','Kansas'),('KY','Kentucky'),('LA','Louisiana'),
        ('ME','Maine'),('MD','Maryland'),('MA','Massachusetts'),('MI','Michigan'),
        ('MN','Minnesota'),('MS','Mississippi'),('MO','Missouri'),
        ('MT','Montana'),('NE','Nebraska'),('NV','Nevada'),('NH','New Hampshire'),
        ('NJ','New Jersey'),('NM','New Mexico'),('NY','New York'),('NC','North Carolina'),
        ('ND','North Dakota'),('OH','Ohio'),('OK','Oklahoma'),('OR','Oregon'),('PA','Pennsylvania'),
        ('PR','Puerto Rico'),('RI','Rhode Island'),('SC','South Carolina'),
        ('SD','South Dakota'),('TN','Tennessee'),('TX','Texas'),('UT','Utah'),
        ('VT','Vermont'),('VA','Virginia'),('WA','Washington'),('WV','West Virginia'),
        ('WI','Wisconsin'),('WY','Wyoming')],validators=[DataRequired()])

    zipcode = IntegerField('Zip code',validators=[DataRequired()])
    phonenumber = StringField('Phone Number',validators=[DataRequired(),Length(min = 10, max = 10)],
        render_kw={"placeholder": "1234567890"})
    sex = SelectField('Sex', choices=[('',''),('male','Male'),('female','Female')],validators=[DataRequired(),Length(min = 1)])
    ethnicity =  SelectField('Ethnicity',
        choices=[('',''),('W','White'),('AA','African American'),('AI','Asian'),
        ('NA','Native American'),('PI','Pacific Islander'),('HI','Hispanic'),('OT','Others')],

        validators=[DataRequired(),Length(min = 1)])
    
    username = StringField('UserName',validators=[DataRequired(),Length(min = 4,max = 20)])
    email = StringField('Email',validators = [DataRequired(),Email(),Length(max = 30)])
    password = StringField('Password',validators=[DataRequired(), 
        Length(min = 6,max = 20)],widget=PasswordInput(hide_value=False))

    cpassword = PasswordField('Confirm Password',validators=[DataRequired(),Length(min = 6, max = 20),
        EqualTo('password')],widget=PasswordInput(hide_value=False))
    
    submit = SubmitField('Sign Up')

class StaffForm(FlaskForm):
    query_string = ("Select Office_Name from office")
    qe.connect()
    option_loc = qe.do_query(query_string)
    qe.disconnect()
    loc = []
    for elem in option_loc:
        elem = elem[0]
        loc.append(elem)
    #print(loc)
    officelocation = SelectField('Office Location',choices = [(l, l) for l in loc] ,validators=[DataRequired()])
    work_date = MultiCheckboxField('Working Date', choices= [('M', 'Monday'),('Tu','Tuesday'),('W', 'Wednesday'),('Th','Thursday'),('F','Friday'),('Sa','Saturday'),('Su','Sunday')], validators=[DataRequired()])
    submit = SubmitField('Create')



