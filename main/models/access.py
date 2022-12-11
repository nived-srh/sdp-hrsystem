from . import base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

class Profile(base.Model):
    __tablename__ = 'profile'
    id = Column(Integer, primary_key=True)
    profile_name = Column(String, nullable=False, index=True)
    profile_descr = Column(String)
    profile_active = Column(Boolean, default=True)
    children = relationship("ProfileAccess", back_populates="profile")
    persons = relationship("Person", back_populates="profile")
    
    def __init__(self, formData = None):
        if formData != None:
            self.profile_name = formData["profile_name"]

    def createProfileForm(self, db, formData):
        self.__init__(formData)
        return self.createProfile(self,db)

    def createProfileWithAccess(self, db, viewList, formData):
        self.profile_name = formData["profile_name"]
        if formData["profile_name"] == "ADMIN" or  formData["profile_name"] == "HR" :
            formData["full_access"] = True
        else:            
            formData["full_access"] = False
        response = self.createProfile(db)
        if response == "INSERTED_PROFILE":
            session = db.initiateSession()
            try:
                for item in viewList:
                    pfa = ProfileAccess(self, item, formData)
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
    
    def fetchProfiles(self, db, queryFields = None, queryParams = None, queryLimit = None):
        return db.fetchData('profile', queryFields, queryParams, queryLimit)

    def fetchProfilesWithPersonCount(self, db, queryFields = None, queryParams = None, queryLimit = None):
        return db.fetchData('profile', 'profile_name, profile_descr, profile_active, (SELECT COUNT(id) FROM person WHERE person.profile_id = profile.id)', queryParams, queryLimit)    
        
class ProfileAccess(base.Model):
    __tablename__ = 'profileaccess'
    id = Column(Integer, primary_key=True)
    allow_read = Column(Boolean, default=False)
    allow_create = Column(Boolean, default=False)
    allow_edit = Column(Boolean, default=False)
    allow_delete = Column(Boolean, default=False)
    profile_id = Column(Integer, ForeignKey("profile.id"))
    view_id = Column(Integer, ForeignKey("view.id"))
    profile = relationship("Profile", back_populates="children")
    view = relationship("View", back_populates="children")

    def __init__(self, profile = None, view = None, formData = None):
        if view != None and profile != None and formData != None:
            self.view = view if view is not None else None
            self.profile = profile if profile is not None else None
            if formData["full_access"] == True:
                self.allow_read = True
                self.allow_create = True
                self.allow_edit = True
                self.allow_delete = True
            else:
                self.allow_read = False
                self.allow_create = False
                self.allow_edit = False
                self.allow_delete = False

    def createProfileAccessForm(self, db, formData):
        self.__init__(formData)
        return self.createProfileAccess(db)

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
                return "ERROR"
        else:
            return "DUPLICATE_PROFILEACCESS"
    
    def fetchProfileAccess(self, db, queryFields = None, queryParams = None, queryLimit = None):
        return db.fetchData('profileaccess', queryFields, queryParams, queryLimit)

    def fetchProfileAccessByUsername(self, db, username, accessCheck = False, onlyTables = False):
        if username != None and username != '':
            queryParams = 'profileaccess.view_id = view.id AND profileaccess.profile_id = person.profile_id AND profileaccess.allow_read = true AND username = \'' + username + '\''
            queryFields = 'view_name, view_group, view_url, view_label, view_tab, view_icon, allow_read, allow_create, allow_edit, allow_delete' if accessCheck else 'view_name, view_group, view_url, view_label, view_tab, view_icon, allow_read'
        else:
            queryParams = 'profileaccess.view_id = view.id AND profileaccess.profile_id = person.profile_id AND profileaccess.allow_read = true AND view.view_group = \'PUBLIC\' ORDER BY profileaccess.id '
            queryFields = 'view_name, view_group, view_url, view_label, view_tab, view_icon, allow_read'
        
        if onlyTables:
            queryParams += ' AND view.view_type = \'TABLE\' '
        return db.fetchData('profileaccess, view, person', queryFields, queryParams, None)

class View(base.Model):
    __tablename__ = 'view'
    id = Column(Integer, primary_key=True)
    view_name = Column(String, default="default", unique=True, index=True) 
    view_group = Column(String, default="default", index=True) 
    view_type = Column(String, default="default", index=True) 
    view_url = Column(String, default="/", index=True) 
    view_label = Column(String) 
    view_tab = Column(Boolean, default=False)
    view_icon = Column(String) 
    allow_read_default = Column(Boolean, default=False)
    allow_create_default = Column(Boolean, default=False)
    allow_edit_default = Column(Boolean, default=False)
    allow_delete_default = Column(Boolean, default=False)
    children = relationship("ProfileAccess", back_populates="view")


    def __init__(self, **kwargs):
        if len(list(kwargs.keys())) > 0:
            self.view_name = kwargs["view_name"]
            self.view_group = str(kwargs["view_group"]).upper()
            self.view_type = str(kwargs["view_type"]).upper()
            self.view_url = kwargs["view_url"]
            self.view_label = kwargs["view_label"]
            self.view_icon = kwargs["view_icon"]
            self.view_tab = kwargs["view_tab"] if "view_tab" in kwargs else False
            self.allow_read_default = kwargs["allow_read_default"] if "allow_read_default" in kwargs else False
            self.allow_create_default = kwargs["allow_create_default"] if "allow_create_default" in kwargs else False
            self.allow_edit_default = kwargs["allow_edit_default"] if "allow_edit_default" in kwargs else False
            self.allow_delete_default = kwargs["allow_delete_default"] if "allow_delete_default" in kwargs else False

    def createView(self, db):
        existingView = None #self.fetchUsers(db, username)
        if existingView == None or existingView == []:
            try:
                session = db.initiateSession()
                session.add(self)
                commitStatus = db.commitSession(session)
                if commitStatus == "SUCCESS":
                    return "INSERTED_VIEW"
                else:
                    return "ERROR_" + commitStatus
            except Exception as err:
                return "ERROR"
        else:
            return "DUPLICATE_VIEW"
    
    def fetchViews(self, db, queryFields = None, queryParams = None, queryLimit = None):
        return db.fetchData('view', queryFields, queryParams, queryLimit)
