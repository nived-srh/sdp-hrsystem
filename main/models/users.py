from . import base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Sequence, LargeBinary, Date
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

class Person(base.Model):
    __tablename__ = 'person'
    id = Column(Integer, primary_key=True)
    user_type = Column(String, nullable=False)
    user_status = Column(String, nullable=False)
    user_dob = Column(Date)
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    last_name = Column(String, nullable=False, index=True)
    first_name = Column(String, index=True)
    salutation = Column(String)
    addr_line = Column(String)
    addr_city = Column(String)
    addr_state = Column(String)
    addr_country = Column(String)
    addr_zip = Column(String)
    profile_id = Column(Integer, ForeignKey("profile.id"))
    profile = relationship("Profile", back_populates="persons")
    __mapper_args__ = {'polymorphic_identity': 'person', 'polymorphic_on': user_type}

    def __init__(self, formData = None):
        self.user_status = "ACTIVE"
        if formData != None:
            self.hashed_password = generate_password_hash(formData["password"], method='pbkdf2:sha256', salt_length=8)
            self.email = formData["email"]
            self.username = formData["username"]
            self.last_name = formData["last_name"]
            self.user_dob = formData["date_of_birth"] if "first_name" in formData else None
            self.first_name = formData["first_name"] if "first_name" in formData else ""
            self.salutation = formData["salutation"] if "salutation" in formData else ""
            self.addr_line = formData["addr_line"] if "addr_line" in formData else ""
            self.addr_city = formData["addr_city"] if "addr_city" in formData else ""
            self.addr_state = formData["addr_state"] if "addr_state" in formData else ""
            self.addr_country = formData["addr_country"] if "addr_country" in formData else ""
            self.addr_zip = formData["addr_zip"] if "addr_zip" in formData else ""

            if "profile_id" in formData:
                self.profile_id = formData["profile_id"]
            elif "profile" in formData:
                self.profile = formData["profile"]

    def validatePerson(self, db, username, password):
        try:
            result = self.fetchByUsername(db, username)
            if result != None:
                for row in result:
                    if check_password_hash(row.hashed_password,password):
                        return row
                    else:
                        return "ERROR_INVALID_CREDENTIALS"
            return "ERROR_USER_NOT_FOUND"
        except Exception as err:
            return "ERROR : " + str(err)

    def fetchPersons(self, db, queryFields = None, queryParams = None, queryLimit = None):
        return db.fetchData('person', queryFields, queryParams, queryLimit)

    def fetchByUserId(self, db, userIds = []):
        if userIds != [] and userIds != None:
            if isinstance(userIds, str):   
                params = 'person.id = \'' + userIds + '\'' 
            elif isinstance(userIds, list):
                params = 'person.id IN (' + ','.join([ '\'' + usr + '\'' for usr in userIds]) + ')' 
            params += ' AND person.profile_id = profile.id' 
            return db.fetchData('person, profile', 'person.id, email, username, first_name, last_name, profile.profile_name', params, None) 
        return "ERROR_MISSING_USERIDS"

    def fetchByUsername(self, db, usernames = []):
        if usernames != [] and usernames != None:
            if isinstance(usernames, str):   
                params = 'username = \'' + usernames + '\'' 
            elif isinstance(usernames, list):
                params = 'username IN (' + ','.join([ '\'' + usr + '\'' for usr in usernames]) + ')' 
            return self.fetchPersons(db, 'id, email, hashed_password, username, first_name, last_name, user_type', params) 
        return "ERROR_MISSING_USERNAMES"

    def changePassword(self, db, username, oldpassword, newpassword):        
        session = db.initiateSession()
        userRecord = session.query(Person).filter(Person.username==username).first()     
        if userRecord != None:
            if check_password_hash(userRecord.hashed_password,oldpassword): 
                userRecord.hashed_password = generate_password_hash(newpassword, method='pbkdf2:sha256', salt_length=8)
                commitStatus = db.commitSession(session)
                return commitStatus
            else:
                return "ERROR_INCORRECT_OLD_PASSWORD"
        return "ERROR_MISSING_USERNAMES"

    ''' Methods overrode by child insert methods
    def createPersonForm(self, db, formData):
        self.hashed_password = generate_password_hash(formData["password"])
        self.email = formData["username"]
        self.username = formData["username"]
        #self.user_type = formData["user_type"]
        self.last_name = formData["user_type"] if formData["user_type"] != None else "employee"
        return self.createPerson(db)

    def createPerson(self, db):
        existingUsers = None #self.fetchUsers(db, username)
        if existingUsers == None or existingUsers == []:
            try:
                session = db.initiateSession()                
                session.add(self)
                commitStatus = db.commitSession(session, False)
                if commitStatus != "Success":
                    return "INSERTED_USER"
                else:
                    return "ERR:" + commitStatus
            except Exception as err:
                return "ERR:"
        else:
            return "DUPLICATE_USER"
    '''        

