from flask import Flask, render_template, url_for, flash, redirect, request
from forms import RegistrationForm, LoginForm, StaffForm, DoctorForm, AddLoc, PatientForm, PriPhys, Insurance
from QueryEngine import QueryEngine
from datetime import datetime,date
import pymysql
import appointment
import login_check
import registerform
import forms
import datetime


from flask import jsonify
import csv
from flask_mail import Mail, Message



qe = QueryEngine()
qe.setup_default()

app = Flask(__name__)

app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'


mail= Mail(app)
app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = "uhdatabase2019@gmail.com"
app.config['MAIL_PASSWORD'] = "coscspring2019"
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)



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
                return redirect(url_for('Patient_View',pt_username=username))

            elif login_check.account_type(username, password) == "doctor":
                flash('You Successfully Log in')
                return render_template('doctor.html')
            elif login_check.account_type(username, password) == "staff":
                flash('You Successfully Log in')
                return redirect(url_for('staffPage'))
        else:
            flash('Invalid Account, Check Your Username and Password', 'danger')

    return render_template('login.html', title='Login', form=form)



'''
PATIENT VIEW AFTER LOG IN 
'''
@app.route("/Patient_View/<pt_username>", methods=['GET', 'POST'])
def Patient_View(pt_username):
    qe.connect()
    query_string = (f" SELECT First_Name, Email, Last_Name, Phone_Number,DOB \
                        FROM general_info, log_in \
                        WHERE log_in.User_ID = general_info.Hospital_ID and log_in.UserName = '{pt_username}';")

    result = qe.do_query(query_string);
    first_name = result[0][0]
    email = result[0][1]
    last_name = result[0][2]
    phone = result[0][3]
    dob = result[0][4]
    return render_template('Patient_View.html',
                            first_name =first_name,
                            email = email,
                            last_name = last_name,
                            phone = phone, dob = dob,pt_username = pt_username)


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


# Route to send Email 
@app.route("/SendEmail/<D_Fname>/<D_Email>/<P_Fname>/<P_Email>/<Type>")
def SendEmail(D_Fname,D_Email,P_Fname,P_Email,Type):

    #Patient 
    msg1 = Message("Doctor Appoitment Notification", sender = "uhdatabase2019@gmail.com", recipients = [P_Email])

    #Doctor 
    msg2 = Message("Doctor Appoitment Notification", sender = "uhdatabase2019@gmail.com", recipients = [D_Email])

    if (Type == "cancelled" or Type == "Cancelled"):
        msg1.body = "Hi " + P_Fname + ", Your appointment has been successfully cancelled"
        msg2.body = "Hi " + D_Fname + ", Patient " + P_Fname +  " has cancelled appointment"
    else: 
        msg1.body = "Hello Flask message sent from Flask-Mail"
        msg2.body = "Hello Flask message sent from Flask-Mail"

    mail.send(msg1)
    mail.send(msg2)
    return "Sent"

@app.route("/cancel_Appointment/<app_id>",methods=['GET', 'POST'])
def cancel_appointment(app_id):
    qe.connect()
    query_string = (f"UPDATE appointment SET Appt_Status = 'Cancelled' WHERE Appt_ID = {app_id};")
    qe.do_query(query_string);
    qe.commit()

    #get Fname and Email
    get_info =  (f"SELECT D.Email, D.First_Name, P.Email, P.First_Name\
        FROM appointment AS  A,  general_info  AS P, general_info  AS D\
        WHERE  Appt_ID  = {app_id}  AND A.With_Doctor  =  D.Hospital_ID  AND  A.Patient_ID  =  P.Hospital_ID;")

    result = qe.do_query(get_info);
    doctor_email = result[0][0]
    doctor_fname = result[0][1]
    patient_email = result[0][2]
    patient_fname = result[0][3]

    Type = "cancelled"
    qe.disconnect()

    return redirect(url_for('SendEmail',D_Fname = doctor_fname,D_Email = doctor_email,
        P_Fname = patient_fname,P_Email = patient_email,Type = Type))


'''
APPOINTMENT ROUTE 
'''
@app.route("/pt_View_Current_Appointment/<pt_username>",methods=['GET', 'POST'])
def pt_View_Current_Appointment(pt_username):
    #BOOKED RESULT 
    qe.connect()
    query_string_booked = (f"SELECT App_Type,App_date,App_hour,With_Doctor,Appt_Status, Office_Name, Appt_ID \
        FROM appointment, log_in, office \
        WHERE log_in.UserName = '{pt_username}' \
        AND log_in.User_ID = appointment.Patient_ID \
        AND office.Office_ID =  appointment.App_Location_ID\
        AND appointment.Appt_Status = 'Booked';")

    booked_result = qe.do_query(query_string_booked)
    qe.disconnect()

    #COMPLETED RESULT 
    qe.connect()
    query_string_completed = (f"SELECT App_Type,App_date,App_hour,With_Doctor,Appt_Status, Office_Name, Appt_ID \
        FROM appointment, log_in, office \
        WHERE log_in.UserName = '{pt_username}' \
        AND log_in.User_ID = appointment.Patient_ID \
        AND office.Office_ID =  appointment.App_Location_ID\
        AND appointment.Appt_Status <> 'Booked';")

    completed_result= qe.do_query(query_string_completed)
    qe.disconnect()

    booked_data = []
    completed_data = []

    #Append list 
    for i in booked_result:
        booked_data.append(list(i))
    
    for i in completed_result:
        completed_data.append(list(i))

    for elem in booked_data:
        print(f"current appt is {elem[6]}")
        hour = int(elem[2])
        suffix = 'AM'
        if(hour >= 12):
            suffix = 'PM'
        hour %= 12
        if(hour == 0):
            hour = 12
        elem[2] = str(hour) + ":00 " + suffix

    for elem in completed_data:
        hour = int(elem[2])
        suffix = 'AM'
        if(hour >= 12):
            suffix = 'PM'
        hour %= 12
        if(hour == 0):
            hour = 12
        elem[2] = str(hour) + ":00 " + suffix


    return render_template("pt_View_Current_Appointment.html", 
                            booked_data = booked_data,completed_data=completed_data)


if __name__ == '__main__':
    app.run(debug=True)
