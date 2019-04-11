from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm, StaffForm

import pymysql
import appointment
import login_check
import registerform
import forms
from QueryEngine import QueryEngine

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'


@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')


@app.route("/about")
def about():
    return render_template('about.html', title='About')

@app.route("/register/<st_username>", methods = ['GET','POST'])
def staff_reg(st_username):
    form = StaffForm()
    if form.validate_on_submit():
        office_loc = form.officelocation.data
        work_date = form.work_date.data
        registerform.insert_staff(st_username, office_loc, work_date)
        flash(f'Account is Registerd, Please Log in!', 'success')
        return redirect(url_for('home'))
    return render_template('staff_reg.html', form = form)


'''
AFTTER LOG IN VIEWS FOR PATIENT, DOCTOR AND STAFF 
 '''

@app.route("/After_Login_Patient", methods=['GET', 'POST'])
def After_Login_Patient():
    return render_template('After_Login_Patient.html')

@app.route("/After_Login_Doctor", methods=['GET', 'POST'])
def After_Login_Doctor():
    return render_template('After_Login_Patient.html')

@app.route("/After_Login_Staff", methods=['GET', 'POST'])
def After_Login_Staff():
    return render_template('After_Login_Patient.html')



@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        fname = form.firstname.data
        lname = form.lastname.data
        mname = form.middleinitial.data
        dob = form.dob.data
        streetnum = form.streetnumber.data
        streetname = form.streetname.data
        aptnum = form.aptnumber.data
        city = form.city.data
        state = form.statename.data
        zipcode = form.zipcode.data
        phonenum = form.phonenumber.data
        sex = form.sex.data
        ethnicity = form.ethnicity.data
        email = form.email.data
        iam = form.iam.data

        if (mname == ""):
            mname = None

        if ethnicity == "W":
            ethnicity = "White"
        elif ethnicity == "AA":
            ethnicity = "African American"
        elif ethnicity == "AI":
            ethnicity = "Asian"
        elif ethnicity == "NA":
            ethnicity = "Native American"
        elif ethnicity == "PI":
            ethnicity = "Pacific Islander"
        elif ethnicity == "HI":
            ethnicity = "Pacific Islander"
        elif ethnicity == "OT":
            ethnicity = "Others"

        #print(username, password, fname, lname, mname,dob,streetnum, streetname, aptnum, city, state, zipcode, email, phonenum, sex, ethnicity)
        if dob <= "1900-01-01":
            flash(f"Date of Birth Should be greater than 1900-01-01")
        elif registerform.email_check(email) == False:
            flash(f"{username} is already TAKEN, Please use another")
        elif registerform.user_check(email) == False:
            flash(f"{email} is already TAKEN, Please use another")
        else:
            registerform.insert_to_db(username, password, fname, lname, mname,dob,streetnum, streetname, aptnum, city, state, zipcode, email, phonenum, sex, ethnicity)
            if (iam == "ST"):
                flash(f'Account created for {form.username.data}!', 'success')
                #print(username)
                return redirect(url_for('staff_reg', st_username = username))
            elif (iam == "PA"):
                return redirect(url_for('patient_reg'))
            elif (iam == "DR"):
                return redirect(url_for('doc_reg'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.user.data
        password = form.password.data
        if login_check.login_check(username, password) == True:
            if login_check.account_type(username, password) == "patient":
                flash('You Successfully Log in')
                return redirect(url_for('After_Login_Patient'))

            elif login_check.account_type(username, password) == "doctor":
                flash('You Successfully Log in')
                return redirect(url_for('After_Login_Doctor'))

            elif login_check.account_type(username, password) == "staff":
                flash('You Successfully Log in')
                return redirect(url_for('After_Login_Staff'))
        else:
            flash('Invalid Account, Check Your Username and Password', 'danger')

    return render_template('login.html', title='Login', form=form)

#----------------------------------
@app.route("/appointment", methods=['GET', 'POST'])
def appointment():
    return render_template('appointment.html',title="Appointment")

@app.route("/manage_account", methods=['GET', 'POST'])
def manage_account():
    return render_template('manage_account.html',title="Manage Account")


if __name__ == '__main__':
    app.run(debug=True)
