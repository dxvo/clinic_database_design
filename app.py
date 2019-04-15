from flask import Flask, render_template, url_for, flash, redirect, request
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

@app.route("/patient_reg/<pt_username>", methods = ['GET','POST'])
def patient_reg(pt_username):
    form = PatientForm()
    if form.validate_on_submit():
        location = form.officelocation.data
        return redirect(url_for('primary_phys_pick',office = location, pt_username = pt_username))
    return render_template('patient_reg.html', form = form)


@app.route("/register/staff_reg/<uuid:st_username>", methods = ['GET','POST'])
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




@app.route("/staffPage/<st_username>/staffPost/<appt_id>",methods = ['GET','POST'])
def staffPost(st_username, appt_id):
    form = StaffPostForm()
    if (form.validate_on_submit()):
        if (form.submit.data):
            print(appt_id)
            diagnosis = form.doctorDiagnosis.data
            balance = form.balance.data
            insert_string = f"INSERT INTO POST_APPOINTMENT(Appointment_ID, Doctor_Diagnosis, Balance_Due) VALUE({appt_id},'{diagnosis}',{balance})"
            print(insert_string)
            qe.connect()
            qe.do_query(insert_string)
            qe.commit()
            qe.disconnect()
            print(diagnosis)
            print(balance)
            blood_prescript = form.blood_prescript.data
            print(blood_prescript)
            blood = 'Fb'
            prescript = 'Fp'
            for elem in blood_prescript:
                if elem == 'Tp':
                    prescript = 'Tp'
                if elem == 'Tb':
                    blood = 'Tb'
            print(blood, prescript)
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
            insert_string = f"INSERT INTO BLOOD_TEST_RESULT(White_blood_Cell_Count, Red_blood_Cell_Count, Hemoglobin, Hematocrit, MCV, MCH, RDW, Platelet_Count, Lymphocyte, Monocyte, Cholesterol, Iron, Sodium, Potassium, Appt_ID) VALUE({white_blood},{red_blood},{hemoglobin},{hematocrit},{mcv},{mch},{rdw},{platelet},{lymphocyte},{monocyte},{cholesterol},{iron},{sodium},{potassium},{appt_id})"
            qe.connect()
            qe.do_query(insert_string)
            qe.commit()
            qe.disconnect()
            query_string = f"SELECT Blood_test_id FROM BLOOD_TEST_RESULT WHERE Appt_ID = {appt_id}"
            qe.connect()
            blood_id = qe.do_query(query_string)[0][0]
            qe.disconnect()
            update_string = f"UPDATE POST_APPOINTMENT SET Blood_Test_ID = {blood_id} WHERE Appointment_ID = {appt_id}"
            qe.connect()
            qe.do_query(update_string)
            qe.commit()
            qe.disconnect()
            update_string = f"UPDATE APPOINTMENT SET Appt_Status = 'Completed' WHERE Appt_ID = {appt_id}"
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
            query_string = f"SELECT With_Doctor, Patient_ID FROM APPOINTMENT WHERE Appt_ID = {appt_id}"
            qe.connect()
            ppl = qe.do_query(query_string)
            dr_id = ppl[0][0]
            pt_id = ppl[0][1]
            qe.disconnect()
            insert_string = f"INSERT INTO PRESCRIPTION(Drug_Name, Assigned_By, Usage_Note, Num_Refill, Patient_ID, Appt_ID) VALUE('{drug}',{dr_id},'{usage}',{numfill},{pt_id},{appt_id})"
            qe.connect()
            qe.do_query(insert_string)
            qe.commit()
            qe.disconnect()
            query_string = f"SELECT Prescription_ID FROM PRESCRIPTION WHERE Appt_ID = {appt_id}"
            qe.connect()
            prescript_id = qe.do_query(query_string)[0][0]
            qe.disconnect()
            update_string = f"UPDATE POST_APPOINTMENT SET Prescription_ID = {prescript_id} WHERE Appointment_ID = {appt_id}"
            qe.connect()
            qe.do_query(update_string)
            qe.commit()
            qe.disconnect()
            update_string = f"UPDATE APPOINTMENT SET Appt_Status = 'Completed' WHERE Appt_ID = {appt_id}"
            qe.connect()
            qe.do_query(update_string)
            qe.commit()
            qe.disconnect()
            return redirect(url_for('staffPage',st_username = st_username))
        if form.next_submit.data:
            query_string = f"SELECT With_Doctor, Patient_ID FROM APPOINTMENT WHERE Appt_ID = {appt_id}"
            qe.connect()
            ppl = qe.do_query(query_string)
            dr_id = ppl[0][0]
            pt_id = ppl[0][1]
            qe.disconnect()
            insert_string = f"INSERT INTO PRESCRIPTION(Drug_Name, Assigned_By, Usage_Note, Num_Refill, Patient_ID, Appt_ID) VALUE('{drug}',{dr_id},'{usage}',{numfill},{pt_id},{appt_id})"
            qe.connect()
            qe.do_query(insert_string)
            qe.commit()
            qe.disconnect()
            query_string = f"SELECT Prescription_ID FROM PRESCRIPTION WHERE Appt_ID = {appt_id}"
            qe.connect()
            prescript_id = qe.do_query(query_string)[0][0]
            qe.disconnect()
            update_string = f"UPDATE POST_APPOINTMENT SET Prescription_ID = {prescript_id} WHERE Appointment_ID = {appt_id}"
            qe.connect()
            qe.do_query(update_string)
            qe.commit()
            qe.disconnect()
            return redirect(url_for('staffPostBlood',st_username = st_username, appt_id = appt_id))

    return render_template('staffPostPrescript.html', form = form, bl = bl)

