from flask import Flask, render_template, url_for, flash, redirect
from forms import RegistrationForm, LoginForm, StaffForm, DoctorForm, AddLoc

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

@app.route("/register/staff_reg/<st_username>", methods = ['GET','POST'])
def staff_reg(st_username):
    form = StaffForm()
    if form.validate_on_submit():
        office_loc = form.officelocation.data
        work_date = form.work_date.data
        #print (office_loc)
        #print(work_date)
        registerform.insert_staff(st_username, office_loc, work_date)
        flash(f'Account is Registerd, Please Log in!', 'success')
        return redirect(url_for('home'))
    return render_template('staff_reg.html', form = form)

@app.route("/register/doc_reg/<dr_username>/add_loc", methods = ['GET','POST'])
def add_loc(dr_username):
    form = AddLoc()
    if form.validate_on_submit():
        office_loc = form.officelocation.data
        work_date = form.work_date.data
        office_choice = True
        work_date_choice = True
        if form.submit.data:
            office_choice, work_date_choice = registerform.add_loc(dr_username,office_loc,work_date)
            if office_choice == False:
                flash(f'You Have Worked at This Office, Please Pick another!', 'danger')
            elif work_date_choice == False:
                flash(f'You Have Worked on One of Those Days, Please Pick another!', 'danger')
            else:
                flash(f'Account is Registerd, Please Log in!', 'success')
                return redirect(url_for('home'))
        elif form.add_loc.data:
            office_choice, work_date_choice = registerform.add_loc(dr_username,office_loc,work_date)
            if office_choice == False:
                flash(f'You Have Worked at This Office, Please Pick another!', 'danger')
            elif work_date_choice == False:
                flash(f'You Have Worked on One of Those Days, Please Pick another!', 'danger')
            else:
                #print("Im: ",dr_username)
                #print('I am here')
                return redirect(url_for('add_loc', dr_username = dr_username))
        elif form.cancel.data:
            flash(f'Account is Registerd, Please Log in!', 'success')
            return redirect(url_for('home'))
    else:
            if form.cancel.data:
                flash(f'Account is Registerd, Please Log in!', 'success')
                return redirect(url_for('home'))
    return render_template('add_loc.html', form = form)

@app.route("/register/doc_reg/<dr_username>", methods = ['GET','POST'])
def doc_reg(dr_username):
    form = DoctorForm()
    if form.validate_on_submit():
        office_loc = form.officelocation.data
        work_date = form.work_date.data
        spec = form.specialization.data
        if form.submit.data:
            #print (office_loc)
            #print(work_date)
            registerform.insert_doc(dr_username, office_loc, work_date, spec)
            flash(f'Account is Registerd, Please Log in!', 'success')
            return redirect(url_for('home'))
        elif form.add_loc.data:
            registerform.insert_doc(dr_username, office_loc, work_date, spec)
            return redirect(url_for('add_loc',dr_username = dr_username))
    return render_template('doc_reg.html', form = form)

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
            flash(f"Date of Birth Should be greater than 1900-01-01", 'danger')
        elif registerform.email_check(email) == False:
            flash(f"{username} is already TAKEN, Please use another", 'danger')
        elif registerform.user_check(email) == False:
            flash(f"{email} is already TAKEN, Please use another", 'danger')
        else:
            registerform.insert_to_db(username, password, fname, lname, mname,dob,streetnum, streetname, aptnum, city, state, zipcode, email, phonenum, sex, ethnicity)
            if (iam == "ST"):
                flash(f'Account created for {form.username.data}!', 'success')
                #print(username)
                return redirect(url_for('staff_reg', st_username = username))
            elif (iam == "PA"):
                return redirect(url_for('patient_reg'))
            elif (iam == "DR"):
                #print("dr_name: " + username)
                return redirect(url_for('doc_reg', dr_username = username))
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
                return render_template('patient.html')
            elif login_check.account_type(username, password) == "doctor":
                flash('You Successfully Log in')
                return render_template('doctor.html')
            elif login_check.account_type(username, password) == "patient":
                flash('You Successfully Log in')
                return render_template('staff.html')
        else:
            flash('Invalid Account, Check Your Username and Password', 'danger')

    return render_template('login.html', title='Login', form=form)


if __name__ == '__main__':
    app.run(debug=True)
