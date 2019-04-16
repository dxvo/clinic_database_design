#worksheet1
SELECT * FROM heroku_5c85c34484343c5.appointment


-- Get staff and doctor working together same office
SELECT Staff_ID,Doctor_ID,Office_Name
FROM doctor_office,staff,office
WHERE  staff.Office_Location_ID =  doctor_office.Office_ID AND office.Office_ID = doctor_office.Office_ID
