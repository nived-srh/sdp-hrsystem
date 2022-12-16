from . import base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

class Account(base.Model):
    __tablename__ = 'account'
    id = Column(Integer, primary_key=True)
    acc_name = Column(String, nullable=False, index=True)
    acc_type = Column(String, nullable=False, index=True)
    acc_status = Column(String, nullable=False, index=True, default="ACTIVE")
    projects = relationship("Project", back_populates="account")
    external_persons = relationship("External", back_populates="account")

    def __init__(self, formData = None):
        if formData != None:
            self.acc_name = formData["acc_name"]
            self.acc_type = formData["acc_type"] if "acc_type" in formData else ""
            self.acc_status = formData["acc_status"] if "acc_status" in formData else ""

    def createAccountForm(self, db, formData):
        self.__init__(formData)
        return self.createAccount(db)

    def createAccount(self, db):
        try:
            session = db.initiateSession()
            session.add(self)
            commitStatus = db.commitSession(session)
            if commitStatus == "SUCCESS":
                return "INSERTED_Account"
            else:
                return "ERROR_" + commitStatus
        except Exception as err:
            return "ERROR : " + str(err)

    def editAccountForm(self, db, formData):
        session = db.initiateSession()
        recordToEdit = session.query(Account).filter(Account.id==formData["account_id"]).first()
        recordToEdit.account_name = formData["account_name"] 
        recordToEdit.account_type = formData["account_type"] 
        recordToEdit.account_status = formData["account_status"] 
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
        return "ERROR_MISSING_AccountIDS"

    def fetchAccountWithUserCount(self, db, queryFields = None, queryParams = None, queryLimit = None):
        return db.fetchData('account, person', "id, account_name, account_descr, account_active, account_default, account_payscale, (SELECT COUNT(id) FROM person WHERE person.account_id = account.id)" , queryParams, queryLimit)

    def fetchaccounts(self, db, queryFields = None, queryParams = None, queryLimit = None):
        return db.fetchData('account', queryFields, queryParams, queryLimit)

class Project(base.Model):
    __tablename__ = 'project'
    id = Column(Integer, primary_key=True)
    description = Column(String)
    account_id = Column(Integer, ForeignKey("account.id"))
    account = relationship("Account", back_populates="projects")
    children = relationship("ProjectAssignment", back_populates="project")
    
class ProjectAssignment(base.Model):
    __tablename__ = 'projectassignment'
    id = Column(Integer, primary_key=True)
    role = Column(String, nullable=False, index=True)
    account_id = Column(Integer, ForeignKey("project.id"))
    person_id = Column(Integer, ForeignKey("person.id"))
    project = relationship("Project", back_populates="children")