@app.route("/staffPage/<st_username>/staffReports",methods = ['GET','POST'])
def staffReports(st_username):
    return render_template('staffReports.html', st_username = st_username)

@app.route("/staffPage/<st_username>/staffProfile", methods = ['GET','POST'])
def staffProfile(st_username):
    return render_template('staffProfile.html', st_username = st_username)



@app.route("/specialistType/<pt_username>", methods = ['GET', 'POST'])
def specialistType(pt_username):
  form = ApptSpecialistType()
  print("abd: ", form.back.data)
  print("dgh: ", form.submit.data)
  if(form.back.data):
    return redirect(url_for('makeAppointment', pt_username = pt_username))
  elif(form.submit.data):
    return redirect(url_for("chooseSpecialist", pt_username = pt_username, specialization = form.select.data))
  
  return render_template("apptSpecialistType.html", form = form)

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
  
  print("BACK: ", form.back.data)
  
  if(form.back.data):
    return redirect(url_for("specialistType", pt_username = pt_username))
  elif(form.submit.data):
    dr_id = form.select.data
    return redirect(url_for("appointmentloc", pt_username = pt_username, dr_id = dr_id))
  
  return render_template("apptSpecialist.html", form = form)

@app.route("/appointmentDate/<pt_username>/<dr_id>", methods = ['GET','POST'])
def appointmentloc(pt_username, dr_id):
    form = ApptLoc()
    query_string = f"SELECT O.Office_Name FROM OFFICE AS O, DOCTOR_OFFICE AS DO WHERE DO.Doctor_ID = {dr_id} AND DO.Office_ID = O.Office_ID"
    qe.connect()
    apt_loc = qe.do_query(query_string)
    qe.disconnect()
    form.select.choices = [(l[0], l[0]) for l in apt_loc]
    print(form.select.choices)
    if (form.submit.data):
        print(form.select.data)
        apt_loc = form.select.data
        print(apt_loc)
        return redirect(url_for('scheduleDate', pt_username = pt_username, dr_id = dr_id, apt_loc = apt_loc))
    elif (form.back.data):
        return redirect(url_for('specialistType', pt_username = pt_username))
    
    return render_template('appointmentLocation.html', form = form)

@app.route("/appointmentDate/<pt_username>/<dr_id>/<apt_loc>", methods = ['GET', 'POST'])
def scheduleDate(pt_username, dr_id, apt_loc):
  form = ApptDate()
  qe.connect()
  query_loc = f"SELECT Office_ID FROM OFFICE WHERE Office_Name = '{apt_loc}'"
  loc_id = qe.do_query(query_loc)[0][0]
  query_string = f"SELECT D.Working_date FROM APPOINTMENT AS A, DOCTOR_OFFICE AS D WHERE D.Doctor_ID = {dr_id} AND D.Office_ID = {loc_id}"
