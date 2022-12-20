from . import base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
# {% if "Accounts" in response and response["Accounts"] != None %}

class Account(base.Model):
    __tablename__ = 'account'
    id = Column(Integer, primary_key=True)
    acc_name = Column(String, nullable=False, index=True)
    acc_type = Column(String, nullable=False, index=True)
    acc_status = Column(String, nullable=False, index=True, default="ACTIVE")
    addr_line = Column(String)
    addr_city = Column(String)
    addr_state = Column(String)
    addr_country = Column(String)
    addr_zip = Column(String)
    projects = relationship("Project", back_populates="account")
    external_persons = relationship("External", back_populates="account")

    def __init__(self, formData = None):
        if formData != None:
            self.acc_name = formData["acc_name"]
            self.acc_type = str(formData["acc_type"] if "acc_type" in formData else "").upper()
            self.acc_status = str(formData["acc_status"] if "acc_status" in formData else "").upper()
            self.addr_line = formData["addr_line"] if "addr_line" in formData else ""
            self.addr_city = formData["addr_city"] if "addr_city" in formData else ""
            self.addr_state = formData["addr_state"] if "addr_state" in formData else ""
            self.addr_country = formData["addr_country"] if "addr_country" in formData else ""
            self.addr_zip = formData["addr_zip"] if "addr_zip" in formData else ""

    def createAccountForm(self, db, formData):
        self.__init__(formData)
        return self.createAccount(db)

    def createAccount(self, db):
        try:
            session = db.initiateSession()
            session.add(self)
            commitStatus = db.commitSession(session)
            if commitStatus == "SUCCESS":
                return "INSERTED_ACCOUNT"
            else:
                return "ERROR : " + commitStatus
        except Exception as err:
            if "duplicate key" in str(err):
                return "ERROR : DUPLICATE KEY" 
            return "ERROR : INS_ACCOUNT"

    def editAccountForm(self, db, formData):
        session = db.initiateSession()
        recordToEdit = session.query(Account).filter(Account.id==formData["account_id"]).first()
        recordToEdit.account_name = formData["account_name"] if "account_name" in formData else recordToEdit.account_name
        recordToEdit.account_type = formData["account_type"] if "account_type" in formData else recordToEdit.account_type
        recordToEdit.account_status = formData["account_status"] if "account_status" in formData else recordToEdit.account_status
        recordToEdit.addr_line = formData["addr_line"] if "addr_line" in formData else recordToEdit.addr_line
        recordToEdit.addr_city = formData["addr_city"] if "addr_city" in formData else recordToEdit.addr_city
        recordToEdit.addr_state = formData["addr_state"] if "addr_state" in formData else recordToEdit.addr_state
        recordToEdit.addr_country = formData["addr_country"] if "addr_country" in formData else recordToEdit.addr_zip
        recordToEdit.addr_zip = formData["addr_zip"] if "addr_zip" in formData else recordToEdit.addr_zip
        commitStatus = db.commitSession(session)
        return commitStatus

    def deleteAccount(self, db, recordIds):
        queryParams = "id IN (" + ','.join([ '\'' + rcdId + '\'' for rcdId in recordIds]) + ") AND account_default != true"
        return db.deleteData('account', queryParams)

    def fetchByAccountId(self, db, recordIds = []):
        params = ""
        if recordIds != [] and recordIds != None:
            if isinstance(recordIds, str):   
                params = 'id = \'' + recordIds + '\'' 
            elif isinstance(recordIds, list):
                params = 'id IN (' + ','.join([ '\'' + rcdId + '\'' for rcdId in recordIds]) + ')' 
            return db.fetchData('Account', None, params, None) 
        return "ERROR : MISSING_AccountIDS"

    def fetchAccountWithProjectCount(self, db, queryFields = None, queryParams = None, queryLimit = None):
        return db.fetchData('account', "id, acc_name, acc_type, acc_status, addr_line, addr_city, addr_state, addr_country, addr_zip, (SELECT COUNT(id) FROM project WHERE project.account_id = account.id) AS count" , queryParams, queryLimit)

    def fetchAccounts(self, db, queryFields = None, queryParams = None, queryLimit = None):
        return db.fetchData('account', queryFields, queryParams, queryLimit)

