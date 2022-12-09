from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker    
from .base import Model
from .access import Profile, ProfileAccess
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

    formData["profile_name"] = "admin"
    prf = Profile(formData)
    results.append(prf.createProfileWithAccess(db, formData))
    
    formData= {}
    formData["username"] = "admin"
    formData["email"] = "admin"
    formData["password"] = "admin"
    formData["last_name"] = "admin"
    formData["profile"] = prf
    
    emp = Employee()
    results.append(emp.createEmployeeForm(db, formData))
    return results
    