#   query_appointments = '''
#     SELECT App_date, App_hour, doctor.Doctor_ID, Working_date
#     FROM appointment, doctor, doctor_office
#     WHERE Appt_Status != 'Completed' AND With_Doctor = doctor.Doctor_ID
  already_string = f"SELECT A.App_date FROM APPOINTMENT AS A, LOG_IN AS L WHERE L.UserName = '{pt_username}' AND L.User_ID = A.Patient_ID AND Appt_Status = 'Booked'"
  already = qe.do_query(already_string)

  appts = qe.do_query(query_string)  
    
  qe.disconnect()

  workingDate = appts[0][0]
  print("working date: ",workingDate)
  weekday = ['M', 'Tu', 'W', 'Th', 'F', 'Sa', 'Su']
  
  dates = {}  # Stores valid dates - pre-existing/booked appointments will set days to False
  
  ordToday = date.today().toordinal()
  for ordDay in range(ordToday, ordToday + 30):
    dates[date.fromordinal(ordDay)] = True
  
#   for appt in appts:
#     day = appt[0]
#     if(day in dates):
#       dates[day] = False

  for elem in dates:
    if(weekday[date.weekday(elem)] in workingDate):
      label = str(elem.month) + '/' + str(elem.day)
      form.radio.choices.append([elem, label])

  if form.submit.data:
    apt_date = form.radio.data
    Datepick = True
    print(already)
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
  
  return render_template('apptDate.html', form = form, titleText = "Choose Date")


@app.route("/appointmentHour/<pt_username>/<dr_id>/<apt_loc>/<apt_date>", methods = ['GET', 'POST'])
def scheduleHour(pt_username, dr_id, apt_loc, apt_date):
  form = ApptHour()
  #print(type(apt_date))
  qe.connect()
  loc_string = f"SELECT Office_ID FROM OFFICE WHERE Office_Name = '{apt_loc}'"
  loc_id = qe.do_query(loc_string)[0][0]
  query_appointments = (f"SELECT App_hour FROM appointment WHERE With_Doctor = {dr_id} AND App_date = '{str(apt_date)}' AND Appt_Status = 'Booked' AND App_Location_ID = {loc_id}")
  appts = qe.do_query(query_appointments)
  qe.disconnect()
  
  hours = [8, 9, 10, 11, 12, 13, 14, 15, 16]
  
  print(appts)
  if appts:
    for appt in appts:
            #print("removing:", appt[0])
        if(appt[0] in hours):
            print("removing:", appt[0])
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
          print("soemthing here")
          apt_type = ""
          qe.connect()
          loc_string = f"SELECT Office_ID FROM OFFICE WHERE Office_Name = '{apt_loc}'"
          apt_id = qe.do_query(loc_string)[0][0]
          pt_string = f"SELECT User_ID FROM LOG_IN WHERE UserName = '{pt_username}'"
          pt_id = qe.do_query(pt_string)[0][0]

          pp_string = f"SELECT Primary_physician_ID FROM PATIENT WHERE Patient_ID = {pt_id}"
          pp_id = qe.do_query(pp_string)[0][0]

          print("Primary Physician ID: ", pp_id, "Dr ID: ", dr_id)

          apt_type == "General"
          if pp_id != int(dr_id):
              apt_type = "Specialist"

          insert_string = f"INSERT INTO APPOINTMENT(App_Type, App_date, App_hour, With_Doctor, Patient_ID, App_Location_ID) VALUE('{apt_type}','{str(apt_date)}',{apt_hour},{dr_id},{pt_id},{apt_id})"
          qe.do_query(insert_string)
          qe.commit()
          qe.disconnect()

          flash(f'You Successfully Make An Appointment','success')
          return redirect(url_for('makeAppointment', pt_username = pt_username))

  elif form.back.data:
    return redirect(url_for('scheduleDate',pt_username = pt_username, dr_id = dr_id, apt_loc = apt_loc))
  
  return render_template('apptHour.html', form = form, titleText = "Choose Hour", no_hour = no_hour)

# @app.route("/staffReports")
# def staffReports():
#     return render_template('staffReports.html')

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
                flash(f'You Successfully Log in','success')
                return redirect(url_for('Patient_View',pt_username = username))

            elif login_check.account_type(username, password) == "doctor":
                flash(f'You Successfully Log in','success')
                return render_template('doctor.html')

            elif login_check.account_type(username, password) == "staff":
                flash(f'You Successfully Log in','success')
                return redirect(url_for('Staff_View',st_username = username))
        else:
            flash('Invalid Account, Check Your Username and Password', 'danger')

    return render_template('login.html', title='Login', form=form)

