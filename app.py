from flask import Flask, render_template, url_for, flash, redirect, request, make_response
from forms import *
from QueryEngine import QueryEngine
from datetime import datetime,date
import pymysql
import appointment
import login_check
import registerform
import forms
import uuid
import csv
from flask_mail import Mail, Message
from io import StringIO
import csv
import pandas as pd
from Chart import Chart

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

@app.route('/')
@app.route("/about")
def about():
    return render_template('about.html', title='About')


@app.route("/contact")
def contact():
    return render_template('contact.html')


#REGISTERARTION OF PATIENT:

@app.route("/patient_reg/<pt_username>/insurance", methods = ['GET','POST'])
def insurance(pt_username):
    form = Insurance()
    insur_id = form.insur_id.data
    insur_name = form.insur_name.data
    insur_phone = form.insur_phone.data
    exp_date = form.expir_date.data
    if form.cancel.data:
        flash(f'You Successfully Created Account, Please Log in', 'success')
        return redirect(url_for('login'))
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
            return redirect(url_for('login'))
    return render_template('insurance.html', form = form)

@app.route("/patient_reg/<pt_username>/<office>", methods = ['GET','POST'])
def primary_phys_pick(office, pt_username):
    form = PriPhys()
    query_string = (f"SELECT Office_ID FROM office WHERE Office_Name = '{office}'")
    qe.connect()
    office_id = qe.do_query(query_string)
    qe.disconnect()
    office_id = office_id[0][0]
    #print(office_id)
    query_string = (f"SELECT Hospital_ID, Last_Name FROM general_info, doctor_office WHERE doctor_office.Office_ID = {office_id} AND doctor_office.Doctor_ID = general_info.Hospital_ID")
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
            #print(phys_id)
            registerform.insert_patient(pt_username, phys_id)
            flash(f'You Successfully Added a Primary Physician','success')
            return redirect(url_for('insurance', pt_username = pt_username))
        elif form.back.data:
            return redirect(url_for('patient_reg', pt_username = pt_username))
    return render_template("primary_phys_pick.html", form = form)

@app.route("/patient_reg/<pt_username>", methods = ['GET','POST'])
def patient_reg(pt_username):
    form = PatientForm()
    if form.validate_on_submit():
        location = form.officelocation.data
        return redirect(url_for('primary_phys_pick',office = location, pt_username = pt_username))
    return render_template('patient_reg.html', form = form)

######## END PATIENT REGISTERATION #########

# REGISTERATION OF STAFF #
@app.route("/admin_reg/staff_reg/<st_username>", methods = ['GET','POST'])
def staff_reg(st_username):
    form = StaffForm()
    if form.validate_on_submit():
        office_loc = form.officelocation.data
        work_date = form.work_date.data
        #print (office_loc)
        #print(work_date)
        registerform.insert_staff(st_username, office_loc, work_date)
        flash(f'Account is Registerd, Please Log in!', 'success')
        return redirect(url_for('login'))
    return render_template('staff_reg.html', form = form)

###### END STAFF REGISTERATION #####

# REGISTERATION OF DOCTOR #

@app.route("/admin_reg/doc_reg/<dr_username>/add_loc", methods = ['GET','POST'])
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
                return redirect(url_for('login'))
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
            return redirect(url_for('login'))
    else:
        if form.cancel.data:
            flash(f'Account is Registerd, Please Log in!', 'success')
            return redirect(url_for('login'))
    return render_template('add_loc.html', form = form)

@app.route("/admin_reg/doc_reg/<dr_username>", methods = ['GET','POST'])
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
            return redirect(url_for('login'))
        elif form.add_loc.data:
            registerform.insert_doc(dr_username, office_loc, work_date, spec)
            return redirect(url_for('add_loc',dr_username = dr_username))
    return render_template('doc_reg.html', form = form)

##### END DOCTOR REGISTERATION ######

# GENERAL INFO SIGN UP #
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
            return redirect(url_for('patient_reg', pt_username = username))
    return render_template('register.html', title='Register', form=form)


###### END GENERAL INFO SIGN UP #######



'''
_________________________________________________________________________________________________
            
                        LOG IN 
_________________________________________________________________________________________________
'''

