from QueryEngine import QueryEngine
from flask import flash
import string

qe = QueryEngine()
qe.setup_default()


def user_check(username):
  qe.connect()
  check_exist = qe.do_query("select count(*) from log_in where UserName = '" + username + "'")
  qe.disconnect()
  count = check_exist[0][0]
  if count == 1:
    #print("Username is already taken, pls use another one")
    return False
  else:
    #print("Good username")
    return True 

def email_check(email):
    qe.connect()
    check_exist = qe.do_query("select count(*) from general_info where Email = '" + email + "'")
    qe.disconnect()
    count = check_exist[0][0]
    if count == 1:
        #print("Email is already taken, pls use another")
        return False
    else:
        #print("Good email")
        return True


def insert_to_db(username, password, fname, lname, mname,dob,streetnum, streetname, aptnum, city, state, zipcode, email, phonenum, sex, ethnicity):
    qe.connect()
    state = qe.do_query("select State_ID from state where State_code = '" + state + "'")
    qe.disconnect()
    state_id = state[0][0]
    #print(state_id)
    if mname == None:
      mname = 'NULL'
    else:
      mname = '"' + mname + '"'
    
    if aptnum == None:
      aptnum = 'NULL'

    insert_string = (f"INSERT INTO general_info(First_name, Last_Name, Middle_Initial, DOB, Street_Number, Street_Name, Apt_Number,City, State_ID, Zipcode, Email, Phone_Number, Sex, Ethnicity) Value('{fname}','{lname}',{mname},'{dob}',{streetnum},'{streetname}',{aptnum},'{city}',{state_id},{zipcode},'{email}','{phonenum}','{sex}','{ethnicity}')") 
    #print(insert_string)   
    qe.connect()
    qe.do_query(insert_string)
    qe.commit()
    qe.disconnect()
    query_string = (f"select Hospital_ID from general_info where Email =  '{email}'")
    qe.connect()
    hos_id = qe.do_query(query_string)
    qe.disconnect()
    hos_id = hos_id[0][0]
    insert_string = (f"INSERT INTO log_in(User_ID, Username, Password_Hash) VALUE({hos_id},'{username}',MD5('{password}'))")
    qe.connect()
    qe.do_query(insert_string)
    qe.commit()
    qe.disconnect()

  #def insert_patient(primary_dr, insurance_id, ins_name, ins_expr, ins_phone):
def insert_staff(username, office_loc, work_date):
    query_string = (f"SELECT User_ID FROM log_in WHERE UserName = '{username}'")
    qe.connect()
    hos_id = qe.do_query(query_string)
    qe.disconnect()
    hos_id = hos_id[0][0]
    #print(hos_id)
    query_string = (f"SELECT Office_ID FROM office WHERE Office_Name = '{office_loc}'")
    qe.connect()
    office_id = qe.do_query(query_string)
    qe.disconnect()
    office_id = office_id[0][0]
    #print(office_id)
    staff_date = ""
    for d in work_date:
      staff_date = staff_date + d
    #print(staff_date)
    insert_string = (f"INSERT INTO staff(Staff_ID, Office_Location_ID,Employed_Since,Working_date) VALUE({hos_id},{office_id},CURDATE(),'{staff_date}')")
    #print(insert_string)
    qe.connect()
    qe.do_query(insert_string)
    qe.commit()
    qe.disconnect()

def insert_doc(username,office_loc, work_date, spec):
    query_string = (f"SELECT User_ID FROM log_in WHERE UserName = '{username}'")
    qe.connect()
    hos_id = qe.do_query(query_string)
    qe.disconnect()
    hos_id = hos_id[0][0]

    query_string = (f"SELECT Office_ID FROM office WHERE Office_Name = '{office_loc}'")
    qe.connect()
    office_id = qe.do_query(query_string)
    qe.disconnect()
    office_id = office_id[0][0]

    query_string = (f"SELECT Specialization_ID FROM specialization WHERE Type = '{spec}'")
    qe.connect()
    spec_id = qe.do_query(query_string)
    qe.disconnect()
    spec_id = spec_id[0][0]

    #print(hos_id," ",spec_id, " ",office_id)
    dr_date = ""
    for d in work_date:
      dr_date = dr_date + d
    
    insert_string = (f"INSERT INTO doctor(Doctor_ID, Specialization_ID, Employed_Since) VALUE({hos_id},{spec_id},CURDATE())")
    #print(insert_string)
    qe.connect()
    qe.do_query(insert_string)
    qe.commit()
    qe.disconnect()

    insert_string = (f"INSERT INTO doctor_office(Office_ID, Doctor_ID, Start_Date, Working_date) VALUE({office_id},{hos_id},CURDATE(),'{dr_date}')")
    qe.connect()
    qe.do_query(insert_string)
    qe.commit()
    qe.disconnect()

