from . import base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

class Profile(base.Model):
    __tablename__ = 'profile'
    id = Column(Integer, primary_key=True)
    profile_name = Column(String, nullable=False, index=True)
    children = relationship("ProfileAccess", back_populates="profile")
    persons = relationship("Person", back_populates="profile")
    
    def __init__(self, formData = None):
        if formData != None:
            self.profile_name = formData["profile_name"]

    def createProfileForm(self, db, formData):
        self.__init__(formData)
        return self.createProfile(self,db)

    def createProfileWithAccess(self, db, formData):
        self.view_name = formData["profile_name"]
        if formData["profile_name"] == "admin":
            formData["is_admin"] = True
        else:            
            formData["is_admin"] = False
        response = self.createProfile(db)
        if response == "INSERTED_PROFILE":
            session = db.initiateSession()
            try:
                for item in ACCESS_LIST:
                    formData["view_name"] = item
                    pfa = ProfileAccess(self, formData)
                    session.add(pfa)
                commitStatus = db.commitSession(session)
                if commitStatus == "SUCCESS":
                    return "INSERTED_PROFILE_WITH_ACCESS"
                else:
                    return "ERROR_" + commitStatus
            except Exception as err:
                return "ERROR_INS_PROFILE_WITH_ACCESS"
        else:
            return "DUPLICATE_PROFILEACCESS"

    def createProfile(self, db):
        existingProfile = None #self.fetchUsers(db, username)
        if (existingProfile == None or existingProfile == []) and self.profile_name is not None:
            try:
                session = db.initiateSession()
                session.add(self)
                commitStatus = db.commitSession(session)
                if commitStatus == "SUCCESS":
                    return "INSERTED_PROFILE"
                else:
                    return "ERROR_" + commitStatus
            except Exception as err:
                return "ERROR"
        elif self.profile_name is None:
            return "MISSING_PROFILE_NAME"
        else:
            return "DUPLICATE_PROFILE"
            
#ACCESS CONTROL
ACCESS_LIST = ["dashboard", "profile", "dailystatus", "vacation", "settings", "recruitment", "payroll", "candidate", "external", "employee", "accounts", "projects", "profiles", "views"]

class ProfileAccess(base.Model):
    __tablename__ = 'profileaccess'
    id = Column(Integer, primary_key=True)
    view_name = Column(String, default="default", index=True) 
    view_group = Column(String, default="default", index=True) 
    view_url = Column(String, default="/", index=True) 
    view_label = Column(String) 
    allow_read = Column(Boolean, default=False)
    allow_create = Column(Boolean, default=False)
    allow_edit = Column(Boolean, default=False)
    allow_delete = Column(Boolean, default=False)
    profile_id = Column(Integer, ForeignKey("profile.id"))
    profile = relationship("Profile", back_populates="children")

    def __init__(self, profile = None, formData = None):
        if profile != None and formData != None:
            self.profile = profile if profile is not None else None
            self.view_name = formData["view_name"] if "view_name" in formData else "invalid"
            self.view_group = formData["view_group"] if "view_group" in formData else None
            if formData["is_admin"] == True:
                self.allow_read = True
                self.allow_create = True
                self.allow_edit = True
                self.allow_delete = True
            else:
                self.allow_read = formData["allowRead"] if "allowRead" in formData else False
                self.allow_create = formData["allowCreate"] if "allowCreate" in formData else False
                self.allow_edit = formData["allowEdit"] if "allowEdit" in formData else False
                self.allow_delete = formData["allowDelete"] if "allowDelete" in formData else False

    def createProfileAccessForm(self, db, formData):
        self.__init__(formData)
        return self.createViewDetail(db)

    def createProfileAccess(self, db):
        existingProfileAccess = None #self.fetchUsers(db, username)
        if existingProfileAccess == None or existingProfileAccess == []:
            try:
                session = db.initiateSession()
                session.add(self)
                commitStatus = db.commitSession(session)
                if commitStatus == "SUCCESS":
                    return "INSERTED_PROFILEACCESS"
                else:
                    return "ERROR_" + commitStatus
            except Exception as err:
                return "ERR:"
        else:
            return "DUPLICATE_PROFILEACCESS"
    
    def fetchProfileAccess(self, db, queryFields, queryParams, queryLimit):
        return db.fetchData('profileaccess', queryFields, queryParams, queryLimit)

    def fetchProfileAccessByUsername(self, db, username, accessCheck = False):
        if username != None and username != '':
            queryParams = 'profileaccess.profile_id = person.user_profile AND username = \'' + username + '\''
            queryFields = 'view_name, view_group, view_url, view_label, allow_read, allow_create, allow_edit, allow_delete' if accessCheck else 'view_name, view_group, view_url, view_label, allow_read'
            return db.fetchData('profileaccess, person', queryFields, queryParams, None)