class Employee(Person):
    __tablename__ = 'employee'
    person_id = Column(None, ForeignKey('person.id'), primary_key=True)
    manager_id = Column(None, ForeignKey('person.id'))
    employee_id = Column(Integer, Sequence("employee_id_seq", start=1000), primary_key=True)
    num_vacations = Column(Integer)
    tier_id = Column(Integer, ForeignKey("tier.id"))
    tier = relationship("Tier", back_populates="persons")
    __mapper_args__ = dict(polymorphic_identity = 'employee', inherit_condition = (person_id == Person.id))

    def __init__(self):
        super().__init__()

    def createEmployeeForm(self, db, formData):   
        self.user_type = "employee"
        self.num_vacations = 30
        self.tier_id = formData["tier_id"] if "tier_id" in formData else None
        super(Employee, self).__init__(formData)     
        existingUsers = self.fetchByUsername(db, self.username)
        if existingUsers == None or list(existingUsers) == []:
            return self.createEmployee(db)
        else:
            return "DUPLICATE_USER"

    def createEmployee(self, db):        
        try:
            session = db.initiateSession()                
            session.add(self)
            commitStatus = db.commitSession(session, False)
            if commitStatus == "SUCCESS":
                return "INSERTED_EMPLOYEE"
            else:
                return "ERROR_DBCOMMIT"
        except Exception as err:
            return "ERROR : " + str(err)
    
    def editEmployeeForm(self, db, formData):
        session = db.initiateSession()
        recordToEdit = session.query(Employee).filter(Person.id==formData["person_id"]).first()
        recordToEdit.email = formData["email"]  
        recordToEdit.username = formData["email"]
        recordToEdit.first_name = formData["first_name"]  
        recordToEdit.last_name = formData["last_name"]
        recordToEdit.salutation = formData["salutation"]  
        recordToEdit.tier_id = formData["tier_id"] if "tier_id" in formData else recordToEdit.tier_id
        recordToEdit.addr_line = formData["addr_line"] if "addr_line" in formData else recordToEdit.addr_line
        recordToEdit.addr_city = formData["addr_city"] if "addr_city" in formData else recordToEdit.addr_city
        recordToEdit.addr_state = formData["addr_state"] if "addr_state" in formData else recordToEdit.addr_state
        recordToEdit.addr_country = formData["addr_country"] if "addr_country" in formData else recordToEdit.addr_country
        recordToEdit.addr_zip = formData["addr_zip"] if "addr_zip" in formData else recordToEdit.addr_zip
        commitStatus = db.commitSession(session)
        return commitStatus

    def fetchManagers(self, db, queryFields = None, queryParams = None, queryLimit = None):
        queryParams = " employee.person_id = person.id AND person.profile_id = profile.id AND profile.profile_name LIKE '%MANAGER%' "
        return db.fetchData('employee, person, profile', "person.first_name, person.last_name, person.id", queryParams, queryLimit)        

    def fetchEmployeesWithDetails(self, db, queryFields = None, queryParams = None, queryLimit = None):
        for row in db.fetchData('employee, person, profile', queryFields, queryParams, queryLimit)        :
            print(str(row))
        return db.fetchData('employee, person, profile', queryFields, queryParams, queryLimit)        

class External(Person):
    __mapper_args__ = {'polymorphic_identity': 'external'}
    __tablename__ = 'external'
    person_id = Column(None, ForeignKey('person.id'), primary_key=True)
    ext_type = Column(String)
    account_id = Column(None, ForeignKey('account.id'))
    contract_period_days = Column(Integer)
    tier_id = Column(Integer, ForeignKey("tier.id"))
    account = relationship("Account", back_populates="external_persons")
    tier = relationship("Tier", back_populates="persons")

    def __init__(self):
        super().__init__()

    def createExternalForm(self, db, formData):
        self.user_type = "external"
        self.ext_type = formData["ext_type"]
        super(External, self).__init__(formData)  
        existingUsers = None#self.fetchByUsername(db, self.username)
        if existingUsers == None or list(existingUsers) == []:
            return self.createExternal(db)
        else:
            return "DUPLICATE_USER"

    def createExternal(self, db):
        try:
            session = db.initiateSession()                
            session.add(self)
            commitStatus = db.commitSession(session, False)
            print('TEst' , commitStatus)
            if commitStatus != "Success":
                return "INSERTED_EXTERNAL"
            else:
                return "ERROR_DBCOMMIT"
        except Exception as err:
            return "ERROR : " + str(err) 

    def fetchExternalsWithDetails(self, db, queryFields = None, queryParams = None, queryLimit = None):
        return db.fetchData('external, person, profile', queryFields, queryParams, queryLimit)    

