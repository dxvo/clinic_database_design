from flask import Flask, render_template, url_for, flash, redirect, request
from forms import RegistrationForm, LoginForm, StaffForm, DoctorForm, AddLoc, PatientForm, PriPhys, Insurance
from QueryEngine import QueryEngine
from datetime import datetime,date
import pymysql
import appointment
import login_check
import registerform
import forms

qe = QueryEngine()
qe.setup_default()

app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/contact")
def contact():
    return render_template('contact.html')

@app.route("/about")
def about():
    return render_template('about.html', title='About')

'''
General Registration 
'''
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
        
        if registerform.email_check(email) == False:
            flash(f"{email} is already TAKEN, Please use another", 'danger')

        elif registerform.user_check(username) == False:
            flash(f"{username} is already TAKEN, Please use another", 'danger')
        
        elif phonenum.isdigit() == False:
            flash(f'Please Enter a Valid Phone Number', 'danger')
        elif (dob < date(1900,1,1)) or (dob > date.today()) :
            flash(f"Please Enter a Valid Date of Birth", 'danger')
        else:
            registerform.insert_to_db(username, password, fname, lname, mname,dob,streetnum, streetname, aptnum, city, state, zipcode, email, phonenum, sex, ethnicity)
            if (iam == "ST"):
                flash(f'Account created for {form.username.data}!', 'success')
                #print(username)
                return redirect(url_for('staff_reg', st_username = username))
            elif (iam == "PA"):
                return redirect(url_for('patient_reg', pt_username = username))
            elif (iam == "DR"):
                #print("dr_name: " + username)
                return redirect(url_for('doc_reg', dr_username = username))

    return render_template('register.html', title='Register', form=form)



'''
PATIENT REGISTRATION
____________________________
1. Register General Account Info 
2. Choose Location 
3. Choocse Doctor 
4. Insurance Info 
'''
@app.route("/patient_reg/<pt_username>", methods = ['GET','POST'])
def patient_reg(pt_username):
    form = PatientForm()
    if form.validate_on_submit():
        location = form.officelocation.data
        return redirect(url_for('primary_phys_pick',office = location, pt_username = pt_username))
    return render_template('patient_reg.html', form = form)



@app.route("/patient_reg/<pt_username>/<office>", methods = ['GET','POST'])
def primary_phys_pick(office, pt_username):
    form = PriPhys()
    query_string = (f"SELECT Office_ID FROM OFFICE WHERE Office_Name = '{office}'")
    qe.connect()
    office_id = qe.do_query(query_string)
    qe.disconnect()
    office_id = office_id[0][0]
    print(office_id)
    query_string = (f"SELECT Hospital_ID, Last_Name FROM GENERAL_INFO, DOCTOR_OFFICE WHERE DOCTOR_OFFICE.Office_ID = {office_id} AND DOCTOR_OFFICE.Doctor_ID = GENERAL_INFO.Hospital_ID")
    qe.connect()
    dr_lname = qe.do_query(query_string)
    qe.disconnect()
    form.pphys_pick.choices=dr_lname
    if not dr_lname:
        flash(f'No Doctor is Working Here Yet, Please Pick Another Location', 'danger')
        return redirect(url_for('patient_reg', pt_username = pt_username))
    else:
        
        if form.next_submit.data:
            phys_id = form.pphys_pick.data
            print(phys_id)
            registerform.insert_patient(pt_username, phys_id)
            flash(f'You Successfully Added a Primary Physician','success')
            return redirect(url_for('insurance', pt_username = pt_username))
        elif form.back.data:
            return redirect(url_for('patient_reg', pt_username = pt_username))
    return render_template("primary_phys_pick.html", form = form)



@app.route("/patient_reg/<pt_username>/insurance", methods = ['GET','POST'])
def insurance(pt_username):
    form = Insurance()
    insur_id = form.insur_id.data
    insur_name = form.insur_name.data
    insur_phone = form.insur_phone.data
    exp_date = form.expir_date.data
    if form.cancel.data:
        flash(f'You Successfully Created Account, Please Log in', 'success')
        return redirect(url_for('home'))
    elif form.submit.data:
        if insur_id == None or insur_name == None or insur_phone == None:
            flash(f'Please Fill All of Them', 'danger')
        elif insur_phone.isdigit() == False:
            flash(f'Please Enter a Valid Phone Number', 'danger')
        elif exp_date < date.today():
            flash(f"The Insurance is Expried. Please User a Valid Insurance")
        else:
            registerform.insert_insur(pt_username, insur_id, insur_name, exp_date, insur_phone)
            flash(f'You Successfully Created Account, Please Log in', 'success')
            return redirect(url_for('home'))
    return render_template('insurance.html', form = form)



'''
STAFF REGISTRATION

'''

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



'''
Doctor REGISTRATION

'''

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


'''
LOG IN 
'''

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.user.data
        password = form.password.data
        if login_check.login_check(username, password) == True:
            if login_check.account_type(username, password) == "patient":
                flash('You Successfully Log in')
                return render_template('Patient_View.html')

            elif login_check.account_type(username, password) == "doctor":
                flash('You Successfully Log in')
                return render_template('doctor.html')
            elif login_check.account_type(username, password) == "staff":
                flash('You Successfully Log in')
                return redirect(url_for('staffPage'))
        else:
            flash('Invalid Account, Check Your Username and Password', 'danger')

    return render_template('login.html', title='Login', form=form)



'''STAFF VIEW'''
@app.route("/staffPage")
def staffPage():
    qe.connect()
    appointmentData = qe.do_query("SELECT A.With_Doctor,A.Patient_ID, A.App_date,A.App_hour FROM appointment AS A;")
    numberedData = []
    for i in range(len(appointmentData)):
        temp = []
        temp.append(i + 1)
        temp += appointmentData[i]
        numberedData.append(temp)
    qe.disconnect()
    return render_template('staffPage.html',data = numberedData)

@app.route("/staffReports")
def staffReports():
    return render_template('staffReports.html')

if __name__ == '__main__':
    app.run(debug=True)
