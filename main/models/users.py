from . import base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Sequence
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

class Person(base.Model):
    __tablename__ = 'person'
    id = Column(Integer, primary_key=True)
    user_type = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False)
    first_name = Column(String, index=True)
    last_name = Column(String, nullable=False, index=True)
    profile_id = Column(Integer, ForeignKey("profile.id"))
    profile = relationship("Profile", back_populates="persons")
    __mapper_args__ = {'polymorphic_identity': 'person', 'polymorphic_on': user_type}

    def __init__(self, formData = None):
        self.is_active = True
        if formData != None:
            self.hashed_password = generate_password_hash(formData["password"])
            self.email = formData["email"]
            self.username = formData["username"]
            self.last_name = formData["last_name"]
            self.first_name = formData["first_name"] if "first_name" in formData else None
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
            else: 
                return "ERROR_USER_NOT_FOUND"
        except Exception as err:
            return "ERROR"

    def fetchPersons(self, db, queryFields = None, queryParams = None, queryLimit = None):
        return db.fetchData('person', queryFields, queryParams, queryLimit)

    def fetchByUserId(self, db, userIds = []):
        if userIds != [] and userIds != None:
            if isinstance(userIds, str):   
                params = 'id IN \'' + userIds + '\'' 
            elif isinstance(userIds, list):
                params = 'id IN (' + ','.join([ '\'' + usr + '\'' for usr in userIds]) + ')' 
            params += ' AND person.profile_id = profile.id' 
            return db.fetchData('person, profile', 'person.id, email, username, first_name, last_name, profile.profile_name', params, None) 
        return "ERROR_MISSING_USERIDS"

    def fetchByUsername(self, db, usernames = []):
        if usernames != [] and usernames != None:
            if isinstance(usernames, str):   
                params = 'username = \'' + usernames + '\'' 
            elif isinstance(usernames, list):
                params = 'username IN (' + ','.join([ '\'' + usr + '\'' for usr in usernames]) + ')' 
            return self.fetchPersons(db, 'id, email, hashed_password, username, first_name, last_name', params, None) 
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
    __mapper_args__ = {'polymorphic_identity': 'employee'}
    __tablename__ = 'employee'
    person_id = Column(None, ForeignKey('person.id'), primary_key=True)
    employee_id = Column(Integer, Sequence("employee_id_seq", start=1000), primary_key=True)
    num_vacations = Column(Integer)

    def __init__(self):
        pass

    def createEmployeeForm(self, db, formData):   
        self.user_type = "employee"
        self.num_vacations = 30
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
                return "COMMIT_ERROR_" + commitStatus
        except Exception as err:
            return "ERROR : " + str(err)
    
    def fetchEmployeesWithDetails(self, db, queryFields = None, queryParams = None, queryLimit = None):
        return db.fetchData('employee, person, profile', queryFields, queryParams, queryLimit)        

class External(Person):
    __mapper_args__ = {'polymorphic_identity': 'external'}
    __tablename__ = 'external'
    id = Column(None, ForeignKey('person.id'), primary_key=True)
    ext_type = Column(String)
    account_id = Column(None, ForeignKey('account.id'))
    account = relationship("Account", back_populates="external_persons")
    contract_period_days = Column(Integer)

    def __init__(self):
        pass

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
                return "COMMIT_ERROR_" + commitStatus
        except Exception as err:
            return "ERROR : " + str(err) 

class Candidate(Person):
    __mapper_args__ = {'polymorphic_identity': 'candidate'}
    __tablename__ = 'candidate'
    id = Column(None, ForeignKey('person.id'), primary_key=True)
    num_residents = Column(Integer)

    def __init__(self):
        pass

    def createCandidateForm(self, db, formData):
        self.user_type = "candidate"
        self.num_vacations = 30
        super(Candidate, self).__init__(formData) 
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
            if commitStatus != "SUCCESS":
                return "INSERTED_CANDIDATE"
            else:
                return "COMMIT_ERROR_" + commitStatus
        except Exception as err:
            return "ERROR : " + str(err)

