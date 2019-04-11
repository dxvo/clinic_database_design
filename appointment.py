import datetime

from QueryEngine import QueryEngine

qe = QueryEngine()
qe.setup_default()

def date_from_string(date):
  # Converts string-date to datetime.date object
  year = int(date[0:4])
  month = int(date[5:7])
  day = int(date[8:10])
  return datetime.date(year, month, day)

def doctor_location(doctor, app_date):
  # Returns Office_ID of doctor on any given date
  query_string = '''SELECT Working_date, Office_ID
                    FROM doctor_office
                    WHERE Doctor_ID = {} AND End_Date is NULL'''
  qe.connect()
  results = qe.do_query(query_string.format(doctor))
  qe.disconnect()
  weekdays = ["M", "Tu", "W", "Th", "F", "Sa", "Su"]
  schedule = weekdays[date_from_string(app_date).weekday()]
  for location in results:
    if schedule in location[0]: 
      return location[1]

def doctor_locations(doctor):
  # Returns list of all locations/offices for doctor
  query_string = '''SELECT Office_Name
                    FROM doctor_office, office
                    WHERE doctor_office.Doctor_ID = {} AND doctor_office.Office_ID = office.Office_ID'''
  qe.connect()
  results = qe.do_query(query_string.format(doctor))
  qe.disconnect()
  # Make list
  office_list = []
  for r in results:
    office_list.append(r[0])
  return office_list

def doctor_reserved_times(doctor, date):
  # Returns a list of time slots UNAVAILABLE in 24-hour time (Ex. 1:00pm = 13, 4:00pm = 16)
  query_string = '''SELECT App_hour
                    FROM appointment
                    WHERE App_date = '{}' AND With_Doctor = {}'''
  qe.connect()
  results = qe.do_query(query_string.format(date, doctor))
  qe.disconnect()
  # Array of restricted/already-booked slots
  reserved_slots = []
  for slot in results:
    reserved_slots.append(slot[0])
  return reserved_slots


def doctor_available(doctor, date, hour):
  # Returns whether or not a doctor is available for an appointment at a specified date and hour/slot
  query_string = '''SELECT * 
                    FROM appointment
                    WHERE App_date = '{}' AND App_hour = {} AND With_Doctor = {}'''
  qe.connect()
  results = qe.do_query(query_string.format(date, hour, doctor))
  qe.disconnect()
  return (len(results) == 0)

def doctor_list():
  # Returns list of doctors information
  # (ID, First_Name, Last_Name, Specialization, [Locations])
  query_string = '''SELECT doctor.Doctor_ID, general_info.First_Name, general_info.Last_Name, specialization.type
                    FROM doctor, general_info, specialization
                    WHERE doctor.Specialization_ID = specialization.Specialization_ID AND doctor.Doctor_ID = general_info.Hospital_ID'''
  qe.connect()
  results_doctors = qe.do_query(query_string)
  qe.disconnect()
  # Copy results
  doctors = []  
  for r in results_doctors:
    doctor = []
    for attr in r:
      doctor.append(attr)
    # Attach doctor's locations
    doctor_id = doctor[0]
    doctor.append(doctor_locations(doctor_id))
    doctors.append(doctor)
  return doctors