def add_loc(username, office_loc, work_date):
    office_choice = True
    work_date_choice = True

    query_string = (f"SELECT User_ID FROM log_in WHERE UserName = '{username}'")
    qe.connect()
    hos_id = qe.do_query(query_string)
    qe.disconnect()
    hos_id = hos_id[0][0]

    query_string = (f"SELECT Office_ID FROM office WHERE Office_Name = '{office_loc}'")
    qe.connect()
    office_id = qe.do_query(query_string)
    qe.disconnect()
    office_id = office_id[0][0]

    query_string = (f"SELECT count(*) from doctor_office Where Office_ID = {office_id} AND Doctor_ID = {hos_id} AND End_Date is NULL")
    qe.connect()
    exist = qe.do_query(query_string)
    qe.disconnect()
    

    if exist == 1:
      office_choice = False
      return office_choice, work_date_choice
    
    query_string = (f"SELECT Working_date from doctor_office WHERE Doctor_ID = {hos_id} AND End_Date is NULL")
    qe.connect()
    exist_workdate = qe.do_query(query_string)
    qe.disconnect()
    
    date_exist = []
    for d in exist_workdate:
      d = d[0]
      date_exist.append(d)

    for el in work_date:
      for d in date_exist:
        if (d.find(f'{el}') != -1):
          work_date_choice = False
          return office_choice, work_date_choice
    
    dr_date = ""
    for d in work_date:
      dr_date = dr_date + d

    insert_string = (f"INSERT INTO doctor_office(Office_ID, Doctor_ID, Start_Date, Working_date) VALUE({office_id},{hos_id},CURDATE(),'{dr_date}')")
    qe.connect()
    qe.do_query(insert_string)
    qe.commit()
    qe.disconnect()

    return office_choice, work_date_choice

def insert_patient(username, dr_id):
  query_string = (f"SELECT User_ID FROM log_in WHERE UserName = '{username}'")
  qe.connect()
  user_id = qe.do_query(query_string)
  qe.disconnect()
  user_id = user_id[0][0]
  insert_string = (f"INSERT INTO patient(Patient_ID,Patient_Since,Primary_physician_ID) VALUE({user_id},CURDATE(),{dr_id})")
  qe.connect()
  qe.do_query(insert_string)
  qe.commit()
  qe.disconnect()
  insert_string = (f"INSERT INTO health_profile(Health_Profile_ID) VALUE({user_id})")
  qe.connect()
  qe.do_query(insert_string)
  qe.commit()
  qe.disconnect()

def insert_insur(username, insur_id, insur_name, insur_exp, insur_phone):
  query_string = (f"SELECT User_ID FROM log_in WHERE UserName = '{username}'")
  qe.connect()
  user_id = qe.do_query(query_string)
  qe.disconnect()
  user_id = user_id[0][0]
  insert_string = (f"INSERT INTO insurance_info(Insurance_ID,Insurance_Name,Expiration,Insur_Phone) VALUE({insur_id},'{insur_name}','{insur_exp}','{insur_phone}')")
  qe.connect()
  qe.do_query(insert_string)
  qe.commit()
  qe.disconnect()
  insert_string = (f"UPDATE Patient SET Insurance_ID = {insur_id} WHERE Patient_ID = {user_id}")
  qe.connect()
  qe.do_query(insert_string)
  qe.commit()
  qe.disconnect()
 

