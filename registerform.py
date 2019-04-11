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
    print("Username is already taken, pls use another one")
    return False
  else:
    print("Good username")
    return True 

def email_check(email):
    qe.connect()
    check_exist = qe.do_query("select count(*) from general_info where Email = '" + email + "'")
    qe.disconnect()
    count = check_exist[0][0]
    if count == 1:
        print("Email is already taken, pls use another")
        return False
    else:
        print("Good email")
        return True


def insert_to_db(username, password, fname, lname, mname,dob,streetnum, streetname, aptnum, city, state, zipcode, email, phonenum, sex, ethnicity):
    qe.connect()
    state = qe.do_query("select State_ID from state where State_code = '" + state + "'")
    qe.disconnect()
    state_id = state[0][0]
    print(state_id)
    if mname == None:
      mname = 'NULL'
    else:
      mname = '"' + mname + '"'
    
    if aptnum == None:
      aptnum = 'NULL'

    insert_string = (f"INSERT INTO GENERAL_INFO(First_name, Last_Name, Middle_Initial, DOB, Street_Number, Street_Name, Apt_Number,City, State_ID, Zipcode, Email, Phone_Number, Sex, Ethnicity) Value('{fname}','{lname}',{mname},'{dob}',{streetnum},'{streetname}',{aptnum},'{city}',{state_id},{zipcode},'{email}','{phonenum}','{sex}','{ethnicity}')") 
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
    insert_string = (f"INSERT INTO LOG_IN(User_ID, Username, Password_Hash) VALUE({hos_id},'{username}',MD5('{password}'))")
    qe.connect()
    qe.do_query(insert_string)
    qe.commit()
    qe.disconnect()

  #def insert_patient(primary_dr, insurance_id, ins_name, ins_expr, ins_phone):
def insert_staff(username, office_loc, work_date):
    query_string = (f"SELECT User_ID FROM LOG_IN WHERE UserName = '{username}'")
    qe.connect()
    hos_id = qe.do_query(query_string)
    qe.disconnect()
    hos_id = hos_id[0][0]
    print(hos_id)
    query_string = (f"SELECT Office_ID FROM OFFICE WHERE Office_Name = '{office_loc}'")
    qe.connect()
    office_id = qe.do_query(query_string)
    qe.disconnect()
    office_id = office_id[0][0]
    print(office_id)
    staff_date = ""
    for d in work_date:
      staff_date = staff_date + d
    print(staff_date)
    insert_string = (f"INSERT INTO STAFF(Staff_ID, Office_Location_ID,Employed_Since,Working_date) VALUE({hos_id},{office_id},CURDATE(),'{staff_date}')")
    print(insert_string)
    qe.connect()
    qe.do_query(insert_string)
    qe.commit()
    qe.disconnect()




