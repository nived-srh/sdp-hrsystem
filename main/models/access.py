from . import base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

class Profile(base.Model):
    __tablename__ = 'profile'
    id = Column(Integer, primary_key=True)
    profile_name = Column(String, nullable=False, index=True)
    view_id = Column(Integer, ForeignKey("view.id"))
    #children = relationship("ProfileAssignment", back_populates="profile")
    view = relationship("View", back_populates="profiles")
    
    def __init__(self, profileName, view):
        self.view = view
        self.profile_name = profileName

    def createProfileForm(self, db, formData):
        self.profile_name = formData["profile_name"]
        return self.createProfile(self,db)

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

'''
class ProfileAssignment(base.Model):
    __tablename__ = 'profileAssignment'
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("profile.id"))
    person_id = Column(Integer, ForeignKey("person.id"))
    profile = relationship("Profile", back_populates="children")
'''

#ACCESS CONTROL
VIEW_LIST = ["dashboard", "profile", "dailystatus", "vacation", "settings", "recruitment", "payroll", "candidate", "external", "employee", "accounts", "projects", "profiles", "views"]

class View(base.Model):
    __tablename__ = 'view'
    id = Column(Integer, primary_key=True)
    view_name = Column(String, unique=True, nullable=False, index=True) 
    profiles = relationship("Profile", back_populates="view")
    view_details = relationship("ViewDetail", back_populates="view")
    
    def __init__(self, formData):
        self.view_name = formData["view_name"]

    def createViewForm(self, db, formData):
        self.view_name = formData["view_name"]
        return self.createView(db)

    def createViewWithDetails(self, db, formData):
        self.view_name = formData["view_name"]
        if formData["view_name"] == "admin":
            formData["is_admin"] = True
        else:            
            formData["is_admin"] = False
        response = self.createView(db)
        if response == "INSERTED_VIEW":
            session = db.initiateSession()
            try:
                for item in VIEW_LIST:
                    formData["viewdetail_name"] = item
                    vd = ViewDetail(self, formData)
                    session.add(vd)
                commitStatus = db.commitSession(session)
                if commitStatus == "SUCCESS":
                    return "INSERTED_VIEWDETAIL_BULK"
                else:
                    return "ERROR_" + commitStatus
            except Exception as err:
                return "ERR:"
        else:
            return "DUPLICATE_VIEWDETAIL"

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
                return "ERR:"
        else:
            return "DUPLICATE_VIEW"

class ViewDetail(base.Model):
    __tablename__ = 'viewdetail'
    id = Column(Integer, primary_key=True)
    viewdetail_name = Column(String, default="default", index=True) 
    viewdetail_group = Column(String, default="default", index=True) 
    allow_read = Column(Boolean, default=False)
    allow_create = Column(Boolean, default=False)
    allow_edit = Column(Boolean, default=False)
    allow_delete = Column(Boolean, default=False)
    view_id = Column(Integer, ForeignKey("view.id"))
    view = relationship("View", back_populates="view_details")

    def __init__(self, view, formData):
        self.view = view if view is not None else None
        self.viewdetail_name = formData["viewdetail_name"] if "viewdetail_name" in formData else "invalid"
        self.viewdetail_group = formData["viewdetail_group"] if "viewdetail_group" in formData else None
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

    def createViewDetailForm(self, db, view, formData):
        self.view = view if view is not None else None
        self.view_group = formData["viewdetail_group"] if "viewdetail_group" in formData else None
        self.allow_read = formData["allowRead"] if "allowRead" in formData else False
        self.allow_create = formData["allowCreate"] if "allowCreate" in formData else False
        self.allow_edit = formData["allowEdit"] if "allowEdit" in formData else False
        self.allow_delete = formData["allowDelete"] if "allowDelete" in formData else False
        return self.createViewDetail(db)

    def createViewDetail(self, db):
        existingViewDetail = None #self.fetchUsers(db, username)
        if existingViewDetail == None or existingViewDetail == []:
            try:
                session = db.initiateSession()
                session.add(self)
                commitStatus = db.commitSession(session)
                if commitStatus == "SUCCESS":
                    return "INSERTED_VIEWDETAIL"
                else:
                    return "ERROR_" + commitStatus
            except Exception as err:
                return "ERR:"
        else:
            return "DUPLICATE_VIEWDETAIL"

'''
class ViewAssignment(base.Model):
    __tablename__ = 'viewAssignment'
    id = Column(Integer, primary_key=True)
    view_id = Column(Integer, ForeignKey("view.id"))
    profile_id = Column(Integer, ForeignKey("profile.id"))
    view = relationship("View", back_populates="children")
'''