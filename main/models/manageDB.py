from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker    
from .base import Model
from .access import Profile, ProfileAccess, View
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

    #CREATE_VIEWS
    viewList = []
    viewList.append(View(view_name = "dashboard", view_group = "default", view_url = "/", view_label = "Dashboard", view_icon = "", view_tab = True, allow_read_default = True, allow_create_default = False, allow_edit_default = False, allow_delete_default = False))
    viewList.append(View(view_name = "profile", view_group = "default", view_url = "/profile", view_label = "Profile", view_icon = "", view_tab = True, allow_read_default = True, allow_create_default = False, allow_edit_default = False, allow_delete_default = False))
    viewList.append(View(view_name = "dailystatus", view_group = "default", view_url = "/dailystatus", view_label = "Daily Status", view_icon = "", view_tab = True, allow_read_default = True, allow_create_default = False, allow_edit_default = False, allow_delete_default = False))
    viewList.append(View(view_name = "vacation", view_group = "default", view_url = "/vacation", view_label = "Vacation", view_icon = "", view_tab = True, allow_read_default = True, allow_create_default = False, allow_edit_default = False, allow_delete_default = False))
    viewList.append(View(view_name = "settings", view_group = "default", view_url = "/settings", view_label = "Settings", view_icon = "", view_tab = True, allow_read_default = True, allow_create_default = False, allow_edit_default = False, allow_delete_default = False))
    viewList.append(View(view_name = "accounts", view_group = "default", view_url = "/account", view_label = "Account", view_icon = "", view_tab = False, allow_read_default = True, allow_create_default = False, allow_edit_default = False, allow_delete_default = False))
    viewList.append(View(view_name = "projects", view_group = "default", view_url = "/project", view_label = "Project", view_icon = "", view_tab = False, allow_read_default = True, allow_create_default = False, allow_edit_default = False, allow_delete_default = False))
    viewList.append(View(view_name = "search", view_group = "default", view_url = "/search", view_label = "Search", view_icon = "", view_tab = False, allow_read_default = True, allow_create_default = False, allow_edit_default = False, allow_delete_default = False))
    viewList.append(View(view_name = "employee", view_group = "default", view_url = "/employee", view_label = "Employee", view_icon = "", view_tab = False, allow_read_default = True, allow_create_default = False, allow_edit_default = False, allow_delete_default = False))
    viewList.append(View(view_name = "consultants", view_group = "default", view_url = "/contractor", view_label = "Contractor", view_icon = "", view_tab = False, allow_read_default = True, allow_create_default = False, allow_edit_default = False, allow_delete_default = False))
    viewList.append(View(view_name = "contractors", view_group = "default", view_url = "/consultant", view_label = "Consultant", view_icon = "", view_tab = False, allow_read_default = True, allow_create_default = False, allow_edit_default = False, allow_delete_default = False))
    viewList.append(View(view_name = "access", view_group = "admin", view_url = "/access", view_label = "Access", view_icon = "", view_tab = True, allow_read_default = True, allow_create_default = False, allow_edit_default = False, allow_delete_default = False))
    viewList.append(View(view_name = "profiles", view_group = "admin", view_url = "/profile", view_label = "Profile", view_icon = "", view_tab = False, allow_read_default = True, allow_create_default = False, allow_edit_default = False, allow_delete_default = False))
    viewList.append(View(view_name = "views", view_group = "admin", view_url = "/view", view_label = "View", view_icon = "", view_tab = False, allow_read_default = True, allow_create_default = False, allow_edit_default = False, allow_delete_default = False))
    viewList.append(View(view_name = "people", view_group = "manage", view_url = "/people", view_label = "People", view_icon = "", view_tab = True, allow_read_default = True, allow_create_default = False, allow_edit_default = False, allow_delete_default = False))
    viewList.append(View(view_name = "payroll", view_group = "manage", view_url = "/payroll", view_label = "Payroll", view_icon = "", view_tab = True, allow_read_default = True, allow_create_default = False, allow_edit_default = False, allow_delete_default = False))
    viewList.append(View(view_name = "recruitment", view_group = "manage", view_url = "/recruitment", view_label = "Recruitment", view_icon = "", view_tab = True, allow_read_default = True, allow_create_default = False, allow_edit_default = False, allow_delete_default = False))
    viewList.append(View(view_name = "jobs", view_group = "public", view_url = "/jobs", view_label = "Jobs", view_icon = "", view_tab = True, allow_read_default = True, allow_create_default = False, allow_edit_default = False, allow_delete_default = False))
    viewList.append(View(view_name = "myapplication", view_group = "public", view_url = "/jobs/myapplication", view_label = "My Applications", view_icon = "", view_tab = True, allow_read_default = True, allow_create_default = False, allow_edit_default = False, allow_delete_default = False))
    viewList.append(View(view_name = "myapplication_signedin", view_group = "candidate", view_url = "/jobs/myapplication", view_label = "My Applications", view_icon = "", view_tab = True, allow_read_default = True, allow_create_default = False, allow_edit_default = False, allow_delete_default = False))
    session = db.initiateSession()
    session.add_all(viewList)
    db.commitSession(session, True)

    formData["profile_name"] = "ADMIN"
    prf = Profile(formData)
    results.append(prf.createProfileWithAccess(db, viewList, formData))

    
    formData["profile_name"] = "MANAGER"
    prf2 = Profile(formData)
    results.append(prf2.createProfileWithAccess(db, viewList, formData))

    formData["profile_name"] = "HR"
    prf3 = Profile(formData)
    results.append(prf3.createProfileWithAccess(db, viewList, formData))

    formData= {}
    formData["username"] = "admin"
    formData["email"] = "admin"
    formData["password"] = "admin"
    formData["last_name"] = "admin"
    formData["profile"] = prf
    
    emp = Employee()
    results.append(emp.createEmployeeForm(db, formData))
    return results
    