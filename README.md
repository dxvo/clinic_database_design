# Clinic Database Design

### Remote database connection via MYSQL workbench  
- host: uh-mysqldbserver.mysql.database.azure.com
- username:  devodevo@uh-mysqldbserver
- password: Bank6you

### Instruction for Testing 
Database contains 4 different account types: Admin, staff, doctor and patient 
- Patient can register themselves from the website. 
- Admin has the ability to add more staff, doctor or clinic location into database. 
- ADMIN log in information: 
        - admin username: admin
        - admin password: password

### Patient Functionality
- Patient can register a new account from website. 
- patient can view info their past appointment (such as diagnosis,..)
- patient  can schedule an appointment or make edit 
- patient can order prescription 
- Patient needs approval from primary physician to make specialist appointment 

### Staff functionality 
- Staff can check in patient during appointment 
- staff can update lab result post appointment 
- staff can access report to view information about a particular office that he/she works for. 
- staff can also look up a particular past appointment
- staff can also make appointment for patient over the phone 

### TRIGGER
- We have total 3 triggers: 2 triggers under appointment table and another trigger under specialistrequest
- After Patient makes appointment with a Specialist, he/she will lose the approval from his/her primary physician (Approval Status in Patient will be False).
- After Staff checks in an appointment, that appointment status will be changed to Process.
- Like mentioned above the final trigger is like the first but reversed. So when a patient requests for a specialist approval the doctor can either deny or approve it. If the doctor approves it the trigger is triggered to set the patients permission to schedule with a specialist to true.

### REPORTS 
- WE have total 3 reports 
- 2 reports can be viewed from admin profile 
- 1 report can be viewed from staff account log in. 


### Log in infomation 
- There are some accounts already register in the database. All accounts are registered with `password` as password. 
- Example for patient 
    - username: pat1 
    - password: password 
- Log in for doctor 
    - username: doc1 
    - password: password
- log in for staff
    - username: staff1
    - password: password