class Candidate(Person):
    __mapper_args__ = {'polymorphic_identity': 'candidate'}
    __tablename__ = 'candidate'
    id = Column(None, ForeignKey('person.id'), primary_key=True)
    resume_filename = Column(String, default="")
    resume_filedata = Column(LargeBinary)
    edu_hightest = Column(String, default="")
    edu_hightest_institution = Column(String, default="")
    edu_hightest_grade = Column(String, default="")
    edu_hightest_year = Column(String, default="")
    work_exp_years = Column(Integer, default=0)
    work_exp_comment = Column(String, default="")
    linkedin_username = Column(String, default="")

    def __init__(self, formData = None):
        super().__init__()

    def createCandidateForm(self, db, formData):

        self.user_type = "candidate"
        formData["username"] = formData["email"]
        self.username = formData["username"]        
        super(Candidate, self).__init__(formData)  
        self.edu_hightest = formData["edu_hightest"] if "edu_hightest" in formData else ""
        self.edu_hightest_grade = formData["edu_hightest_grade"] if "edu_hightest_grade" in formData else ""
        self.edu_hightest_institution = formData["edu_hightest_institution"] if "edu_hightest_institution" in formData else ""
        self.edu_hightest_year = formData["edu_hightest_year"] if "edu_hightest_year" in formData else ""
        self.linkedin_username = formData["linkedin_username"] if "linkedin_username" in formData else ""
        self.work_exp_years = int(formData["work_exp_years"]) if "work_exp_years" in formData else 0
        self.work_exp_comment = formData["work_exp_comment"] if "work_exp_comment" in formData else ""
        existingUsers = self.fetchByUsername(db, self.username)
        if existingUsers == None or list(existingUsers) == []:
            return self.createCandidate(db)
        else:
            return "DUPLICATE_USER"

    def createCandidate(self, db):
        try:
            session = db.initiateSession()                
            session.add(self)
            commitStatus = db.commitSession(session, False)
            if commitStatus == "SUCCESS":
                return "INSERTED_CANDIDATE"
            else:
                return "ERROR_DBCOMMIT"
        except Exception as err:
            return "ERROR : " + str(err)

    def editCandidateForm(self, db, formData):
        session = db.initiateSession()
        candidateToEdit = session.query(Candidate).filter(Candidate.id==formData["candidate_id"]).first()        
        candidateToEdit.email = formData["email"]  
        candidateToEdit.username = formData["email"]
        candidateToEdit.first_name = formData["first_name"]  
        candidateToEdit.last_name = formData["last_name"]
        candidateToEdit.salutation = formData["salutation"]  
        candidateToEdit.edu_hightest = formData["edu_hightest"] if "edu_hightest" in formData else candidateToEdit.edu_hightest
        candidateToEdit.edu_hightest_grade = formData["edu_hightest_grade"] if "edu_hightest_grade" in formData else candidateToEdit.edu_hightest_grade
        candidateToEdit.edu_hightest_institution = formData["edu_hightest_institution"] if "edu_hightest_institution" in formData else candidateToEdit.edu_hightest_institution
        candidateToEdit.edu_hightest_year = formData["edu_hightest_year"] if "edu_hightest_year" in formData else candidateToEdit.edu_hightest_year
        candidateToEdit.linkedin_username = formData["linkedin_username"] if "linkedin_username" in formData else candidateToEdit.linkedin_username
        candidateToEdit.work_exp_years = int(formData["work_exp_years"]) if "work_exp_years" in formData else candidateToEdit.work_exp_years
        candidateToEdit.work_exp_comment = formData["work_exp_comment"] if "work_exp_comment" in formData else candidateToEdit.work_exp_comment

        commitStatus = db.commitSession(session)
        return commitStatus

    def uploadResume(self, db, formData):
        session = db.initiateSession()
        candidateToEdit = session.query(Candidate).filter(Person.id==formData["candidate_id"]).first()
        candidateToEdit.resume_filename = formData["candidate_resume"].filename
        candidateToEdit.resume_filedata = formData["candidate_resume"].read()
        commitStatus = db.commitSession(session)
        return commitStatus

    def fetchCandidateById(self, db, key):
        session = db.initiateSession()
        return session.query(Candidate).filter(Person.id==key).first()

    def fetchCandidatesWithDetails(self, db, queryFields = None, queryParams = None, queryLimit = None):
        return db.fetchData('candidate, person', queryFields, queryParams, queryLimit)    

    def validateCandidateOnApply(self, db, candidate_id):
        errors = []
        if candidate_id != None:
            session = db.initiateSession()
            recordToValidate = session.query(Candidate).filter(Candidate.id==str(candidate_id)).first()

            if recordToValidate.last_name == None or recordToValidate.last_name == "" :
                errors.append("- Last Name is required.")
            if recordToValidate.email == None or recordToValidate.email == "" :
                errors.append("- Email is required.")
            if recordToValidate.resume_filename == None or recordToValidate.resume_filename == "" :
                errors.append("- Resume is required. Please upload your Resume file as PDF.")
            if recordToValidate.edu_hightest == None or recordToValidate.edu_hightest == "" :
                errors.append("- All Education related fields should be updated.")
            if recordToValidate.edu_hightest_institution == None or recordToValidate.edu_hightest_institution == "" :
                errors.append("- All Education related fields should be updated.")
            if recordToValidate.edu_hightest_year == None or recordToValidate.edu_hightest_year == "" :
                errors.append("- All Education related fields should be updated.")
            if recordToValidate.edu_hightest_grade == None or recordToValidate.edu_hightest_grade == "" :
                errors.append("- All Education related fields should be updated.")

        return "SUCCESS" if errors == [] else "ERROR: Please update above details in 'My Application' section before applying.<br/>" '<br/>'.join([ item for item in errors])
        