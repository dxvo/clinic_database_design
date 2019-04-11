from QueryEngine import QueryEngine
from flask import flash

qe = QueryEngine()
qe.setup_default()

def login_check(username, password):
  qe.connect()
  check_acc = qe.do_query("select count(*) from log_in where UserName = '" + username + "' and Password_hash = md5('"+ password + "')" )
  count = check_acc[0][0]
  qe.disconnect()
  if count == 1:
    print("I am in")
   # flash(f'I am in')
    return True
  else:
    print("wrong account")
    #flash(f'Account not exist')
    return False

def account_type(username, password):
  login_id = get_login(username, password)
  qe.connect()
  patient_type = qe.do_query("select count(*) from patient where Patient_ID = " + str(login_id) )
  doctor_type = qe.do_query("select count(*) from doctor where Doctor_ID = " + str(login_id) )
  staff_type = qe.do_query("select count(*) from staff where Staff_ID = " + str(login_id) )
  qe.disconnect()
  if patient_type[0][0] == 1:
    return "patient"
  elif doctor_type[0][0] == 1:
    return "doctor"
  elif staff_type[0][0] == 1:
    return "staff"

def get_login(username, password):
  qe.connect()
  check_acc = qe.do_query("select User_ID from log_in where UserName = '" + username + "' and Password_hash = md5('"+ password + "')" )
  qe.disconnect()
  print("check_acc:", check_acc[0][0])
  return check_acc[0][0]

#login_check("lise_meitner","lise032978")


#print("logins:")
#for entry in logins:
 # print(entry)
  
#print("doctors:")
#for entry in doctors:
#  print('\t',entry)