'''
_________________________________________________________________________________________________
            
                        STAFF - STAFF - STAFF SECTION HERE. 
_________________________________________________________________________________________________
'''
@app.route("/Staff_View/<st_username>", methods=['GET', 'POST'])
def Staff_View(st_username):
    qe.connect()
    query_string = (f" SELECT First_Name, Email, Last_Name, Phone_Number,DOB \
                        FROM general_info, log_in \
                        WHERE log_in.User_ID = general_info.Hospital_ID and log_in.UserName = '{st_username}';")

    result = qe.do_query(query_string);
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

'''
_________________________________________________________________________________________________
            
                        STAFF PAGE - USED TO VIEW CURRENT LIST OF APPOTMENT
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
    appointmentData = qe.do_query(f"SELECT A.Appt_ID, A.Confirm_By,D.Last_Name,P.Last_Name, A.App_date,A.App_hour,Appt_Status FROM general_info AS D, general_info AS P,appointment AS A WHERE App_Location_ID = {staffLocation} AND D.Hospital_ID = A.With_Doctor AND P.Hospital_ID = A.Patient_ID AND (Appt_Status = 'Booked' OR Appt_Status = 'Process');")
    qe.disconnect()
    numberedData = []
    for i in range(len(appointmentData)):
        temp = []
        temp.append(i + 1)
        temp += appointmentData[i]
        numberedData.append(temp)
    print(type(numberedData[0][2]))
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
            status = qe.do_query(f"SELECT Appt_Status FROM APPOINTMENT WHERE Appt_ID = {appt_id};")
            status = status[0][0]
            qe.disconnect()
            if (status == "Booked"):
                flash('You Cannot Modify, The Appointment is Not in Process','danger')
            elif (status == 'Process'):
                return redirect(url_for('staffPost', st_username = st_username, appt_id = appt_id))
        if ("confirm" in data):
            appt_id = data["confirm"]
            update_string = f"UPDATE APPOINTMENT SET Confirm_By = {staffID}, Last_Updated = NOW() WHERE Appt_ID = {appt_id}"
            qe.connect()
            qe.do_query(update_string)
            qe.commit()
            qe.disconnect()
            flash(f'Successfully Confirmed', 'success')
            return redirect(url_for('staffPage', st_username = st_username))
    return render_template('staffPage.html',data = numberedData, st_username = st_username)

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
    query_doctor = f"SELECT P.Primary_physician_ID, G.Last_Name FROM PATIENT AS P, GENERAL_INFO AS G WHERE P.Patient_ID = {pt_id} AND P.Primary_Physician_ID = G.Hospital_ID"
    doctor = qe.do_query(query_doctor)[0]
    qe.disconnect()
    form = ApptDoctor()
    if(form.submitSpecialist.data):
        return redirect(url_for("specialistType", pt_username = pt_username))
    elif form.submitDoctor.data:
        qe.connect()
        query_string = (f"SELECT P.Primary_physician_ID FROM PATIENT AS P, LOG_IN as L WHERE P.Patient_ID = L.User_ID AND L.UserName = '{pt_username}'")
        dr_id = qe.do_query(query_string)[0][0]
        qe.disconnect()
        return redirect(url_for('appointmentloc', pt_username = pt_username, dr_id = dr_id))

    return render_template('apptDoctor.html', form = form, primary = doctor[1], approval = approval)


'''
_________________________________________________________________________________________________
            
                    PATIENT: VIEW CURRENT APPOINTMENT
_________________________________________________________________________________________________
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
                            booked_data = booked_data,completed_data=completed_data,pt_username=pt_username)


'''
_________________________________________________________________________________________________
            
                    EMAIL WHEN APPOINTMENT IS CANCELLED
_________________________________________________________________________________________________
'''
@app.route("/SendEmail/<D_Fname>/<D_Email>/<P_Fname>/<P_Email>/<Type>")
def SendEmail(D_Fname,D_Email,P_Fname,P_Email,Type):
    #Get username to redirect back to account page 
    qe.connect()
    query_string = (f"SELECT UserName \
        FROM general_info, log_in \
        WHERE general_info.Email = '{P_Email}' AND Hospital_ID = User_ID;")
    result = qe.do_query(query_string);
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
    return redirect(url_for('Patient_View',pt_username=username))

'''
_________________________________________________________________________________________________
            
                    ROUTE TO CANCEL APPOINTMENT
_________________________________________________________________________________________________
'''

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



if __name__ == '__main__':
    app.run()

