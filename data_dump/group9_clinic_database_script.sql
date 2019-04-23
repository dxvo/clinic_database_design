
CREATE TABLE `general_info` (
  `Hospital_ID` int(8) unsigned zerofill NOT NULL AUTO_INCREMENT,
  `First_Name` varchar(15) COLLATE utf8_unicode_ci NOT NULL,
  `Last_Name` varchar(20) COLLATE utf8_unicode_ci NOT NULL,
  `Middle_Initial` char(1) COLLATE utf8_unicode_ci DEFAULT NULL,
  `DOB` date NOT NULL,
  `Street_Number` int(8) NOT NULL,
  `Street_Name` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  `Apt_Number` int(5) DEFAULT NULL,
  `City` varchar(20) COLLATE utf8_unicode_ci NOT NULL,
  `State_ID` int(2) NOT NULL,
  `Zipcode` int(5) NOT NULL,
  `Email` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  `Phone_Number` varchar(10) COLLATE utf8_unicode_ci NOT NULL,
  `Sex` enum('male','female') COLLATE utf8_unicode_ci NOT NULL,
  `Ethnicity` enum('White','African American','Asian','Native American','Pacific Islanders','Hispanic','Others') COLLATE utf8_unicode_ci DEFAULT NULL,
  `Created_At` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `Last_Updated` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  PRIMARY KEY (`Hospital_ID`),
  UNIQUE KEY `Email` (`Email`),
  UNIQUE KEY `Hospital_ID_UNIQUE` (`Hospital_ID`),
  UNIQUE KEY `Email_UNIQUE` (`Email`),
  KEY `gen_info.state_fk_state.state_id` (`State_ID`),
  CONSTRAINT `gen_info.state_fk_state.state_id` FOREIGN KEY (`State_ID`) REFERENCES `state` (`State_ID`)
) ENGINE=InnoDB AUTO_INCREMENT=1081 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci



CREATE TABLE `office` (
  `Office_ID` int(5) unsigned zerofill NOT NULL AUTO_INCREMENT,
  `Office_Name` varchar(25) COLLATE utf8_unicode_ci NOT NULL,
  `Street_Number` int(6) unsigned NOT NULL,
  `Street_Name` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  `City` varchar(20) COLLATE utf8_unicode_ci NOT NULL,
  `State_ID` int(2) NOT NULL,
  `Zipcode` int(5) unsigned NOT NULL,
  PRIMARY KEY (`Office_ID`),
  UNIQUE KEY `Office_ID_UNIQUE` (`Office_ID`),
  UNIQUE KEY `Office_Name_UNIQUE` (`Office_Name`),
  KEY `office.state_fk_state.state_id` (`State_ID`),
  CONSTRAINT `office.state_fk_state.state_id` FOREIGN KEY (`State_ID`) REFERENCES `state` (`State_ID`)
) ENGINE=InnoDB AUTO_INCREMENT=19 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci


