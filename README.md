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

### TRIGGER
- We have total 3 triggers: 2 triggers under appointment table and another trigger under specialistrequest

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