@app.route("/login", methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.user.data
        password = form.password.data
        if login_check.login_check(username, password) == True:

            if login_check.account_type(username, password) == "patient":
                # flash(f'You Successfully Log in','success')
                return redirect(url_for('Patient_View',pt_username = username))

            elif login_check.account_type(username, password) == "doctor":
                # flash(f'You Successfully Log in','success')
                return redirect(url_for('Doctor_View',dt_username = username))

            elif login_check.account_type(username, password) == "staff":
                # flash(f'You Successfully Log in','success')
                return redirect(url_for('Staff_View',st_username = username))
            elif login_check.account_type(username, password) == "admin":
                return redirect(url_for("Admin_View", ad_username = username))
        else:
            flash('Invalid Account, Check Your Username and Password', 'danger')

    return render_template('login.html', title='Login', form=form)

'''
_________________________________________________________________________________________________
            
                        DOCTOR - DOCTOR - SECTION HERE. 
_________________________________________________________________________________________________
'''
@app.route("/Doctor_View/<dt_username>", methods=['GET', 'POST'])
def Doctor_View(dt_username):
    qe.connect()
    query_string = (f"SELECT First_Name, Email, Last_Name, Phone_Number,DOB \
                        FROM general_info, log_in \
                        WHERE log_in.User_ID = general_info.Hospital_ID and log_in.UserName = '{dt_username}';")

    result = qe.do_query(query_string)
    first_name = result[0][0]
    email = result[0][1]
    last_name = result[0][2]
    phone = result[0][3]
    dob = result[0][4]
    return render_template('Doctor_View.html',
                            first_name =first_name,
                            email = email,
                            last_name = last_name,
                            phone = phone, dob = dob,dt_username = dt_username)


'''
_________________________________________________________________________________________________
            
                        DOCTOR - VIEW TODAY  APPONTMENT
_________________________________________________________________________________________________
'''
@app.route("/doc_today_appointment/<dt_username>",methods=['GET', 'POST'])
def doc_today_appointment(dt_username):

    qe.connect()
    query_string = (f"SELECT Appt_ID,App_date,App_hour,First_Name,Office_Name,Appt_Status \
        FROM appointment, office,log_in,general_info \
        WHERE log_in.UserName = '{dt_username}' AND office.Office_ID = appointment.App_Location_ID \
        AND log_in.User_ID = appointment.With_Doctor \
        AND DATE(appointment.App_date) = CURDATE()\
        AND appointment.Patient_ID = general_info.Hospital_ID;")

    result = qe.do_query(query_string)
    qe.disconnect()
    print(result)

    data = []
    for i in result:
        data.append(list(i))

    for elem in data:
        hour = int(elem[2])
        suffix = 'AM'
        if(hour >= 12):
            suffix = 'PM'
        hour %= 12
        if(hour == 0):
            hour = 12
        elem[2] = str(hour) + ":00 " + suffix
    
    if (request.method == "POST"):
        data = request.form
        if ("view" in data):
            appt_id = data["view"]
            return redirect(url_for('PtHealthProfile', appt_id = appt_id, dt_username = dt_username))

    return render_template("doc_today_appointment.html",
                            data = data, dt_username=dt_username)

@app.route("/doc_today_appointment/<dt_username>/<appt_id>",methods = ['GET','POST'])
def PtHealthProfile(dt_username, appt_id):
    query_string = f"SELECT H.BloodType, H.Height, H.Weight, H.Health_Summary FROM health_profile AS H, appointment AS A WHERE A.Appt_ID = {appt_id} AND A.Patient_ID = H.Health_Profile_ID"
    qe.connect()
    health_profile = qe.do_query(query_string)
    qe.disconnect()
    if (request.method == "POST"):
        data = request.form
        if ("back" in data):
            return redirect(url_for("doc_today_appointment", dt_username = dt_username))
    return render_template("PtHealthProfile.html",dt_username = dt_username, hprofile = health_profile)

@app.route("/Doctor_View/<dt_username>/specialistApproval",methods=['GET','POST'])
def specialistApproval(dt_username):
    qe.connect()
    doctorID = qe.do_query(f"SELECT User_ID FROM log_in WHERE UserName = '{dt_username}';")
    doctorID = doctorID[0][0]
    qe.disconnect()
    qe.connect()
    patientData = qe.do_query(f"SELECT S.Requested_ID,S.Requested_Date,P.First_Name,P.Last_Name,P.DOB,S.Requested_Reason,P.Phone_Number FROM general_info AS P, specialistrequest AS S WHERE S.Patient_ID = P.Hospital_ID AND S.Doctor_ID = {doctorID} AND S.Requested_Status = 'Pending';")
    qe.disconnect()
    requestedData = []
    for i in range(len(patientData)):
        temp = []
        temp.append(i + 1)
        temp += patientData[i]
        requestedData.append(temp)
    if(request.method == "POST"):
        data = request.form
        if("approveButton" in data):
            requestedID = data["approveButton"]
            qe.connect()
            patientID = qe.do_query(f"SELECT Patient_ID FROM specialistrequest WHERE Requested_ID = {requestedID};")
            patientID = patientID[0][0]
            qe.disconnect()
            qe.disconnect()
            qe.connect()
            approvedQuery = qe.do_query(f"UPDATE specialistrequest SET Requested_Status = 'Approved' WHERE Requested_ID = {requestedID};")
            qe.commit()
            qe.disconnect()
            qe.connect()
            specialistQuery = qe.do_query(f"UPDATE patient SET Approval_Status = 1 WHERE Patient_ID = {patientID};")
            qe.commit()
            qe.disconnect()
            qe.connect()
            doctorID = qe.do_query(f"SELECT User_ID FROM log_in WHERE UserName = '{dt_username}';")
            doctorID = doctorID[0][0]
            qe.disconnect()
            qe.connect()
            patientData = qe.do_query(f"SELECT S.Requested_ID,S.Requested_Date,P.First_Name,P.Last_Name,P.DOB,S.Requested_Reason,P.Phone_Number FROM general_info AS P, specialistrequest AS S WHERE S.Patient_ID = P.Hospital_ID AND S.Doctor_ID = {doctorID} AND S.Requested_Status = 'Pending';")
            qe.disconnect()
            requestedData = []
            for i in range(len(patientData)):
                temp = []
                temp.append(i + 1)
                temp += patientData[i]
                requestedData.append(temp)
            flash(f"Permission Granted Successfully",'success')
            return render_template("specialistApproval.html",dt_username = dt_username,data = requestedData)
        if("denyButton" in data):
            requestedID = data["denyButton"]
            qe.connect()
            patientID = qe.do_query(f"SELECT Patient_ID FROM specialistrequest WHERE Requested_ID = {requestedID};")
            patientID = patientID[0][0]
            qe.disconnect()
            qe.connect()
            denyQuery = qe.do_query(f"UPDATE specialistrequest SET Requested_Status = 'Denied' WHERE Requested_ID = {requestedID};")
            qe.commit()
            qe.disconnect()
            qe.connect()
            specialistQuery = qe.do_query(f"UPDATE patient SET Approval_Status = 0 WHERE Patient_ID = {patientID};")
            qe.commit()
            qe.disconnect()
            qe.connect()
            doctorID = qe.do_query(f"SELECT User_ID FROM log_in WHERE UserName = '{dt_username}';")
            doctorID = doctorID[0][0]
            qe.disconnect()
            qe.connect()
            patientData = qe.do_query(f"SELECT S.Requested_ID,S.Requested_Date,P.First_Name,P.Last_Name,P.DOB,S.Requested_Reason,P.Phone_Number FROM general_info AS P, specialistrequest AS S WHERE S.Patient_ID = P.Hospital_ID AND S.Doctor_ID = {doctorID} AND S.Requested_Status = 'Pending';")
            qe.disconnect()
            requestedData = []
            for i in range(len(patientData)):
                temp = []
                temp.append(i + 1)
                temp += patientData[i]
                requestedData.append(temp)
            flash(f"Permission Denied",'danger')
            return render_template("specialistApproval.html",dt_username = dt_username,data = requestedData)
    return render_template("specialistApproval.html",dt_username = dt_username,data = requestedData)


'''
_________________________________________________________________________________________________
            
                        STAFF - STAFF - STAFF SECTION HERE. 
_________________________________________________________________________________________________
'''
@app.route("/report1/<st_username>", methods=['GET', 'POST'])
def Staff_Report1(st_username):
  charts = []
  
  date_cur = date.today()
  ord_past = date_cur.toordinal() - 7
  date_past = date.fromordinal(ord_past)
  
  qe.connect()
  query1 = f'''
    Select
    count(App_date),A.App_date
    from
    appointment as A, log_in as L, staff as S
    WHERE L.UserName = '{st_username}' AND S.Staff_ID = L.User_ID AND A.App_Location_ID = S.Office_Location_ID AND A.Appt_Status != 'Cancelled' AND ('{str(date_past)}' <= A.App_date AND A.App_date <= '{str(date_cur)}') 
    GROUP BY
    App_date
  '''
  
  query2 = f'''
    Select
    P.Balance_Due, A.App_date
    from
    appointment as A, log_in as L, staff as S, post_appointment as P
    WHERE L.UserName = '{st_username}' AND S.Staff_ID = L.User_ID AND A.App_Location_ID = S.Office_Location_ID AND A.Appt_Status != 'Cancelled' AND P.Appointment_ID = A.Appt_ID AND ('{str(date_past)}' <= A.App_date AND A.App_date <= '{str(date_cur)}') 
    GROUP BY
    App_date
  '''
  
  results1 = qe.do_query(query1)
  results2 = qe.do_query(query2)
  qe.disconnect()
  
  # Chart 1
  chartActivity = Chart("Appointments in Past Week", "bar", "Appointment Count")
  table1 = {}
  for i in range(-7,1):
    day = date.today().toordinal() + i
    table1[date.fromordinal(day)] = 0  
  for elem in results1:
    table1[elem[1]] = elem[0]
  for k,v in table1.items():
    chartActivity.insert(k, v)
  
  charts.append(chartActivity)
  
  # Chart 2
  chartBalance = Chart("Balances Due in Past Week", "bar", "Balance")
  table2 = {}
  for i in range(-7,1):
    day = date.today().toordinal() + i
    table2[date.fromordinal(day)] = 0  
  for elem in results2:
    table2[elem[1]] = elem[0]
  for k,v in table2.items():
    chartBalance.insert(k, v)
  charts.append(chartBalance)
  
  return render_template("staffReport1.html", charts_len = len(charts), charts = charts, st_username = st_username)

@app.route("/Staff_View/<st_username>", methods=['GET', 'POST'])
def Staff_View(st_username):
    qe.connect()
    query_string = (f" SELECT First_Name, Email, Last_Name, Phone_Number,DOB \
                        FROM general_info, log_in \
                        WHERE log_in.User_ID = general_info.Hospital_ID and log_in.UserName = '{st_username}';")

    result = qe.do_query(query_string)
    first_name = result[0][0]
    email = result[0][1]
    last_name = result[0][2]
    phone = result[0][3]
    dob = result[0][4]
    return render_template('Staff_View.html',
                            first_name =first_name,
                            email = email,
                            last_name = last_name,
                            phone = phone, dob = dob,st_username = st_username)

##### STAFF PAGE #####
@app.route("/staffPage/<st_username>/staffPost/<appt_id>",methods = ['GET','POST'])
def staffPost(st_username, appt_id):
    form = StaffPostForm()
    if (form.validate_on_submit()):
        if (form.submit.data):
            #print(appt_id)
            diagnosis = form.doctorDiagnosis.data
            balance = form.balance.data
            insert_string = f"INSERT INTO POST_APPOINTMENT(Appointment_ID, Doctor_Diagnosis, Balance_Due) VALUE({appt_id},'{diagnosis}',{balance})"
            #print(insert_string)
            qe.connect()
            qe.do_query(insert_string)
            qe.commit()
            qe.disconnect()
            #print(diagnosis)
            #print(balance)
            blood_prescript = form.blood_prescript.data
            #print(blood_prescript)
            blood = 'Fb'
            prescript = 'Fp'
            for elem in blood_prescript:
                if elem == 'Tp':
                    prescript = 'Tp'
                if elem == 'Tb':
                    blood = 'Tb'
            #print(blood, prescript)
            if blood =='Tb' and prescript == 'Fp':
                return redirect(url_for('staffPostBlood',st_username = st_username, appt_id = appt_id))
            elif prescript == 'Tp':
                return redirect(url_for('staffPostPrescript', st_username = st_username, appt_id = appt_id, blood = blood))
            elif blood == 'Fb' and prescript == 'Fp':
                update_string = f"UPDATE APPOINTMENT SET Appt_Status = 'Completed' WHERE Appt_ID = {appt_id}"
                qe.connect()
                qe.do_query(update_string)
                qe.commit()
                qe.disconnect()
                return redirect(url_for('staffPage', st_username = st_username))

    return  render_template('staffPost.html', form = form, st_username = st_username)

@app.route("/staffPage/<st_username>/staffPost/<appt_id>/blood_test", methods = ['GET','POST'])
def staffPostBlood(st_username, appt_id):
    form = PostBlood()
    if form.validate_on_submit():
        white_blood = form.white_blood.data
        red_blood = form.red_blood.data
        hemoglobin = form.hemoglobin.data
        hematocrit = form.hematocrit.data
        mcv = form.mcv.data
        mch = form.mch.data
        rdw = form.rdw.data
        platelet = form.platelet.data
        lymphocyte = form.lymphocyte.data
        monocyte = form.monocyte.data
        cholesterol = form.cholesterol.data
        iron = form.iron.data
        sodium = form.sodium.data
        potassium = form.potassium.data
        if form.submit.data:
            insert_string = f"INSERT INTO blood_test_result(White_blood_Cell_Count, Red_blood_Cell_Count, Hemoglobin, Hematocrit, MCV, MCH, RDW, Platelet_Count, Lymphocyte, Monocyte, Cholesterol, Iron, Sodium, Potassium, Appt_ID) VALUE({white_blood},{red_blood},{hemoglobin},{hematocrit},{mcv},{mch},{rdw},{platelet},{lymphocyte},{monocyte},{cholesterol},{iron},{sodium},{potassium},{appt_id})"
            qe.connect()
            qe.do_query(insert_string)
            qe.commit()
            qe.disconnect()
            query_string = f"SELECT Blood_test_id FROM blood_test_result WHERE Appt_ID = {appt_id}"
            qe.connect()
            blood_id = qe.do_query(query_string)[0][0]
            qe.disconnect()
            update_string = f"UPDATE post_appointment SET Blood_Test_ID = {blood_id} WHERE Appointment_ID = {appt_id}"
            qe.connect()
            qe.do_query(update_string)
            qe.commit()
            qe.disconnect()
            update_string = f"UPDATE appointment SET Appt_Status = 'Completed' WHERE Appt_ID = {appt_id}"
            qe.connect()
            qe.do_query(update_string)
            qe.commit()
            qe.disconnect()
            return redirect(url_for('staffPage',st_username = st_username))
        
    return render_template('staffPostBlood.html', form = form)

@app.route("/staffPage/<st_username>/staffPost/<appt_id>/<blood>/prescription", methods = ['GET','POST'])
def staffPostPrescript(st_username, appt_id, blood):
    form = PostPrescript()
    bl = False
    if blood == 'Tb':
        bl = True
    if form.validate_on_submit():
        drug = form.drug.data
        usage = form.usage.data
        numfill = form.numfill.data

        if form.submit.data:
            query_string = f"SELECT With_Doctor, Patient_ID FROM appointment WHERE Appt_ID = {appt_id}"
            qe.connect()
            ppl = qe.do_query(query_string)
            dr_id = ppl[0][0]
            pt_id = ppl[0][1]
            qe.disconnect()
            insert_string = f"INSERT INTO prescription(Drug_Name, Assigned_By, Usage_Note, Num_Refill, Patient_ID, Appt_ID) VALUE('{drug}',{dr_id},'{usage}',{numfill},{pt_id},{appt_id})"
            qe.connect()
            qe.do_query(insert_string)
            qe.commit()
            qe.disconnect()
            query_string = f"SELECT Prescription_ID FROM prescription WHERE Appt_ID = {appt_id}"
            qe.connect()
            prescript_id = qe.do_query(query_string)[0][0]
            qe.disconnect()
            update_string = f"UPDATE post_appointment SET Prescription_ID = {prescript_id} WHERE Appointment_ID = {appt_id}"
            qe.connect()
            qe.do_query(update_string)
            qe.commit()
            qe.disconnect()
            update_string = f"UPDATE appointment SET Appt_Status = 'Completed' WHERE Appt_ID = {appt_id}"
            qe.connect()
            qe.do_query(update_string)
            qe.commit()
            qe.disconnect()
            return redirect(url_for('staffPage',st_username = st_username))
        if form.next_submit.data:
            query_string = f"SELECT With_Doctor, Patient_ID FROM appointment WHERE Appt_ID = {appt_id}"
            qe.connect()
            ppl = qe.do_query(query_string)
            dr_id = ppl[0][0]
            pt_id = ppl[0][1]
            qe.disconnect()
            insert_string = f"INSERT INTO prescription(Drug_Name, Assigned_By, Usage_Note, Num_Refill, Patient_ID, Appt_ID) VALUE('{drug}',{dr_id},'{usage}',{numfill},{pt_id},{appt_id})"
            qe.connect()
            qe.do_query(insert_string)
            qe.commit()
            qe.disconnect()
            query_string = f"SELECT Prescription_ID FROM prescription WHERE Appt_ID = {appt_id}"
            qe.connect()
            prescript_id = qe.do_query(query_string)[0][0]
            qe.disconnect()
            update_string = f"UPDATE post_appointment SET Prescription_ID = {prescript_id} WHERE Appointment_ID = {appt_id}"
            qe.connect()
            qe.do_query(update_string)
            qe.commit()
            qe.disconnect()
            return redirect(url_for('staffPostBlood',st_username = st_username, appt_id = appt_id))

    return render_template('staffPostPrescript.html', form = form, bl = bl)

@app.route("/staffPage/<st_username>/confirm/<appt_id>", methods = ['GET','POST'])
def staffConfirm(st_username, appt_id):
    all_blood_type = ['A+','A-','B+','B-','AB+','AB-','O-','O+']
    form = StaffPostHealthProfile()
    qe.connect()
    staffID = qe.do_query(f"SELECT User_ID FROM log_in WHERE UserName = '{st_username}';")
    staffID = staffID[0][0]
    qe.disconnect()
    blood_typeExist = True
    health_query = f"SELECT H.BloodType FROM health_profile AS H, appointment AS A WHERE A.Appt_ID = {appt_id} AND H.Health_Profile_ID = A.Patient_ID"
    pt_string = f"SELECT Patient_ID FROM appointment WHERE Appt_ID = {appt_id}"
    qe.connect()
    blood = qe.do_query(health_query)[0][0]
    pt_id = qe.do_query(pt_string)[0][0]
    qe.disconnect()
    if blood is None:
        blood_typeExist = False
    else:
        blood_typeExist = True 
    if blood_typeExist == False and form.validate_on_submit():
        blood_type = form.bloodtype.data
        health_summary = form.health_summary.data
        height = form.height.data
        weight = form.weigth.data
        correct_blood = False
        for elem in all_blood_type:
            if blood_type == elem:
                correct_blood = True
        if correct_blood == False:
            flash(f'Incorrect Blood Type', 'danger')
        else:
            update_string = f"UPDATE health_profile SET BloodType = '{blood_type}', Health_Summary = '{health_summary}',Height = {height},Weight={weight} WHERE Health_Profile_ID = {pt_id}"
            qe.connect()
            qe.do_query(update_string)
            qe.commit()
            update_string = f"UPDATE appointment SET Confirm_By = {staffID}  WHERE Appt_ID = {appt_id}"
            qe.do_query(update_string)
            qe.commit()
            qe.disconnect()
            
            
            flash(f'Successfully Confirmed', 'success')
            return redirect(url_for('staffPage', st_username = st_username))
    elif blood_typeExist == True and form.validate_on_submit():
        health_summary = form.health_summary.data
        height = form.height.data
        weight = form.weigth.data
        update_string = f"UPDATE health_profile SET Health_Summary = '{health_summary}',Height = {height},Weight={weight} WHERE Health_Profile_ID = {pt_id}"
        qe.connect()
        qe.do_query(update_string)
        qe.commit()
        update_string = f"UPDATE appointment SET Confirm_By = {staffID} WHERE Appt_ID = {appt_id}"
        qe.do_query(update_string)
        qe.commit()
        qe.disconnect()
        
        flash(f'Patient is checked in for today appointment', 'success')
        return redirect(url_for('staffPage', st_username = st_username))

    return render_template('staffConfirm.html', form = form, st_username = st_username,blood_typeExist = blood_typeExist, blood = blood )



@app.route("/staffPage/<st_username>/staffReports",methods = ['GET','POST'])
def staffReports(st_username):
    return render_template('staffReports.html', st_username = st_username)





@app.route("/staffPage/<st_username>/staffProfile", methods = ['GET','POST'])
def staffProfile(st_username):
    return render_template('staffProfile.html', st_username = st_username)

'''
_________________________________________________________________________________________________
            
                        STAFF PAGE - USED TO VIEW CURRENT LIST OF TODAY APPOTMENT
_________________________________________________________________________________________________
'''

@app.route("/staffPage/<st_username>", methods = ['GET','POST'])
def staffPage(st_username):
    qe.connect()
    staffID = qe.do_query(f"SELECT User_ID FROM log_in WHERE UserName = '{st_username}';")
    staffID = staffID[0][0]
    staffLocation = qe.do_query(f"SELECT Office_Location_ID FROM staff WHERE Staff_ID = {staffID};")
    staffLocation = staffLocation[0][0]
    qe.disconnect()
    qe.connect()
    appointmentData = qe.do_query(f"SELECT A.Appt_ID, A.Confirm_By,D.Last_Name,P.Last_Name, A.App_date,A.App_hour,Appt_Status FROM general_info AS D, general_info AS P,appointment AS A \
                                        WHERE App_Location_ID = {staffLocation} \
                                        AND D.Hospital_ID = A.With_Doctor AND P.Hospital_ID = A.Patient_ID  \
                                        AND A.App_date = CURDATE() \
                                        AND (Appt_Status = 'Booked' OR Appt_Status = 'Process');")
    qe.disconnect()
    numberedData = []
    for i in range(len(appointmentData)):
        temp = []
        temp.append(i + 1)
        temp += appointmentData[i]
        numberedData.append(temp)
    for elem in numberedData:
        hour = int(elem[6])
        suffix = 'AM'
        if(hour >= 12):
            suffix = 'PM'
        hour %= 12
        if(hour == 0):
            hour = 12
        elem[6] = str(hour) + ":00 " + suffix
    if(request.method == "POST"):
        data = request.form
        if("selectRow" in data):
            appt_id = data["selectRow"]
            qe.disconnect()
            qe.connect()
            status = qe.do_query(f"SELECT Appt_Status FROM appointment WHERE Appt_ID = {appt_id};")
            status = status[0][0]
            qe.disconnect()
            if (status == "Booked"):
                flash('You Cannot Modify, The Appointment is Not in Process','danger')
            elif (status == 'Process'):
                return redirect(url_for('staffPost', st_username = st_username, appt_id = appt_id))
        if ("confirm" in data):
            appt_id = data["confirm"]
            return redirect(url_for('staffConfirm', st_username = st_username, appt_id = appt_id))
    return render_template('staffPage.html',data = numberedData, st_username = st_username)


@app.route("/staffApptSearch/<st_username>",methods = ['GET','POST'])
def staffApptSearch(st_username):
    form = AptSearch()
    
    if form.submit.data:
        date_search = form.date_search.data
        if date_search != None:
            return redirect(url_for('staffAptSearchResult',st_username = st_username, date_search = date_search))
        else:
            flash(f"Enter a date",'danger')
    return render_template("staffApptSearch.html",form = form, st_username = st_username)



@app.route("/staffApptSearch/<st_username>/<date_search>",methods = ['GET','POST'])
def staffAptSearchResult(st_username, date_search):
    date_search = str(date_search)
    qe.connect()
    staffID = qe.do_query(f"SELECT User_ID FROM log_in WHERE UserName = '{st_username}';")
    staffID = staffID[0][0]
    staffLocation = qe.do_query(f"SELECT Office_Location_ID FROM staff WHERE Staff_ID = {staffID};")
    staffLocation = staffLocation[0][0]
    qe.disconnect()
    qe.connect()
    appointmentData = qe.do_query(f"SELECT A.Appt_ID, A.Confirm_By,D.Last_Name,P.Last_Name, A.App_date,A.App_hour,Appt_Status FROM general_info AS D, general_info AS P,appointment AS A WHERE App_Location_ID = {staffLocation} AND D.Hospital_ID = A.With_Doctor AND P.Hospital_ID = A.Patient_ID  AND A.App_date = '{date_search}' AND (Appt_Status = 'Booked' OR Appt_Status = 'Process');")
    qe.disconnect()
    numberedData = []
    for i in range(len(appointmentData)):
        temp = []
        temp.append(i + 1)
        temp += appointmentData[i]
        numberedData.append(temp)
    for elem in numberedData:
        hour = int(elem[6])
        suffix = 'AM'
        if(hour >= 12):
            suffix = 'PM'
        hour %= 12
        if(hour == 0):
            hour = 12
        elem[6] = str(hour) + ":00 " + suffix
    if(request.method == "POST"):
        data = request.form
        if("selectRow" in data):
            appt_id = data["selectRow"]
            qe.disconnect()
            qe.connect()
            status = qe.do_query(f"SELECT Appt_Status FROM appointment WHERE Appt_ID = {appt_id};")
            status = status[0][0]
            qe.disconnect()
            if (status == "Booked"):
                flash('You Cannot Modify, The Appointment is Not in Process','danger')
            elif (status == 'Process'):
                return redirect(url_for('staffPost', st_username = st_username, appt_id = appt_id))
        if ("confirm" in data):
            appt_id = data["confirm"]
            return redirect(url_for('staffConfirm', st_username = st_username, appt_id = appt_id))
    return render_template('staffPage.html',data = numberedData, st_username = st_username)

@app.route("/requestedSpecialist/<pt_username>", methods = ['GET','POST'])
def requestedSpecialist(pt_username):
    form = requesteSpecialistForm()
    qe.connect()
    patientID = qe.do_query(f"SELECT User_ID FROM log_in WHERE UserName = '{pt_username}';")
    patientID = patientID[0][0]
    qe.disconnect()
    qe.connect()
    requestedPendingData = qe.do_query(f"SELECT S.Requested_Date,S.Requested_Reason,S.Requested_Status FROM specialistrequest AS S WHERE Patient_ID = {patientID} AND S.Requested_Status = 'Pending';")
    qe.disconnect()
    qe.connect()
    requestedOldData = qe.do_query(f"SELECT S.Requested_Date,S.Requested_Reason,S.Requested_Status FROM specialistrequest AS S WHERE Patient_ID = {patientID} AND S.Requested_Status != 'Pending';")
    qe.disconnect()
    pendingData = []
    for i in range(len(requestedPendingData)):
        temp = []
        temp.append(i + 1)
        temp += requestedPendingData[i]
        pendingData.append(temp)
    oldData = []
    for i in range(len(requestedOldData)):
        temp = []
        temp.append(i + 1)
        temp += requestedOldData[i]
        oldData.append(temp)
    if (form.submit.data):
        reasonData = form.reason.data
        qe.connect()
        patient_ID = qe.do_query(f"SELECT User_ID FROM log_in WHERE UserName = '{pt_username}';")
        patient_ID = patient_ID[0][0]
        qe.disconnect()
        qe.connect()
        query_string = (f"SELECT Patient_ID FROM specialistrequest WHERE Patient_ID={patientID} AND Requested_Status='Pending';")
        requestedPendingData = len(qe.do_query(query_string))
        qe.disconnect()
        if(requestedPendingData >= 1):
            flash(f'Already Requested Specialist', 'danger')
            return render_template('requestedSpecialist.html', form = form, pt_username = pt_username, pendingData = pendingData, oldData = oldData)
        
        qe.connect()
        primaryID = qe.do_query(f"SELECT P.Primary_physician_ID FROM patient AS P WHERE P.Patient_ID = {patientID};")
        qe.disconnect()
        primaryID = primaryID[0][0]
        qe.connect()
        qe.do_query(f"INSERT INTO specialistrequest VALUES(NULL,{primaryID},{patientID},'Pending',NOW(),'{reasonData}');")
        qe.commit()
        qe.disconnect()
        qe.connect()
        qe.connect()
        requestedPendingData = qe.do_query(f"SELECT S.Requested_Date,S.Requested_Reason,S.Requested_Status FROM specialistrequest AS S WHERE Patient_ID = '{patientID}' AND S.Requested_Status = 'Pending';")
        qe.disconnect()
        qe.connect()
        requestedOldData = qe.do_query(f"SELECT S.Requested_Date,S.Requested_Reason,S.Requested_Status FROM specialistrequest AS S WHERE Patient_ID = '{patientID}' AND S.Requested_Status != 'Pending';")
        qe.disconnect()
        pendingData = []
        for i in range(len(requestedPendingData)):
            temp = []
            temp.append(i + 1)
            temp += requestedPendingData[i]
            pendingData.append(temp)
        oldData = []
        for i in range(len(requestedOldData)):
            temp = []
            temp.append(i + 1)
            temp += requestedOldData[i]
            oldData.append(temp)
        flash(f'Successfully Requested Specialist', 'success')
    return render_template('requestedSpecialist.html', form = form, pt_username = pt_username, pendingData = pendingData, oldData = oldData)

'''
_________________________________________________________________________________________________
            
                    PATIENT - BLOOD TEST RESULT DOWNLOAD FILE
_________________________________________________________________________________________________
'''

@app.route("/<pt_username>/post_appointment/<appt_id>", methods = ['GET','POST'])
def patientPostAppt(pt_username, appt_id):

    blood_test = True
    prescript = True
    post_string = f"SELECT Doctor_Diagnosis, Balance_Due, Blood_Test_ID, Prescription_ID FROM post_appointment WHERE Appointment_ID = {appt_id}"
    qe.connect()
    all_post = qe.do_query(post_string)[0]
    qe.disconnect()

    if all_post[2] is None:
        blood_test = False
    if all_post[3] is None:
        prescript = False

    blood_result = []
    if blood_test == True:
        qe.connect()
        blood_test_query = f"SELECT Blood_test_id FROM blood_test_result WHERE Appt_ID = {appt_id}"
        blood_result = qe.do_query(blood_test_query)[0][0]
        print(blood_result)
        qe.disconnect()

    prescript_result = []
    if prescript == True:
        qe.connect()
        prescript_query = f"SELECT Prescription_ID, Drug_Name, Usage_Note, Num_Refill, Patient_ID FROM prescription WHERE Appt_ID = {appt_id}"
        prescript_result = qe.do_query(prescript_query)[0]
        qe.disconnect()

    if (request.method == "POST"):
      data = request.form
      if ("download" in data):
        return redirect(url_for("BloodTest",bl_id = blood_result, pt_username = pt_username))
            
      if ("request" in data):
        refill_query = f"UPDATE PRESCRIPTION SET Num_Refill = Num_Refill - 1 WHERE Prescription_ID = {prescript_result[0]}"
        qe.connect()
        qe.do_query(refill_query)
        qe.commit()
        qe.disconnect()
        flash(f'You have Ordered a Refill','success')
        return redirect(url_for('patientPostAppt',pt_username = pt_username, appt_id = appt_id))

    return render_template('patientPostAppt.html', pt_username = pt_username, blood_test = blood_test, prescript = prescript, prescript_result = prescript_result, all_post = all_post)

@app.route("/BloodTest/<pt_username>/<bl_id>", methods = ['GET','POST'])
def BloodTest(pt_username, bl_id):
	qe.connect()
	appointmentData = qe.do_query(f"SELECT White_blood_Cell_Count, Red_blood_Cell_Count, Hemoglobin,Hematocrit, MCV, MCH, RDW, Platelet_Count, Lymphocyte, Monocyte, Cholesterol, Iron, Sodium, Potassium FROM blood_test_result where blood_test_result.Blood_test_id = {bl_id} ;")
	qe.disconnect()
	column_names = ['White blood Cell Count', 'Red blood Cell Count', 'Hemoglobin','Hematocrit', 'MCV', 'MCH', 'RDW','Platelet Count', 'Lymphocyte', 'Monocyte', 'Cholesterol', 'Iron', 'Sodium', 'Potassium']
	si = StringIO()
	cw = csv.writer(si)
	cw.writerow(column_names)
	cw.writerows(appointmentData)
	output = make_response(si.getvalue())
	output.headers["Content-disposition"] = "attachment; filename = export.csv"
	output.headers["Content-type"] = "text/csv"
	return output

'''
_________________________________________________________________________________________________
            
                        VIEW HEALTH PROFILE
_________________________________________________________________________________________________

'''
@app.route("/Patient_Health_Profile/<pt_username>",methods=['GET', 'POST'])
def Patient_Health_Profile(pt_username):
    qe.connect()
    query_string = (f"SELECT BloodType,Height,Weight,Health_Summary \
        FROM health_profile, log_in\
        WHERE log_in.UserName = '{pt_username}' \
        AND log_in.User_ID=health_profile.Health_Profile_ID;")

    result = qe.do_query(query_string)
    qe.disconnect()
    data =[]

    for i in result:
        data.append(list(i))

    return render_template('pt_Health_Profile.html',pt_username=pt_username,data = data)

'''
_________________________________________________________________________________________________
            
                    PATIENT - PATIENT - PATIENT -PATIENT SECTION 

                        PATIENT MAIN PAGE AFTER LOG IN
_________________________________________________________________________________________________
'''
@app.route("/Patient_View/<pt_username>", methods=['GET', 'POST'])
def Patient_View(pt_username):
    qe.connect()
    query_string = (f" SELECT First_Name, Email, Last_Name, Phone_Number,DOB \
                        FROM general_info, log_in \
                        WHERE log_in.User_ID = general_info.Hospital_ID and log_in.UserName = '{pt_username}';")

    result = qe.do_query(query_string)
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


'''
_________________________________________________________________________________________________
            
                    MAKE APPOINTMENT
_________________________________________________________________________________________________
'''

@app.route("/makeAppointment/<pt_username>", methods = ['GET', 'POST'])
def makeAppointment(pt_username):
    qe.disconnect()
    qe.connect()
    query_patient = f"SELECT User_ID FROM log_in WHERE UserName = '{pt_username}'"
    pt_id = qe.do_query(query_patient)[0][0]
    query_approval = f"SELECT Approval_Status FROM patient WHERE Patient_ID = {pt_id}"
    approval = qe.do_query(query_approval)[0][0]
    approval = (approval == 'T')
    query_doctor = f"SELECT P.Primary_physician_ID, G.Last_Name FROM patient AS P, GENERAL_INFO AS G WHERE P.Patient_ID = {pt_id} AND P.Primary_Physician_ID = G.Hospital_ID"
    doctor = qe.do_query(query_doctor)[0]
    qe.disconnect()
    form = ApptDoctor()
    if(form.submitSpecialist.data):
        return redirect(url_for("specialistType", pt_username = pt_username))
    elif form.submitDoctor.data:
        qe.connect()
        query_string = (f"SELECT P.Primary_physician_ID FROM patient AS P, LOG_IN as L WHERE P.Patient_ID = L.User_ID AND L.UserName = '{pt_username}'")
        dr_id = qe.do_query(query_string)[0][0]
        qe.disconnect()
        return redirect(url_for('appointmentloc', pt_username = pt_username, dr_id = dr_id))

    return render_template('apptDoctor.html', form = form, primary = doctor[1], approval = approval, pt_username = pt_username)



@app.route("/specialistType/<pt_username>", methods = ['GET', 'POST'])
def specialistType(pt_username):
  form = ApptSpecialistType()
  if(form.back.data):
    return redirect(url_for('makeAppointment', pt_username = pt_username))
  elif(form.submit.data):
    return redirect(url_for("chooseSpecialist", pt_username = pt_username, specialization = form.select.data))
  
  return render_template("apptSpecialistType.html", form = form, pt_username = pt_username)

@app.route("/chooseSpecialist/<pt_username>/<specialization>", methods = ['GET', 'POST'])
def chooseSpecialist(pt_username, specialization):
  form = ApptSpecialist()
  
  query_doctors = f"SELECT G.Hospital_ID, G.Last_Name, G.First_Name FROM general_info AS G, specialization as S, doctor as D WHERE S.Type = '{specialization}' AND D.Specialization_ID = S.Specialization_ID AND D.Doctor_ID = G.Hospital_ID"
  
  qe.connect()
  table = qe.do_query(query_doctors)
  qe.disconnect()
  
  choices = []
  
  for elem in table:
    choice = [elem[0], elem[2][0] + ". " + elem[1]]
    choices.append(choice)
  
  form.select.choices = choices
  
  #print("BACK: ", form.back.data)
  
  if(form.back.data):
    return redirect(url_for("specialistType", pt_username = pt_username))
  elif(form.submit.data):
    dr_id = form.select.data
    return redirect(url_for("appointmentloc", pt_username = pt_username, dr_id = dr_id))
  
  return render_template("apptSpecialist.html", form = form, pt_username = pt_username)

@app.route("/appointmentDate/<pt_username>/<int:dr_id>", methods = ['GET','POST'])
def appointmentloc(pt_username, dr_id):
    form = ApptLoc()
    query_string = f"SELECT O.Office_Name FROM office AS O, doctor_office AS DO WHERE DO.Doctor_ID = {dr_id} AND DO.Office_ID = O.Office_ID"
    qe.connect()
    apt_loc = qe.do_query(query_string)
    qe.disconnect()
    form.select.choices = [(l[0], l[0]) for l in apt_loc]
    #print(form.select.choices)
    if (form.submit.data):
        #print(form.select.data)
        apt_loc = form.select.data
        #print(apt_loc)
        return redirect(url_for('scheduleDate', pt_username = pt_username, dr_id = dr_id, apt_loc = apt_loc))
    elif (form.back.data):
        qe.connect()
        pt_string = f"SELECT User_ID FROM log_in WHERE UserName = '{pt_username}'"
        pt_id = qe.do_query(pt_string)[0][0]

        pp_string = f"SELECT Primary_physician_ID FROM patient WHERE Patient_ID = {pt_id}"
        pp_id = qe.do_query(pp_string)[0][0]
        qe.disconnect()

        back_to_primary = True
        if pp_id != int(dr_id):
            back_to_primary = False
        
        if back_to_primary == True:
            return redirect(url_for('makeAppointment',pt_username = pt_username))
        elif back_to_primary == False:
            return redirect(url_for('specialistType', pt_username = pt_username))
    
    return render_template('appointmentLocation.html', form = form, pt_username = pt_username)

@app.route("/appointmentDate/<pt_username>/<int:dr_id>/<apt_loc>", methods = ['GET', 'POST'])
def scheduleDate(pt_username, dr_id, apt_loc):
  form = ApptDate()
  qe.connect()
  query_loc = f"SELECT Office_ID FROM office WHERE Office_Name = '{apt_loc}'"
  loc_id = qe.do_query(query_loc)[0][0]
  print(loc_id)
  query_string = f"SELECT D.Working_date FROM doctor_office AS D WHERE D.Doctor_ID = {dr_id} AND D.Office_ID = {loc_id}"
  already_string = f"SELECT A.App_date FROM appointment AS A, LOG_IN AS L WHERE L.UserName = '{pt_username}' AND L.User_ID = A.Patient_ID AND Appt_Status = 'Booked'"
  already = qe.do_query(already_string)
  
  appts = qe.do_query(query_string)  
    
  qe.disconnect()
  print(appts)
  workingDate = appts[0][0]
  print(workingDate)
  #print("working date: ",workingDate)
  weekday = ['M', 'Tu', 'W', 'Th', 'F', 'Sa', 'Su']
  
  dates = {}  # Stores valid dates - pre-existing/booked appointments will set days to False
  
  ordToday = date.today().toordinal()
  for ordDay in range(ordToday, ordToday + 30):
    dates[date.fromordinal(ordDay)] = True

  for elem in dates:
    if(weekday[date.weekday(elem)] in workingDate):
      label = str(elem.month) + '/' + str(elem.day)
      form.radio.choices.append([elem, label])

  if form.submit.data:
    apt_date = form.radio.data
    Datepick = True
    #print(already)
    if already: 
        for elem in already:
            if str(elem[0]) == apt_date:
                Datepick = False
    if apt_date == "None":
        flash(f'Please Pick a Date', 'danger')
    elif Datepick == False:
        flash(f'You Already Have Appointment on this day. Please Choose Another', 'danger')
    else:
        return redirect(url_for('scheduleHour', pt_username = pt_username, dr_id = dr_id, apt_loc = apt_loc, apt_date = apt_date))
  elif form.back.data:
      return redirect(url_for('appointmentloc',pt_username = pt_username, dr_id = dr_id))

  return render_template('apptDate.html', form = form, titleText = "Choose Date", pt_username = pt_username)


@app.route("/appointmentHour/<pt_username>/<int:dr_id>/<apt_loc>/<apt_date>", methods = ['GET', 'POST'])
def scheduleHour(pt_username, dr_id, apt_loc, apt_date):
  form = ApptHour()
  qe.connect()
  loc_string = f"SELECT Office_ID FROM office WHERE Office_Name = '{apt_loc}'"
  loc_id = qe.do_query(loc_string)[0][0]
  query_appointments = (f"SELECT App_hour FROM appointment WHERE With_Doctor = {dr_id} AND App_date = '{str(apt_date)}' AND Appt_Status = 'Booked' AND App_Location_ID = {loc_id}")
  appts = qe.do_query(query_appointments)
  qe.disconnect()
  
  hours = [8, 9, 10, 11, 12, 13, 14, 15, 16]
  
  #print(appts)
  if appts:
    for appt in appts:
        if(appt[0] in hours):
            #print("removing:", appt[0])
            hours.remove(int(appt[0]))
  
  for hour in hours:
    modHour = hour % 12
    if(modHour == 0):
      modHour = 12
    suffix = 'AM'
    if(hour >= 12):
      suffix = 'PM'
    label = str(modHour) + ":00 " + suffix
    form.radio.choices.append([hour, label])

  no_hour = False
  if not hours:
      no_hour = True 

  #print(form.radio.choices)
  if form.submit.data:
      apt_hour = form.radio.data
      if apt_hour == "None":
          flash(f'Please Pick a Time', 'danger')
      else:
          apt_type = ""
          qe.connect()
          loc_string = f"SELECT Office_ID FROM office WHERE Office_Name = '{apt_loc}'"
          apt_id = qe.do_query(loc_string)[0][0]
          pt_string = f"SELECT User_ID FROM log_in WHERE UserName = '{pt_username}'"
          pt_id = qe.do_query(pt_string)[0][0]

          pp_string = f"SELECT Primary_physician_ID FROM patient WHERE Patient_ID = {pt_id}"
          pp_id = qe.do_query(pp_string)[0][0]

          apt_type = "General"
          if pp_id != int(dr_id):
              apt_type = "Specialist"
          #print(apt_type)
          insert_string = f"INSERT INTO appointment(App_Type, App_date, App_hour, With_Doctor, Patient_ID, App_Location_ID) VALUE('{apt_type}','{str(apt_date)}',{apt_hour},{dr_id},{pt_id},{apt_id})"
          qe.do_query(insert_string)
          qe.commit()
          qe.disconnect()
        #   if apt_type == "Specialist":
        #     approval_string = f"UPDATE patient SET Approval_Status = 'F' WHERE Patient_ID = {pt_id}"
        #     qe.connect()
        #     qe.do_query(approval_string)
        #     qe.commit()
        #     qe.disconnect()

          flash(f'You Successfully Make An Appointment','success')
          return redirect(url_for('makeAppointment', pt_username = pt_username))

  elif form.back.data:
    return redirect(url_for('scheduleDate',pt_username = pt_username, dr_id = dr_id, apt_loc = apt_loc))
  
  return render_template('apptHour.html', form = form, titleText = "Choose Hour", no_hour = no_hour, pt_username = pt_username)


'''
_________________________________________________________________________________________________
            
                        Modify current appointment 
_________________________________________________________________________________________________

'''

@app.route("/modify_current_appointment/<app_id>",methods=['GET', 'POST'])
def modify_current_appointment(app_id):
    qe.connect()
    query_string = (f"UPDATE appointment \
        SET Appt_Status  = 'Cancelled' \
        WHERE  Appt_ID =  {app_id};")
    qe.do_query(query_string)
    qe.commit()
    qe.disconnect()


    qe.connect()
    query_string2 = (f"SELECT UserName \
        FROM appointment,log_in \
        WHERE   Appt_ID =  {app_id} AND appointment.Patient_ID = log_in.User_ID")

    result = qe.do_query(query_string2)

    pt_username = result[0][0]
    qe.disconnect()
    
    return redirect(url_for('makeAppointment',pt_username=pt_username))

'''
_________________________________________________________________________________________________
            
                    PATIENT: VIEW CURRENT APPOINTMENT
_________________________________________________________________________________________________
'''

@app.route("/pt_View_Current_Appointment/<pt_username>",methods=['GET', 'POST'])
def pt_View_Current_Appointment(pt_username):
    #BOOKED RESULT 
    qe.connect()
    query_string_booked = (f"SELECT A.App_Type,A.App_date,A.App_hour,G.Last_Name,A.Appt_Status, O.Office_Name, A.Appt_ID \
        FROM appointment as A, log_in as L, office as O, general_info as G \
        WHERE L.UserName = '{pt_username}' \
        AND L.User_ID = A.Patient_ID \
        AND O.Office_ID =  A.App_Location_ID\
        AND A.With_Doctor = G.Hospital_ID\
        AND A.Appt_Status = 'Booked';")

    booked_result = qe.do_query(query_string_booked)
    qe.disconnect()

    #COMPLETED RESULT 
    qe.connect()
    query_string_completed = (f"SELECT A.App_Type,A.App_date,A.App_hour,G.Last_Name,A.Appt_Status, O.Office_Name, A.Appt_ID \
        FROM appointment as A, log_in as L, office as O, general_info as G\
        WHERE L.UserName = '{pt_username}' \
        AND L.User_ID = A.Patient_ID \
        AND O.Office_ID =  A.App_Location_ID\
        AND A.With_Doctor = G.Hospital_ID\
        AND (A.Appt_Status = 'Completed' Or A.Appt_Status = 'Process');")

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
        #print(f"current appt is {elem[6]}")
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

    if (request.method == 'POST'):
        data = request.form
        if ("selectRow" in data):
            appt_id = data["selectRow"]
            print(appt_id)
            
            return redirect(url_for('patientPostAppt',pt_username = pt_username, appt_id = appt_id))

    return render_template("pt_View_Current_Appointment.html",
                            booked_data = booked_data,completed_data=completed_data,pt_username=pt_username)


'''
_________________________________________________________________________________________________
            
                    EMAIL WHEN APPOINTMENT IS CANCELLED
_________________________________________________________________________________________________
'''
@app.route("/SendEmail/<pt_username>/<D_Fname>/<D_Email>/<P_Fname>/<P_Email>/<Type>")
def SendEmail(pt_username, D_Fname,D_Email,P_Fname,P_Email,Type):
    #Get username to redirect back to account page 
    qe.connect()
    query_string = (f"SELECT UserName \
        FROM general_info, log_in \
        WHERE general_info.Email = '{P_Email}' AND Hospital_ID = User_ID;")
    result = qe.do_query(query_string)
    username = result[0][0]

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
    return redirect(url_for('pt_View_Current_Appointment',pt_username=pt_username))

'''
_________________________________________________________________________________________________
            
                    ROUTE TO CANCEL APPOINTMENT
_________________________________________________________________________________________________
'''

@app.route("/cancel_Appointment/<pt_username>/<app_id>",methods=['GET', 'POST'])
def cancel_appointment(app_id,pt_username):
    qe.connect()
    query_string = (f"UPDATE appointment SET Appt_Status = 'Cancelled' WHERE Appt_ID = {app_id};")
    qe.do_query(query_string)
    qe.commit()

    #get Fname and Email
    get_info =  (f"SELECT D.Email, D.First_Name, P.Email, P.First_Name\
        FROM appointment AS  A,  general_info  AS P, general_info  AS D\
        WHERE  Appt_ID  = {app_id}  AND A.With_Doctor  =  D.Hospital_ID  AND  A.Patient_ID  =  P.Hospital_ID;")

    result = qe.do_query(get_info)
    doctor_email = result[0][0]
    doctor_fname = result[0][1]
    patient_email = result[0][2]
    patient_fname = result[0][3]

    Type = "cancelled"
    qe.disconnect()

    return redirect(url_for('SendEmail',pt_username = pt_username, D_Fname = doctor_fname,D_Email = doctor_email,
        P_Fname = patient_fname,P_Email = patient_email,Type = Type))



@app.route("/staffMakeAppt/<st_username>", methods = ['GET','POST'])
def staffMakeAppt(st_username):
    form = MakeApptStaff()
    if form.validate_on_submit():
        fname = form.first_name.data
        lname = form.last_name.data
        dob = form.dob.data
        return redirect(url_for('pickPatient',st_username = st_username, fname = fname, lname = lname, dob = dob))

    return render_template("staffMakeAppt.html", st_username = st_username, form = form)

@app.route("/staffMakeAppt/<st_username>/<fname>/<lname>/<dob>", methods = ['GET','POST'])
def pickPatient(st_username, fname,lname,dob):
    pt_query = f"SELECT L.UserName, G.First_Name, G.Last_Name, G.DOB, G.Email, G.Phone_Number FROM general_info AS G, patient AS P, log_in AS L WHERE G.First_Name = '{fname}' AND G.Last_Name = '{lname}' AND G.DOB = '{str(dob)}' AND G.Hospital_ID = P.Patient_ID AND G.Hospital_ID = L.User_ID"
    qe.connect()
    pt_list = qe.do_query(pt_query)
    qe.disconnect()

    if(request.method == "POST"):
        data = request.form
        if ("selectRow" in data):
            pt_username = data["selectRow"]
            return redirect(url_for("pickDoctor",st_username = st_username, pt_username = pt_username))
    return render_template("PickPatient.html",st_username = st_username, pt_list = pt_list)

@app.route("/cancelAppt/<st_username>", methods = ['GET','POST'])
def cancelMissedAppt(st_username):
    qe.connect()
    staffID = qe.do_query(f"SELECT User_ID FROM log_in WHERE UserName = '{st_username}';")
    staffID = staffID[0][0]
    staffLocation = qe.do_query(f"SELECT Office_Location_ID FROM staff WHERE Staff_ID = {staffID};")
    staffLocation = staffLocation[0][0]
    qe.disconnect()
    qe.connect()
    appointmentData = qe.do_query(f"SELECT A.Appt_ID, D.Last_Name,P.Last_Name, A.App_date, Appt_Status, P.Phone_Number, P.Email FROM general_info AS D, general_info AS P,appointment AS A \
                                        WHERE App_Location_ID = {staffLocation} \
                                        AND D.Hospital_ID = A.With_Doctor AND P.Hospital_ID = A.Patient_ID  \
                                        AND A.App_date = Subdate(CURDATE(),1)\
                                        AND A.Confirm_By is Null \
                                        AND Appt_Status = 'Booked'")
    qe.disconnect()
    if (request.method == "POST"):
        data = request.form
        if ("selectRow" in data):
            appt_id = data["selectRow"]
            print(appt_id)
            cancel_string = f"UPDATE appointment SET Appt_Status = 'Cancelled', Last_Updated = NOW() WHERE Appt_ID = {appt_id}"
            qe.connect()
            qe.do_query(cancel_string)
            qe.commit()
            qe.disconnect()
            flash(f'Appointment Has Been Cancelled','success')
            return redirect(url_for('cancelMissedAppt',st_username = st_username))
    return render_template('staffCancelAppt.html', st_username = st_username, appointmentData = appointmentData)

@app.route("/staffMakeAppt/<st_username>/<pt_username>",methods = ['GET','POST'])
def pickDoctor(st_username, pt_username):
    qe.disconnect()
    qe.connect()
    query_patient = f"SELECT User_ID FROM log_in WHERE UserName = '{pt_username}'"
    pt_id = qe.do_query(query_patient)[0][0]
    query_approval = f"SELECT Approval_Status FROM patient WHERE Patient_ID = {pt_id}"
    approval = qe.do_query(query_approval)[0][0]
    approval = (approval == 'T')
    query_doctor = f"SELECT P.Primary_physician_ID, G.Last_Name FROM patient AS P, general_info AS G WHERE P.Patient_ID = {pt_id} AND P.Primary_Physician_ID = G.Hospital_ID"
    doctor = qe.do_query(query_doctor)[0]
    qe.disconnect()
    form = staffPickDoctor()
    if(form.submitSpecialist.data):
        return redirect(url_for("pickSpecialType", st_username = st_username, pt_username = pt_username))
    elif form.submitDoctor.data:
        qe.connect()
        query_string = (f"SELECT P.Primary_physician_ID FROM patient AS P, LOG_IN as L WHERE P.Patient_ID = L.User_ID AND L.UserName = '{pt_username}'")
        dr_id = qe.do_query(query_string)[0][0]
        qe.disconnect()
        return redirect(url_for('pickLoc', st_username = st_username, pt_username = pt_username, dr_id = dr_id))

    return render_template('PickDoctor.html', form = form, primary = doctor[1], approval = approval, pt_username = pt_username, st_username = st_username)

@app.route("/staffMakeAppt/<st_username>/<pt_username>/pickspecialtype",methods = ['GET','POST'])
def pickSpecialType(st_username, pt_username):
    form = StaffPickSpecialType()
    if(form.back.data):
        return redirect(url_for('staffMakeAppt', st_username = st_username, pt_username = pt_username))
    elif(form.submit.data):
        return redirect(url_for("pickSpecialist", st_username = st_username, pt_username = pt_username, specialization = form.select.data))
  
    return render_template("PickSpecialType.html", form = form, st_username = st_username, pt_username = pt_username)

@app.route("/staffMakeAppt/<st_username>/<pt_username>/<specialization>/pickspecialist", methods = ['GET','POST'])
def pickSpecialist(st_username, pt_username,specialization ):
    form = StaffSpecialist()
    query_doctors = f"SELECT G.Hospital_ID, G.Last_Name, G.First_Name FROM general_info AS G, specialization as S, doctor as D WHERE S.Type = '{specialization}' AND D.Specialization_ID = S.Specialization_ID AND D.Doctor_ID = G.Hospital_ID"
  
    qe.connect()
    table = qe.do_query(query_doctors)
    qe.disconnect()
  
    choices = []
  
    for elem in table:
        choice = [elem[0], elem[2][0] + ". " + elem[1]]
        choices.append(choice)
  
    form.select.choices = choices
  
    if(form.back.data):
        return redirect(url_for("pickSpecialType", st_username = st_username, pt_username = pt_username))
    elif(form.submit.data):
        dr_id = form.select.data
        return redirect(url_for("pickLoc", st_username = st_username, pt_username = pt_username, dr_id = dr_id))
  
    return render_template("PickSpecialist.html", st_username = st_username, form = form, pt_username = pt_username)

@app.route("/staffMakeAppt/<st_username>/<pt_username>/<dr_id>", methods = ['GET','POST'])
def pickLoc(st_username, pt_username, dr_id):
    form = staffPickLoc()
    query_string = f"SELECT O.Office_Name FROM office AS O, doctor_office AS DO WHERE DO.Doctor_ID = {dr_id} AND DO.Office_ID = O.Office_ID"
    qe.connect()
    apt_loc = qe.do_query(query_string)
    qe.disconnect()
    form.select.choices = [(l[0], l[0]) for l in apt_loc]
    #print(form.select.choices)
    if (form.submit.data):
        #print(form.select.data)
        apt_loc = form.select.data
        print(apt_loc)
        return redirect(url_for('pickDate', st_username = st_username, pt_username = pt_username, dr_id = dr_id, apt_loc = apt_loc))
    elif (form.back.data):
        qe.connect()
        pt_string = f"SELECT User_ID FROM log_in WHERE UserName = '{pt_username}'"
        pt_id = qe.do_query(pt_string)[0][0]
        pp_string = f"SELECT Primary_physician_ID FROM patient WHERE Patient_ID = {pt_id}"
        pp_id = qe.do_query(pp_string)[0][0]
        qe.disconnect()

        back_to_primary = True
        if pp_id != int(dr_id):
            back_to_primary = False
        
        if back_to_primary == True:
            return redirect(url_for('staffMakeAppt',pt_username = pt_username))
        elif back_to_primary == False:
            return redirect(url_for('pickSpecialType', pt_username = pt_username))
    
    return render_template("pickLoc.html", st_username = st_username, pt_username = pt_username, form= form )

@app.route("/staffMakeAppt/<st_username>/<pt_username>/<int:dr_id>/<apt_loc>", methods = ['GET','POST'])
def pickDate(st_username, pt_username,dr_id,apt_loc):
    
  print('Iam here')
  form = StaffPickDate()
  qe.connect()
  query_loc = f"SELECT Office_ID FROM office WHERE Office_Name = '{apt_loc}'"
  loc_id = qe.do_query(query_loc)[0][0]
  query_string = f"SELECT D.Working_date FROM appointment AS A, DOCTOR_OFFICE AS D WHERE D.Doctor_ID = {dr_id} AND D.Office_ID = {loc_id}"
  already_string = f"SELECT A.App_date FROM appointment AS A, LOG_IN AS L WHERE L.UserName = '{pt_username}' AND L.User_ID = A.Patient_ID AND Appt_Status = 'Booked'"
  already = qe.do_query(already_string)

  appts = qe.do_query(query_string)  
    
  qe.disconnect()
  workingDate = appts[0][0]
  #print("working date: ",workingDate)
  weekday = ['M', 'Tu', 'W', 'Th', 'F', 'Sa', 'Su']
  
  dates = {}  # Stores valid dates - pre-existing/booked appointments will set days to False
  
  ordToday = date.today().toordinal()
  for ordDay in range(ordToday, ordToday + 30):
    dates[date.fromordinal(ordDay)] = True

  for elem in dates:
    if(weekday[date.weekday(elem)] in workingDate):
      label = str(elem.month) + '/' + str(elem.day)
      form.radio.choices.append([elem, label])

  if form.submit.data:
    apt_date = form.radio.data
    Datepick = True
    #print(already)
    if already: 
        for elem in already:
            if str(elem[0]) == apt_date:
                Datepick = False
    if apt_date == "None":
        flash(f'Please Pick a Date', 'danger')
    elif Datepick == False:
        flash(f'You Already Have Appointment on this day. Please Choose Another', 'danger')
    else:
        return redirect(url_for('pickHour', st_username = st_username, pt_username = pt_username, dr_id = dr_id, apt_loc = apt_loc, apt_date = apt_date))
  elif form.back.data:
      return redirect(url_for('pickLoc', st_username = st_username, pt_username = pt_username, dr_id = dr_id))

  return render_template('PickDate.html', st_username = st_username, form = form, titleText = "Choose Date", pt_username = pt_username)


@app.route("/staffMakeAppt/<st_username>/<pt_username>/<int:dr_id>/<apt_loc>/<apt_date>", methods = ['GET','POST'])
def pickHour(st_username, pt_username, dr_id, apt_loc, apt_date):
  form = StaffPickHour()
  qe.connect()
  loc_string = f"SELECT Office_ID FROM office WHERE Office_Name = '{apt_loc}'"
  loc_id = qe.do_query(loc_string)[0][0]
  query_appointments = (f"SELECT App_hour FROM appointment WHERE With_Doctor = {dr_id} AND App_date = '{str(apt_date)}' AND Appt_Status = 'Booked' AND App_Location_ID = {loc_id}")
  appts = qe.do_query(query_appointments)
  qe.disconnect()
  
  hours = [8, 9, 10, 11, 12, 13, 14, 15, 16]
  
  #print(appts)
  if appts:
    for appt in appts:
        if(appt[0] in hours):
            #print("removing:", appt[0])
            hours.remove(int(appt[0]))
  
  for hour in hours:
    modHour = hour % 12
    if(modHour == 0):
      modHour = 12
    suffix = 'AM'
    if(hour >= 12):
      suffix = 'PM'
    label = str(modHour) + ":00 " + suffix
    form.radio.choices.append([hour, label])

  no_hour = False
  if not hours:
      no_hour = True 

  #print(form.radio.choices)
  if form.submit.data:
      apt_hour = form.radio.data
      if apt_hour == "None":
          flash(f'Please Pick a Time', 'danger')
      else:
          apt_type = ""
          qe.connect()
          loc_string = f"SELECT Office_ID FROM office WHERE Office_Name = '{apt_loc}'"
          apt_id = qe.do_query(loc_string)[0][0]
          pt_string = f"SELECT User_ID FROM log_in WHERE UserName = '{pt_username}'"
          pt_id = qe.do_query(pt_string)[0][0]

          pp_string = f"SELECT Primary_physician_ID FROM patient WHERE Patient_ID = {pt_id}"
          pp_id = qe.do_query(pp_string)[0][0]

          apt_type = "General"
          if pp_id != int(dr_id):
              apt_type = "Specialist"
          #print(apt_type)
          insert_string = f"INSERT INTO appointment(App_Type, App_date, App_hour, With_Doctor, Patient_ID, App_Location_ID) \
          VALUE('{apt_type}','{str(apt_date)}',{apt_hour},{dr_id},{pt_id},{apt_id})"
          qe.do_query(insert_string)
          qe.commit()
          qe.disconnect()


          flash(f'You Successfully Make An Appointment','success')
          return redirect(url_for('staffMakeAppt', st_username = st_username, pt_username = pt_username, dr_id = dr_id))

  elif form.back.data:
    return redirect(url_for('pickDate',st_username = st_username, pt_username = pt_username, dr_id = dr_id, apt_loc = apt_loc))
  
  return render_template('PickHour.html', st_username = st_username, form = form, titleText = "Choose Hour", no_hour = no_hour, pt_username = pt_username)

@app.route("/Admin_View/<ad_username>", methods = ['GET','POST'])
def Admin_View(ad_username):
    qe.connect()
    query_string = (f" SELECT First_Name, Email, Last_Name, Phone_Number,DOB \
                        FROM general_info, log_in \
                        WHERE log_in.User_ID = general_info.Hospital_ID and log_in.UserName = '{ad_username}';")

    result = qe.do_query(query_string)
    qe.disconnect()

    first_name = result[0][0]
    email = result[0][1]
    last_name = result[0][2]
    phone = result[0][3]
    dob = result[0][4]
    return  render_template('Admin_View.html', ad_username = ad_username, first_name = first_name, 
                                        last_name = last_name, phone = phone, dob = dob, email=email)

@app.route("/admin_reg/<ad_username>", methods = ['GET','POST'])
def admin_reg(ad_username):
    form = AdminRegistration()
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
            if (iam == 'ST'):
                return redirect(url_for("staff_reg", st_username = username))
            elif (iam == 'DR'):
                return redirect(url_for("doc_reg", dr_username = username))

    return render_template("admin_registeration.html",form = form,ad_username = ad_username)



@app.route("/Admin_View/<ad_username>/GeneralReport",methods = ['GET','POST'])
def GeneralReport(ad_username):
    return render_template('GeneralReport.html', ad_username = ad_username)


@app.route("/addOffice/<ad_username>",methods = ['GET','POST'])
def addOffice(ad_username):
    form = AddOfficeForm()
    if form.validate_on_submit():
        office_name = form.office_name.data
        streetnumber = form.streetnumber.data
        streetname = form.streetname.data
        city = form.city.data

        statename = form.statename.data
        zipcode = form.zipcode.data


        qe.connect()
        state = qe.do_query("select State_ID from state where State_code = '" + statename + "'")
        qe.disconnect()
        state_id = state[0][0]

        qe.connect()
        check_office_name = qe.do_query("select count(*) from office \
            WHERE Office_Name= '" + office_name + "'")
        qe.disconnect()

        check_office_name = check_office_name[0][0]
        if (check_office_name == 1):
            flash(f'This Office Name already Exists','danger')
        else:
            qe.connect()
            query_string = (f"INSERT  INTO office(Office_Name, Street_Number, Street_Name, City, State_ID, Zipcode) \
                            VALUE('{office_name}',{streetnumber},'{streetname}','{city}',{state_id},{zipcode});")

            qe.do_query(query_string)
            qe.commit()
            qe.disconnect()
            flash(f'Office is successfully Added','success')

            return redirect(url_for('addOffice',ad_username = ad_username))

    return render_template("addOffice.html",form = form,ad_username = ad_username)

@app.route("/Staff_View/<st_username>/ClinicReport", methods=['GET','POST'])
def ClinicReport(st_username):
    form = ReportForm()
    qe.connect()
    staffID = qe.do_query(f"SELECT User_ID FROM log_in WHERE UserName = '{st_username}';")
    staffID = staffID[0][0]
    staffLocationID = qe.do_query(f"SELECT Office_Location_ID FROM staff WHERE Staff_ID = {staffID};")
    staffLocationID = staffLocationID[0][0]
    staffLocation = qe.do_query(f"SELECT Office_Name FROM office WHERE Office_ID = {staffLocationID};")
    staffLocation = staffLocation[0][0]
    qe.disconnect()
    qe.connect()
    patientCount = qe.do_query(f"SELECT COUNT(DISTINCT Patient_ID) from medical_clinic.appointment where App_Location_ID = {staffLocationID};")
    patientCount = patientCount[0][0]
    qe.disconnect()
    qe.connect()
    doctorCount = qe.do_query(f"SELECT COUNT(DISTINCT Doctor_ID) from medical_clinic.doctor_office where Office_ID = {staffLocationID};")
    doctorCount = doctorCount[0][0]
    qe.disconnect()
    qe.connect()
    generalCount = qe.do_query(f"SELECT COUNT(DISTINCT od.Doctor_ID) from medical_clinic.doctor_office as od, medical_clinic.doctor as d where od.Office_ID = {staffLocationID} and d.Specialization_ID = 21 and d.Doctor_ID = od.Doctor_ID;")
    generalCount = generalCount[0][0]
    qe.disconnect()
    qe.connect()
    specialCount = qe.do_query(f"SELECT COUNT(DISTINCT od.Doctor_ID) from medical_clinic.doctor_office as od, medical_clinic.doctor as d where od.Office_ID = {staffLocationID} and d.Specialization_ID != 21 and d.Doctor_ID = od.Doctor_ID;")
    specialCount = specialCount[0][0]
    qe.disconnect()
    qe.connect()
    staffCount = qe.do_query(f"SELECT COUNT(*) FROM medical_clinic.staff where Office_Location_ID= {staffLocationID};")
    staffCount = staffCount[0][0]
    qe.disconnect()
    qe.connect()
    apptCount = qe.do_query(f"SELECT COUNT(*) FROM medical_clinic.appointment where app_date >= current_date() and Appt_Status = 'Booked' and  App_Location_ID = {staffLocationID};")
    apptCount = apptCount[0][0]
    qe.disconnect()
    qe.connect()
    apptGeneralCount = qe.do_query(f"SELECT COUNT(*) FROM medical_clinic.appointment where app_date >= current_date() and Appt_Status = 'Booked' and  App_Location_ID = {staffLocationID} and App_Type = 'General';")
    apptGeneralCount = apptGeneralCount[0][0]
    qe.disconnect()
    qe.connect()
    apptSpecialCount = qe.do_query(f"SELECT COUNT(*) FROM medical_clinic.appointment where app_date >= current_date() and Appt_Status = 'Booked' and  App_Location_ID = {staffLocationID} and App_Type = 'Specialist';")
    apptSpecialCount = apptSpecialCount[0][0]
    qe.disconnect()
    if(form.submit.data):
        from_date = form.from_date.data
        to_date = form.to_date.data
        qe.connect()
        result = qe.do_query(f"SELECT a.Appt_ID, a.App_Type, a.App_date, s.Last_Name,d.Last_Name,p.First_Name,p.Last_Name FROM medical_clinic.appointment as a, medical_clinic.general_info as p, medical_clinic.general_info as d, general_info AS s where a.App_Location_ID = {staffLocationID} and a.Appt_Status = 'Completed' and a.App_date>= '{str(from_date)}' and a.App_date <= '{str(to_date)}' and a.Confirm_By = s.Hospital_ID and a.With_Doctor = d.Hospital_ID and a.Patient_ID = p.Hospital_ID;")
        qe.disconnect()
        numberedData = []
        for i in range(len(result)):
            temp = []
            temp.append(i + 1)
            temp += result[i]
            numberedData.append(temp)
        return render_template('ClinicReport.html', st_username = st_username,form = form,data = numberedData,officeName = staffLocation,patientCount = patientCount,doctorCount = doctorCount,generalCount = generalCount,specialCount = specialCount, staffCount = staffCount, apptCount = apptCount, apptGeneralCount = apptGeneralCount,apptSpecialCount = apptSpecialCount)
    if(request.method == 'POST'):
        data = request.form
        if('selectRow' in data):
            appt_ID = data['selectRow']
            return  redirect(url_for('ReportSelect', st_username = st_username,appt_ID = appt_ID))
    return render_template('ClinicReport.html', st_username = st_username,form = form,officeName = staffLocation,patientCount = patientCount,doctorCount = doctorCount,generalCount = generalCount,specialCount = specialCount, staffCount = staffCount, apptCount = apptCount, apptGeneralCount = apptGeneralCount,apptSpecialCount = apptSpecialCount)

@app.route("/Staff_View/<st_username>/ClinicReport/<appt_ID>", methods=['GET','POST'])
def ReportSelect(st_username,appt_ID):
    blood_test = True
    prescript = True
    post_string = f"SELECT Doctor_Diagnosis, Balance_Due, Blood_Test_ID, Prescription_ID FROM post_appointment WHERE Appointment_ID = {appt_ID};"
    qe.connect()
    all_post = qe.do_query(post_string)[0]
    qe.disconnect()

    if all_post[2] is None:
        blood_test = False
    if all_post[3] is None:
        prescript = False

    blood_result = []
    if blood_test == True:
        qe.connect()
        blood_test_query = f"SELECT Blood_test_id FROM blood_test_result WHERE Appt_ID = {appt_ID};"
        blood_result = qe.do_query(blood_test_query)[0][0]
        print(blood_result)
        qe.disconnect()

    prescript_result = []
    if prescript == True:
        qe.connect()
        prescript_query = f"SELECT Prescription_ID, Drug_Name, Usage_Note, Num_Refill, Patient_ID FROM prescription WHERE Appt_ID = {appt_ID};"
        prescript_result = qe.do_query(prescript_query)[0]
        qe.disconnect()

    if (request.method == "POST"):
      data = request.form
      if ("download" in data):
        query_string = f"SELECT L.UserName FROM appointment as A, log_in as L WHERE A.Appt_ID = {appt_ID} AND A.Patient_ID = L.User_ID;"
        qe.connect()
        pt_username = qe.do_query(query_string)[0][0]
        qe.disconnect()
        return redirect(url_for("BloodTest",bl_id = blood_result, pt_username = pt_username))
    return render_template('ReportSelect.html', st_username = st_username, blood_test = blood_test, prescript = prescript, prescript_result = prescript_result, all_post = all_post)


if __name__ == '__main__':
    app.run(debug=True)

