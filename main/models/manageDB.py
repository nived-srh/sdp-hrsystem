from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker    
from .base import Model
from .access import Profile, View, ViewDetail 
from .jobs import JobListing, JobApplication
from .accounts import Account, Project, ProjectAssignment
from .services import DailyStatus, Vacation
from .users import Person, Employee, External, Candidate

def createDB(db):
    engine = create_engine(db.dbURI, echo=True)
    Model.metadata.create_all(bind=engine)
    result = initializeDB(db)
    return result

def dropDB(db):
    engine = create_engine(db.dbURI, echo=True)
    Model.metadata.drop_all(bind=engine)

def initializeDB(db):
    results = []
    formData = {}
    formData["username"] = "admin"
    formData["email"] = "admin"
    formData["password"] = "admin"
    formData["last_name"] = "admin"

    formData["view_name"] = "admin"
    view = View(formData)
    results.append(view.createViewWithDetails(db, formData))
    
    formData["view_name"] = "admin2"
    view2 = View(formData)
    results.append(view2.createViewWithDetails(db, formData))

    prf = Profile("admin", view2)
    results.append(prf.createProfile(db))
    
    formData= {}
    formData["username"] = "admin"
    formData["email"] = "admin"
    formData["password"] = "admin"
    formData["last_name"] = "admin"
    
    emp = Employee()
    results.append(emp.createEmployeeForm(db, formData))
    return results
    