class Project(base.Model):
    __tablename__ = 'project'
    id = Column(Integer, primary_key=True)
    description = Column(String)
    account_id = Column(Integer, ForeignKey("account.id"))
    manager_id = Column(Integer, ForeignKey('person.id'))
    project_status = Column(String)
    account = relationship("Account", back_populates="projects")
    children = relationship("ProjectAssignment", back_populates="project")
    def __init__(self, formData = None):
        if formData != None:
            self.description = formData["description"] if "description" in formData else ""
            self.account_id = formData["project_account_id"] if "project_account_id" in formData else None
            self.manager_id = formData["project_manager_id"] if "project_manager_id" in formData else None
            self.project_status = formData["project_status"] if "project_status" in formData else "ACTIVE"

    def createProjectForm(self, db, formData):
        self.__init__(formData)
        return self.createProject(db)

    def createProject(self, db):
        try:
            session = db.initiateSession()
            session.add(self)
            commitStatus = db.commitSession(session)
            if commitStatus == "SUCCESS":
                return "INSERTED_PROJECT"
            else:
                return "ERROR : " + commitStatus
        except Exception as err:
            if "duplicate key" in str(err):
                return "ERROR : DUPLICATE KEY" 
            return "ERROR : INS_PROJECT"

    def editProjectForm(self, db, formData):
        session = db.initiateSession()
        recordToEdit = session.query(Project).filter(Project.id==formData["project_id"]).first()
        recordToEdit.project_id = formData["project_id"] if "project_id" in formData else recordToEdit.project_id
        recordToEdit.project_description = formData["project_description"] if "project_description" in formData else recordToEdit.project_description
        recordToEdit.account_id = formData["project_account_id"] if "project_account_id" in formData else recordToEdit.account_id
        recordToEdit.manager_id = formData["project_manager_id"] if "project_manager_id" in formData else recordToEdit.manager_id
        recordToEdit.project_status = formData["project_status"] if "project_status" in formData else recordToEdit.project_status
        commitStatus = db.commitSession(session)
        return commitStatus

    def deleteProject(self, db, recordIds):
        queryParams = "id IN (" + ','.join([ '\'' + rcdId + '\'' for rcdId in recordIds]) + ") AND project_default != true"
        return db.deleteData('project', queryParams)

    def fetchByProjectId(self, db, recordIds = []):
        params = ""
        if recordIds != [] and recordIds != None:
            if isinstance(recordIds, str):   
                params = 'id = \'' + recordIds + '\'' 
            elif isinstance(recordIds, list):
                params = 'id IN (' + ','.join([ '\'' + rcdId + '\'' for rcdId in recordIds]) + ')' 
            return db.fetchData('Project', None, params, None) 
        return "ERROR : MISSING_ProjectIDS"

    def fetchProjectWithUserCount(self, db, queryFields = None, queryParams = None, queryLimit = None):
        if queryParams == None:
            queryParams = " account.id = project.account_id AND "
        return db.fetchData('account, project, person', "id, project_name, project_descr, project_active, project_default, project_payscale, (SELECT COUNT(id) FROM person WHERE person.account_id = project.id)" , queryParams, queryLimit)

    def fetchProjects(self, db, queryFields = None, queryParams = None, queryLimit = None):
        return db.fetchData('project', queryFields, queryParams, queryLimit)
    
class ProjectAssignment(base.Model):
    __tablename__ = 'projectassignment'
    id = Column(Integer, primary_key=True)
    role = Column(String, nullable=False, index=True)
    account_id = Column(Integer, ForeignKey("project.id"))
    person_id = Column(Integer, ForeignKey("person.id"))
    project = relationship("Project", back_populates="children")