CREATE TABLE `patient` (
  `Patient_ID` int(8) unsigned zerofill NOT NULL,
  `Patient_Since` date DEFAULT NULL,
  `Insurance_ID` int(7) unsigned zerofill DEFAULT NULL,
  `Primary_physician_ID` int(8) unsigned zerofill NOT NULL,
  `Approval_Status` enum('T','F') COLLATE utf8_unicode_ci NOT NULL DEFAULT 'F',
  PRIMARY KEY (`Patient_ID`),
  UNIQUE KEY `Patient_ID_UNIQUE` (`Patient_ID`),
  KEY `Patient.physican_ID_fk_doctor.doctor_id` (`Primary_physician_ID`),
  KEY `PATIENT.physian_id_fk_INSURANCE_INFO.Insurance_ID_idx` (`Insurance_ID`),
  CONSTRAINT `PATIENT.Insurance_id_fk_INSURANCE_INFO.Insurance_ID` FOREIGN KEY (`Insurance_ID`) REFERENCES `insurance_info` (`Insurance_ID`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `Patient.physican_ID_fk_doctor.doctor_id` FOREIGN KEY (`Primary_physician_ID`) REFERENCES `doctor` (`Doctor_ID`),
  CONSTRAINT `patient.patient_ID_fk_general_info.hospital_id` FOREIGN KEY (`Patient_ID`) REFERENCES `general_info` (`Hospital_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci


CREATE TABLE `admin` (
  `Admin_ID` int(8) unsigned zerofill NOT NULL,
  PRIMARY KEY (`Admin_ID`),
  CONSTRAINT `ADMIN.Amin_ID_FK_GENERALINFO.Hospital_ID` FOREIGN KEY (`Admin_ID`) REFERENCES `general_info` (`Hospital_ID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci


CREATE TABLE `doctor` (
  `Doctor_ID` int(8) unsigned zerofill NOT NULL,
  `Specialization_ID` int(3) NOT NULL,
  `Employed_Since` date NOT NULL,
  `Employment_Status` enum('Employed','Not Employed') COLLATE utf8_unicode_ci DEFAULT 'Employed',
  PRIMARY KEY (`Doctor_ID`),
  UNIQUE KEY `Doctor_ID_UNIQUE` (`Doctor_ID`),
  KEY `Doctor.specialized_id_fk_specialization.specialization_id` (`Specialization_ID`),
  CONSTRAINT `Doctor.specialized_id_fk_specialization.specialization_id` FOREIGN KEY (`Specialization_ID`) REFERENCES `specialization` (`Specialization_ID`),
  CONSTRAINT `doctor.doctor_id_fk_general_information.hospital_id` FOREIGN KEY (`Doctor_ID`) REFERENCES `general_info` (`Hospital_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci


CREATE TABLE `staff` (
  `Staff_ID` int(8) unsigned zerofill NOT NULL,
  `Office_Location_ID` int(5) unsigned zerofill NOT NULL,
  `Employed_Since` date NOT NULL,
  `Working_date` char(11) COLLATE utf8_unicode_ci NOT NULL,
  `Employment_Status` enum('Employed','Unemployed') COLLATE utf8_unicode_ci NOT NULL DEFAULT 'Employed',
  PRIMARY KEY (`Staff_ID`),
  KEY `STAFF.Office_Location_ID_fk_OFFICE.Office_ID` (`Office_Location_ID`),
  CONSTRAINT `STAFF.Office_Location_ID_fk_OFFICE.Office_ID` FOREIGN KEY (`Office_Location_ID`) REFERENCES `office` (`Office_ID`),
  CONSTRAINT `STAFF.Staff_ID_fk_general_info.hospital_id` FOREIGN KEY (`Staff_ID`) REFERENCES `general_info` (`Hospital_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci


CREATE TABLE `appointment` (
  `Appt_ID` int(10) unsigned zerofill NOT NULL AUTO_INCREMENT,
  `App_Type` enum('Specialist','General') COLLATE utf8_unicode_ci NOT NULL,
  `App_date` date NOT NULL,
  `App_hour` int(2) NOT NULL,
  `Created_At` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `Last_Updated` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `Confirm_By` int(8) unsigned zerofill DEFAULT NULL,
  `With_Doctor` int(8) unsigned zerofill NOT NULL,
  `Patient_ID` int(8) unsigned zerofill NOT NULL,
  `App_Location_ID` int(5) unsigned zerofill NOT NULL,
  `Appt_Status` enum('Booked','Cancelled','Completed','Process') COLLATE utf8_unicode_ci NOT NULL DEFAULT 'Booked',
  PRIMARY KEY (`Appt_ID`),
  UNIQUE KEY `Appt_ID_UNIQUE` (`Appt_ID`),
  KEY `APPOINTMENT.with_doctor_FK_DOCTOR.doctor_id` (`With_Doctor`),
  KEY `APPOINTMENT.App_Location_ID_FK_OFFICE.office_id` (`App_Location_ID`),
  KEY `APPOINTMENT.patient_id_FK_PATIENT.patient_id` (`Patient_ID`),
  KEY `APPOINTMENT.Confirm_By_FK_STAFF.staff_id` (`Confirm_By`),
  CONSTRAINT `APPOINTMENT.App_Location_ID_FK_OFFICE.office_id` FOREIGN KEY (`App_Location_ID`) REFERENCES `office` (`Office_ID`),
  CONSTRAINT `APPOINTMENT.Confirm_By_FK_STAFF.staff_id` FOREIGN KEY (`Confirm_By`) REFERENCES `staff` (`Staff_ID`),
  CONSTRAINT `APPOINTMENT.patient_id_FK_PATIENT.patient_id` FOREIGN KEY (`Patient_ID`) REFERENCES `patient` (`Patient_ID`),
  CONSTRAINT `APPOINTMENT.with_doctor_FK_DOCTOR.doctor_id` FOREIGN KEY (`With_Doctor`) REFERENCES `doctor` (`Doctor_ID`)
) ENGINE=InnoDB AUTO_INCREMENT=1000000713 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci


CREATE TABLE `blood_test_result` (
  `Blood_test_id` int(7) unsigned zerofill NOT NULL AUTO_INCREMENT,
  `White_blood_Cell_Count` decimal(10,0) unsigned DEFAULT NULL,
  `Red_blood_Cell_Count` decimal(10,0) unsigned DEFAULT NULL,
  `Hemoglobin` decimal(10,0) unsigned DEFAULT NULL,
  `Hematocrit` decimal(10,0) unsigned DEFAULT NULL,
  `MCV` decimal(10,0) unsigned DEFAULT NULL,
  `MCH` decimal(10,0) unsigned DEFAULT NULL,
  `RDW` decimal(10,0) unsigned DEFAULT NULL,
  `Platelet_Count` decimal(10,0) unsigned DEFAULT NULL,
  `Lymphocyte` decimal(10,0) unsigned DEFAULT NULL,
  `Monocyte` decimal(10,0) unsigned DEFAULT NULL,
  `Cholesterol` decimal(10,0) unsigned DEFAULT NULL,
  `Iron` decimal(10,0) unsigned DEFAULT NULL,
  `Sodium` decimal(10,0) unsigned DEFAULT NULL,
  `Potassium` decimal(10,0) unsigned DEFAULT NULL,
  `Appt_ID` int(10) unsigned zerofill NOT NULL,
  PRIMARY KEY (`Blood_test_id`),
  KEY `BloodResult.Blood_ID_FK_PostAppt.Blood_ID_idx` (`Appt_ID`),
  CONSTRAINT `BLOODRESULT.Appt_ID_FK_POSTAPPT.Appt_ID` FOREIGN KEY (`Appt_ID`) REFERENCES `post_appointment` (`Appointment_ID`) ON DELETE NO ACTION ON UPDATE NO ACTION
) ENGINE=InnoDB AUTO_INCREMENT=7 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci



CREATE TABLE `doctor_office` (
  `Office_ID` int(5) unsigned zerofill NOT NULL,
  `Doctor_ID` int(8) unsigned zerofill NOT NULL,
  `Start_Date` date NOT NULL,
  `End_Date` date DEFAULT NULL,
  `Working_date` char(11) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`Office_ID`,`Doctor_ID`,`Start_Date`),
  KEY `DOCTOR_OFFICE.doctor_id_fk_DOCTOR.doctor_id` (`Doctor_ID`),
  CONSTRAINT `DOCTOR_OFFICE.doctor_id_fk_DOCTOR.doctor_id` FOREIGN KEY (`Doctor_ID`) REFERENCES `doctor` (`Doctor_ID`),
  CONSTRAINT `DOCTOR_OFFICE.office_id_fk_OFFICE.doctor_id` FOREIGN KEY (`Office_ID`) REFERENCES `office` (`Office_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci

CREATE TABLE `health_profile` (
  `Health_Profile_ID` int(8) unsigned zerofill NOT NULL,
  `BloodType` enum('A+','A-','B+','B-','AB+','AB-','O+','O-') COLLATE utf8_unicode_ci DEFAULT NULL,
  `Health_Summary` varchar(100) COLLATE utf8_unicode_ci DEFAULT NULL,
  `Height` decimal(5,2) unsigned DEFAULT NULL,
  `Weight` decimal(5,2) unsigned DEFAULT NULL,
  PRIMARY KEY (`Health_Profile_ID`),
  CONSTRAINT `HEALTH_PROFILE.Health_Profile_ID_FK_PATIENT.patient_id` FOREIGN KEY (`Health_Profile_ID`) REFERENCES `patient` (`Patient_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci


CREATE TABLE `insurance_info` (
  `Insurance_ID` int(7) unsigned zerofill NOT NULL,
  `Insurance_Name` varchar(30) COLLATE utf8_unicode_ci DEFAULT NULL,
  `Deductible` decimal(13,2) DEFAULT NULL,
  `Expiration` date DEFAULT NULL,
  `Insur_Phone` varchar(10) COLLATE utf8_unicode_ci DEFAULT NULL,
  PRIMARY KEY (`Insurance_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci


CREATE TABLE `log_in` (
  `User_ID` int(8) unsigned zerofill NOT NULL,
  `UserName` varchar(20) COLLATE utf8_unicode_ci NOT NULL,
  `Password_Hash` varchar(72) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`User_ID`),
  UNIQUE KEY `UserName_UNIQUE` (`UserName`),
  CONSTRAINT `login.user_Id_fk_general_info.hospital_id` FOREIGN KEY (`User_ID`) REFERENCES `general_info` (`Hospital_ID`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci



CREATE TABLE `post_appointment` (
  `Appointment_ID` int(10) unsigned zerofill NOT NULL,
  `Doctor_Diagnosis` varchar(200) COLLATE utf8_unicode_ci NOT NULL,
  `Balance_Due` decimal(13,2) NOT NULL,
  `Blood_Test_ID` int(7) unsigned DEFAULT NULL,
  `Prescription_ID` int(10) unsigned zerofill DEFAULT NULL,
  PRIMARY KEY (`Appointment_ID`),
  KEY `POST_APPT.Blood_Test_ID_FK_BLOOD_RESULT.Blood_test_id` (`Blood_Test_ID`),
  KEY `POST_APPT.PrescriptID_FK_PRESCRIPTION.PrescriptID_idx` (`Prescription_ID`),
  CONSTRAINT `POST_APPOINTMENT.Appointment_ID_FK_APPOINTMENT.appt_id` FOREIGN KEY (`Appointment_ID`) REFERENCES `appointment` (`Appt_ID`),
  CONSTRAINT `POST_APPT.Blood_Test_ID_FK_BLOOD_RESULT.Blood_test_id` FOREIGN KEY (`Blood_Test_ID`) REFERENCES `blood_test_result` (`Blood_test_id`) ON DELETE SET NULL ON UPDATE CASCADE,
  CONSTRAINT `POST_APPT.PrescriptID_FK_PRESCRIPTION.PrescriptID` FOREIGN KEY (`Prescription_ID`) REFERENCES `prescription` (`Prescription_ID`) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci


CREATE TABLE `prescription` (
  `Prescription_ID` int(10) unsigned zerofill NOT NULL AUTO_INCREMENT,
  `Drug_Name` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  `Assigned_By` int(8) unsigned zerofill NOT NULL,
  `Usage_Note` varchar(100) COLLATE utf8_unicode_ci NOT NULL,
  `Num_Refill` int(2) unsigned NOT NULL,
  `Patient_ID` int(8) unsigned zerofill NOT NULL,
  `Appt_ID` int(10) unsigned zerofill DEFAULT NULL,
  PRIMARY KEY (`Prescription_ID`),
  UNIQUE KEY `Prescription_ID_UNIQUE` (`Prescription_ID`),
  KEY `fk_Prescription_Patient_idx` (`Patient_ID`),
  KEY `PRESCRIPTION.Assigned_By_FK_DOCTOR.Doctor_ID` (`Assigned_By`),
  KEY `PRESCRIPTION.Appt_ID_FK_PostAppt.Appt_ID_idx` (`Appt_ID`),
  CONSTRAINT `PRESCRIPTION.Appt_ID_FK_POSTAPPT.Appt_ID` FOREIGN KEY (`Appt_ID`) REFERENCES `post_appointment` (`Appointment_ID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `PRESCRIPTION.Assigned_By_FK_DOCTOR.Doctor_ID` FOREIGN KEY (`Assigned_By`) REFERENCES `doctor` (`Doctor_ID`),
  CONSTRAINT `PRESCRIPTION.Patient_ID_FK_PATIENT.patient_id` FOREIGN KEY (`Patient_ID`) REFERENCES `patient` (`Patient_ID`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci


CREATE TABLE `specialistrequest` (
  `Requested_ID` int(8) unsigned zerofill NOT NULL AUTO_INCREMENT,
  `Doctor_ID` int(8) unsigned zerofill NOT NULL,
  `Patient_ID` int(8) unsigned zerofill NOT NULL,
  `Requested_Status` enum('Pending','Approved','Denied') NOT NULL,
  `Requested_Date` datetime NOT NULL,
  `Requested_Reason` varchar(100) NOT NULL,
  PRIMARY KEY (`Requested_ID`),
  KEY `FK_Patient_ID_idx` (`Patient_ID`),
  KEY `FK_Doctor_ID_idx` (`Doctor_ID`),
  CONSTRAINT `FK_Doctor_ID` FOREIGN KEY (`Doctor_ID`) REFERENCES `patient` (`Primary_physician_ID`) ON DELETE NO ACTION ON UPDATE NO ACTION,
  CONSTRAINT `FK_Patient_ID` FOREIGN KEY (`Patient_ID`) REFERENCES `patient` (`Patient_ID`)
) ENGINE=InnoDB AUTO_INCREMENT=80 DEFAULT CHARSET=utf8


CREATE TABLE `specialization` (
  `Specialization_ID` int(3) NOT NULL AUTO_INCREMENT,
  `Type` varchar(30) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`Specialization_ID`),
  UNIQUE KEY `Type` (`Type`)
) ENGINE=InnoDB AUTO_INCREMENT=22 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci



CREATE TABLE `state` (
  `State_ID` int(2) NOT NULL AUTO_INCREMENT,
  `State_code` char(2) COLLATE utf8_unicode_ci NOT NULL,
  `State_name` varchar(20) COLLATE utf8_unicode_ci NOT NULL,
  PRIMARY KEY (`State_ID`),
  UNIQUE KEY `State_code` (`State_code`),
  UNIQUE KEY `State_name` (`State_name`)
) ENGINE=InnoDB AUTO_INCREMENT=53 DEFAULT CHARSET=utf8 COLLATE=utf8_unicode_ci




CREATE DEFINER=`devodevo`@`%` TRIGGER `medical_clinic`.`appointment_AFTER_INSERT` AFTER INSERT ON `appointment` FOR EACH ROW
BEGIN
IF (new.App_Type = 'Specialist') THEN
    UPDATE patient
    SET Approval_Status = 'F'
    WHERE new.Patient_ID = patient.Patient_ID;
    END IF;
END



CREATE DEFINER=`devodevo`@`%` TRIGGER `medical_clinic`.`appointment_BEFORE_UPDATE` BEFORE UPDATE ON `appointment` FOR EACH ROW
BEGIN
IF (old.Confirm_By is Null and new.Confirm_By is not Null) THEN
set new.Appt_Status = 'Process';
set new.Last_Updated = NOW();
end if;
END


CREATE DEFINER=`devodevo`@`%` TRIGGER `medical_clinic`.`specialistrequest_AFTER_UPDATE` AFTER UPDATE ON `specialistrequest` FOR EACH ROW
BEGIN
	IF(new.Requested_Status = 'Approved') THEN 
    UPDATE patient
    SET Approval_Status = 'T'
    WHERE new.Patient_ID = patient.Patient_ID;
    END IF;
END