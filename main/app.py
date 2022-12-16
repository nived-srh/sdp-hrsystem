from flask import Flask, request, session, jsonify, render_template, redirect, url_for
from flask_cors import CORS
from datetime import date, timedelta
from .config import AppConfig
from .database import DatabaseConnect
from .models import *
from . import utils 

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['SECRET_KEY'] = AppConfig.SECRET_KEY
app.config['PERMANENT_SESSION_LIFETIME'] = AppConfig.PERMANENT_SESSION_LIFETIME

db = None
publicViews = ["/static", "/dropDatabase", "/createDatabase", "/favicon.ico", "/unauthorized", "login", "logout", "register"] 

@app.before_request
def beforeRequest():
    if len([ view for view in publicViews if view in request.path and request.path != view]) == 0:
        global db
        if db == None:
            db = DatabaseConnect(AppConfig.SQLALCHEMY_DATABASE_URI)
        if 'userSession' in session:        
            hasViewAccess = utils.validateUserAccess(db, session['userSession']["username"], request.path) 
        else:
            hasViewAccess = utils.validateUserAccess(db, None, request.path) 
        
        if (not hasViewAccess) and request.path != "/unauthorized" and request.path != "/login" and request.path != "/logout" and request.path != "/dropDatabase" and request.path != "/createDatabase":
            return redirect(url_for('unauthorized'))

@app.route("/")
def home():
    if 'userSession' not in session:        
        return redirect(url_for('login'))    
    global db
    if db == None:
        db = DatabaseConnect(AppConfig.SQLALCHEMY_DATABASE_URI)

    response = {}
    response["views"] = utils.fetchSidebarLinks(db, session['userSession']["username"])    
    response["hasSidebar"] = True
    response["userSession"] = session['userSession']
    
    return render_template("base.html", response=response)

@app.route("/login", methods=['GET','POST'])
def login():
    response = { 'table' : 'login'}
    if request.method == 'POST':
        global db
        if db == None:
            db = DatabaseConnect(AppConfig.SQLALCHEMY_DATABASE_URI)
        
        result = users.Person().validatePerson(db, request.form['username'], request.form['password'] )
        returnUrl = request.args.get('returnUrl') if 'returnUrl' in request.args and request.args.get('returnUrl') != "/login"  else "/"
        if result != None and "ERROR" not in result:
            activeUser = { 'username' : result.username, 'id':result.id, 'email' : result.email, 'first_name':result.first_name, 'last_name':result.last_name}            
            session['userSession'] = activeUser
            return redirect(returnUrl)
        else:
            response["messages"] = result
    return render_template("login.html", response=response)

@app.route("/register", methods=['POST'])
def register():
    response = { 'table' : 'register'}
    
    global db
    if db == None:
        db = DatabaseConnect(AppConfig.SQLALCHEMY_DATABASE_URI)
    
    response = formData = {}
    formData = dict(request.form)
    candidate_profile = list(access.Profile().fetchProfiles(db, queryParams=" profile_name = 'CANDIDATE'", queryLimit="1"))
    formData["profile_id"] = candidate_profile[0].id
    response["messages"] = users.Candidate().createCandidateForm(db, formData)
    del formData["password"]
    if "ERROR" not in response["messages"]:
        result = list(users.Person().fetchPersons(db, queryParams=" user_type = 'candidate' and username = '" + formData["email"] + "'", queryLimit="1"))[0]
        activeUser = { 'username' : result.username, 'id':result.id, 'email' : result.email, 'first_name':result.first_name, 'last_name':result.last_name}            
        session['userSession'] = activeUser
    returnUrl = request.args.get('returnUrl') if 'returnUrl' in request.args and request.args.get('returnUrl') != "/login"  else "/"
    return redirect(returnUrl)

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    try:
        session.pop('userSession', None)
    except Exception as err:
        print(err)
    finally:         
        return redirect(url_for('login'))

@app.route("/search", methods=['GET','POST'])
def globalSearch():
    if 'userSession' not in session:        
        return redirect(url_for('login'))    
    global db
    if db == None:
        db = DatabaseConnect(AppConfig.SQLALCHEMY_DATABASE_URI)
    
    response = {}
    response["views"] = utils.fetchSidebarLinks(db, session['userSession']["username"])    
    response["hasSidebar"] = True
    response["userSession"] = session['userSession']
    response["payrolls"] = payroll.Payroll().fetchPayrolls(db)

    return render_template("search.html", response=response)
    if "accounts" in response["views"] :
        response["accounts"] = None#accounts.Account().search(db, session['userSession'], views["accounts"])
    elif "projects" in response["views"] :
        response["projects"] = None
    elif "employee" in response["views"] :
        response["employee"] = users.Employee().fetchEmployeesWithDetails(db)
    elif "consultants" in response["views"] :
        response["consultants"] = users.External().fetchExternalsWithDetails(db, queryParams=" person.profile_id = profile.id AND external.ext_type = 'CONSULTANT' AND person.user_type = 'external' AND person.id = external.person_id ORDER BY person.id DESC")
    elif "contractors" in response["views"] :
        response["contractors"] = users.External().fetchExternalsWithDetails(db, queryParams=" person.profile_id = profile.id AND external.ext_type = 'CONTRACTOR' AND person.user_type = 'external' AND person.id = external.person_id ORDER BY person.id DESC")
    elif "profiles" in response["views"] :
        response["profiles"] = None
    elif "views" in response["views"] :
        response["views"] = None
    elif "payroll" in response["views"] :
        response["payroll"] = payroll.Payroll().fetchPayrolls(db)

    return render_template("search.html", response=response)

@app.route("/profile", methods=["GET", "POST"])
def profile():
    if 'userSession' not in session:        
        return redirect(url_for('login'))
        
    global db
    if db == None:
        db = DatabaseConnect(AppConfig.SQLALCHEMY_DATABASE_URI)

    response = {}
    response["views"] = utils.fetchSidebarLinks(db, session['userSession']["username"])    
    response["hasSidebar"] = True
    response["userSession"] = session['userSession']

    if request.method == 'POST':
        formData = dict(request.form)
        formData["employee_id"] = session['userSession']['id']
        new_status = services.DailyStatus().createDailyStatusForm(db, formData)    
        response["messages"] = new_status
    else:        
        formData = {}
        formData["status_date"] = date.today()
        response["formData"] = formData
    response["statuses"] = services.DailyStatus().fetchDailyStatusByUsername(db, session['userSession']['id'])    
    return render_template("profile.html", response=response)       
        
@app.route("/accounts",  defaults={'table': None, 'action' : "read", 'key': None }, methods=['GET'])
@app.route("/accounts/<table>", defaults={'action' : None, 'key': None }, methods=['GET'])
@app.route("/accounts/<table>/<action>", defaults={'key': None}, methods=['GET','POST'])
@app.route("/accounts/<table>/<action>/<key>", methods=['GET','POST'])
def manageAccounts(table, action, key):
    if 'userSession' not in session:        
        return redirect(url_for('login'))
    # if table == None:
    #     return redirect("/payroll/details")    

    global db
    if db == None:
        db = DatabaseConnect(AppConfig.SQLALCHEMY_DATABASE_URI)

    response = formData = {}
    response["views"] = utils.fetchSidebarLinks(db, session['userSession']["username"])    
    response["hasSidebar"] = True
    response["userSession"] = session['userSession']
    response["table"] = table
    response["action"] = action
    response["key"] = key
    formData['proll_period'] = date.today().strftime("%Y-%m")    

    if request.args.get('msg') != None:
        response["messages"] = request.args.get('msg')  
        
    if request.method == 'POST':
        if action == "create":
            formData = dict(request.form)
            if table == "tiers": 
                response["messages"] = payroll.Tier().createTierForm(db, formData)
                if "ERROR" not in response["messages"]:
                    return redirect("/payroll/tiers?msg=" + response["messages"]) 
            elif table == "details":
                response["messages"] = payroll.Payroll().createPayrollForm(db, formData)
                if "ERROR" not in response["messages"]:
                    return redirect("/payroll/details?msg=" + response["messages"]) 
        elif action == "edit":
            formData = dict(request.form)
            if table == "tiers": 
                response["messages"] = payroll.Tier().editTierForm(db, formData)
                if "ERROR" not in response["messages"]:
                    return redirect("/payroll/tiers?msg=" + response["messages"]) 
            elif table == "details":
                response["messages"] = payroll.Payroll().editPayrollForm(db, formData)
                if "ERROR" not in response["messages"]:
                    return redirect("/payroll/details?msg=" + response["messages"]) 

    if key != None:        
        if action == "read":            
            pass
        elif action == "edit":
            if table == "tiers": 
                result = payroll.Tier().fetchByTierId(db, list(key))
                if result != None:
                    for row in result:   
                        formData['tier_name'] = row.tier_name        
                        formData['tier_descr'] = row.tier_descr        
                        formData['tier_payscale'] = row.tier_payscale        
                        formData['tier_active'] = row.tier_active                
            elif table == "details": 
                result = payroll.Payroll().fetchByPayrollId(db, list(key))
                if result != None:
                    for row in result:   
                        formData['proll_period'] = row.proll_year + "-" + row.proll_month
                        formData['proll_status'] = row.proll_status
        elif action == "delete":
            formData = dict(request.form)
            if table == "tiers": 
                result = payroll.Tier().deleteTier(db, list(key))
                if result == "SUCCESS":
                    return redirect("/payroll/tiers?msg=" + result)
                else:
                    response["messages"] = result    
            elif table == "details":    
                result = payroll.Payroll().deletePayroll(db, list(key))
                if result == "SUCCESS":
                    return redirect("/payroll/details?msg=" + result)
                else:
                    response["messages"] = result     
    elif key == None and action != None and table != None and request.method == 'GET':
        response["messages"] = "ERROR_ID_NOT_SPECIFIED"     
          
    response["formData"] = formData
    response["payrolls"] = payroll.Payroll().fetchPayrolls(db)    
    response["tiers"] = payroll.Tier().fetchTiers(db)    
    return render_template("payroll.html", response=response)       
        
@app.route("/dailystatus", methods=["GET", "POST"])
def dailystatus():
    if 'userSession' not in session:        
        return redirect(url_for('login'))
        
    global db
    if db == None:
        db = DatabaseConnect(AppConfig.SQLALCHEMY_DATABASE_URI)

    response = {}
    response["views"] = utils.fetchSidebarLinks(db, session['userSession']["username"])    
    response["hasSidebar"] = True
    response["userSession"] = session['userSession']

    if request.method == 'POST':
        formData = dict(request.form)
        formData["employee_id"] = session['userSession']['id']
        new_status = services.DailyStatus().createDailyStatusForm(db, formData)    
        response["messages"] = new_status
    else:        
        formData = {}
        formData["status_date"] = date.today()
        response["formData"] = formData
    response["statuses"] = services.DailyStatus().fetchDailyStatusByUsername(db, session['userSession']['id'])    
    return render_template("dailystatus.html", response=response)       

@app.route("/vacation", methods=["GET", "POST"])
def vacation():
    if 'userSession' not in session:        
        return redirect(url_for('login'))
        
    global db
    if db == None:
        db = DatabaseConnect(AppConfig.SQLALCHEMY_DATABASE_URI)

    response = formData  = {}
    response["views"] = utils.fetchSidebarLinks(db, session['userSession']["username"])    
    response["hasSidebar"] = True
    response["userSession"] = session['userSession']

    if request.method == 'POST':
        formData = dict(request.form)
        formData["employee_id"] =  session['userSession']['id']
        new_status = services.DailyStatus().createDailyStatusForm(db, formData)    
        response["messages"] = new_status
    else:        
        formData = {}
        formData["vac_startdate"] = date.today()
        formData["vac_enddate"] = date.today() + timedelta(days=1)
        response["formData"] = formData
    response["leaveHistory"] = services.DailyStatus().fetchDailyStatusByUsername(db,  session['userSession']['id'])    
    return render_template("vacation.html", response=response)              

@app.route("/jobs",  defaults={'table': None, 'action' : "read", 'key': None }, methods=['GET'])
@app.route("/jobs/<table>", defaults={'action' : None, 'key': None }, methods=['GET'])
@app.route("/jobs/<table>/<action>", defaults={'key': None}, methods=['GET','POST'])
@app.route("/jobs/<table>/<action>/<key>", methods=['GET','POST'])
def jobportal(table, action, key):
    if table == None:
        return redirect("/jobs/listing")    

    global db
    if db == None:
        db = DatabaseConnect(AppConfig.SQLALCHEMY_DATABASE_URI)
    
    response = formData = {}
    response["views"] = utils.fetchSidebarLinks(db, None)    
    response["hasSidebar"] = True
    response["formData"] = formData
    print("testest ", table)
    if request.method == 'POST':
        pass
    else:
        if table == "myapplication":
            if 'userSession' not in session:  
                return render_template("myapplications.html", response=response)
            else:              
                response["userSession"] = session['userSession']
                return render_template("myapplications.html", response=response)
                
    response["joblistings"] = jobs.JobListing().fetchJobListings(db, queryParams=" job_status != 'INACTIVE' ORDER BY job_role, id DESC")
    return render_template("jobs.html", response=response)
         
@app.route("/recruitment",  defaults={'table': None, 'action' : "read", 'key': None }, methods=['GET'])
@app.route("/recruitment/<table>", defaults={'action' : None, 'key': None }, methods=['GET'])
@app.route("/recruitment/<table>/<action>", defaults={'key': None}, methods=['GET','POST'])
@app.route("/recruitment/<table>/<action>/<key>", methods=['GET','POST'])
def recruitment(table, action, key):
    if 'userSession' not in session:        
        return redirect(url_for('login'))
    if table == None:
        return redirect("/recruitment/joblisting")        
    global db
    if db == None:
        db = DatabaseConnect(AppConfig.SQLALCHEMY_DATABASE_URI)

    response = formData  = {}
    response["views"] = utils.fetchSidebarLinks(db, session['userSession']["username"])    
    response["hasSidebar"] = True
    response["userSession"] = session['userSession']
    response["table"] = table
    response["action"] = action
    response["key"] = key

    if request.method == 'POST':
        if action == "create":
            formData = dict(request.form)
            if table == "joblisting": 
                response["messages"] = jobs.JobListing().createJobListingForm(db, formData)
    
    if key != None:        
        if action == "read":
            pass
        elif action == "edit":
            if table == "joblisting": 
                result = jobs.JobListing().fetchByJobListingId(db, key)
                if result != None:
                    for row in result:                
                        formData["job_title"] = row.job_title
                        formData["job_descr"] = row.job_descr
                        formData["job_exp"] = row.job_exp
                        formData["job_location"] = row.job_location
                        formData["job_role"] = row.job_role
                        formData["job_status"] = row.job_status
        elif action == "delete":
            formData = dict(request.form)
            result = jobs.JobListing().deleteJobListing(db, list(key))
            if result == "SUCCESS":
                return redirect("/recruitment?msg=" + result)
            else:
                response["messages"] = result         
    elif key == None and action != None and table != None and request.method == 'GET':
        response["messages"] = "ERROR_ID_NOT_SPECIFIED"

    response["formData"] = formData
    response["joblistings"] = jobs.JobListing().fetchJobListingWithApplicantCount(db)
    return render_template("recruitment.html", response=response)       

@app.route("/payroll",  defaults={'table': None, 'action' : "read", 'key': None }, methods=['GET'])
@app.route("/payroll/<table>", defaults={'action' : None, 'key': None }, methods=['GET'])
@app.route("/payroll/<table>/<action>", defaults={'key': None}, methods=['GET','POST'])
@app.route("/payroll/<table>/<action>/<key>", methods=['GET','POST'])
def managePayroll(table, action, key):
    if 'userSession' not in session:        
        return redirect(url_for('login'))
    if table == None:
        return redirect("/payroll/details")    

    global db
    if db == None:
        db = DatabaseConnect(AppConfig.SQLALCHEMY_DATABASE_URI)

    response = formData = {}
    response["views"] = utils.fetchSidebarLinks(db, session['userSession']["username"])    
    response["hasSidebar"] = True
    response["userSession"] = session['userSession']
    response["table"] = table
    response["action"] = action
    response["key"] = key
    formData['proll_period'] = date.today().strftime("%Y-%m")    

    if request.args.get('msg') != None:
        response["messages"] = request.args.get('msg')

    if request.method == 'POST':
        if action == "create":
            formData = dict(request.form)
            if table == "tiers": 
                response["messages"] = payroll.Tier().createTierForm(db, formData)
                if "ERROR" not in response["messages"]:
                    return redirect("/payroll/tiers?msg=" + response["messages"]) 
            elif table == "details":
                response["messages"] = payroll.Payroll().createPayrollForm(db, formData)
                if "ERROR" not in response["messages"]:
                    return redirect("/payroll/details?msg=" + response["messages"]) 
        elif action == "edit":
            formData = dict(request.form)
            if table == "tiers": 
                response["messages"] = payroll.Tier().editTierForm(db, formData)
                if "ERROR" not in response["messages"]:
                    return redirect("/payroll/tiers?msg=" + response["messages"]) 
            elif table == "details":
                response["messages"] = payroll.Payroll().editPayrollForm(db, formData)
                if "ERROR" not in response["messages"]:
                    return redirect("/payroll/details?msg=" + response["messages"]) 

    if key != None:        
        if action == "read":            
            pass
        elif action == "edit":
            if table == "tiers": 
                result = payroll.Tier().fetchByTierId(db, list(key))
                if result != None:
                    for row in result:   
                        formData['tier_name'] = row.tier_name        
                        formData['tier_descr'] = row.tier_descr        
                        formData['tier_payscale'] = row.tier_payscale        
                        formData['tier_active'] = row.tier_active                
            elif table == "details": 
                result = payroll.Payroll().fetchByPayrollId(db, list(key))
                if result != None:
                    for row in result:   
                        formData['proll_period'] = row.proll_year + "-" + row.proll_month
                        formData['proll_status'] = row.proll_status
        elif action == "delete":
            formData = dict(request.form)
            if table == "tiers": 
                result = payroll.Tier().deleteTier(db, list(key))
                if result == "SUCCESS":
                    return redirect("/payroll/tiers?msg=" + result)
                else:
                    response["messages"] = result    
            elif table == "details":    
                result = payroll.Payroll().deletePayroll(db, list(key))
                if result == "SUCCESS":
                    return redirect("/payroll/details?msg=" + result)
                else:
                    response["messages"] = result     
    elif key == None and action != None and table != None and request.method == 'GET':
        response["messages"] = "ERROR_ID_NOT_SPECIFIED"     
          
    response["formData"] = formData
    response["payrolls"] = payroll.Payroll().fetchPayrolls(db)    
    response["tiers"] = payroll.Tier().fetchTiers(db)    
    return render_template("payroll.html", response=response)       

@app.route("/people",  defaults={'table': None, 'action' : "read", 'key': None }, methods=['GET'])
@app.route("/people/<table>", defaults={'action' : None, 'key': None }, methods=['GET'])
@app.route("/people/<table>/<action>", defaults={'key': None}, methods=['GET','POST'])
@app.route("/people/<table>/<action>/<key>", methods=['GET','POST'])
def managePeople(table, action, key):
    if 'userSession' not in session:        
        return redirect(url_for('login'))
    if table == None:
        return redirect("/people/employees")    
    global db
    if db == None:
        db = DatabaseConnect(AppConfig.SQLALCHEMY_DATABASE_URI)

    response = formData = {}
    response["views"] = utils.fetchSidebarLinks(db, session['userSession']["username"])    
    response["hasSidebar"] = True
    response["userSession"] = session['userSession']
    response["table"] = table
    response["action"] = action
    response["key"] = key

    if request.args.get('msg') != None:
        response["messages"] = request.args.get('msg')

    if request.method == 'POST':
        if action == "create":
            formData = dict(request.form)
            formData["password"] = AppConfig.DFLT_PASSWORD
            if table == "employees": 
                response["messages"] = users.Employee().createEmployeeForm(db, formData)
            elif table == "contractors":
                formData["ext_type"] = "CONTRACTOR"
                consultant_profile = list(access.Profile().fetchProfiles(db, queryParams=" profile_name = 'CONTRACTOR'", queryLimit="1"))
                formData["profile_id"] = consultant_profile[0].id
                response["messages"]  = users.External().createExternalForm(db, formData)
            elif table == "consultants":
                formData["ext_type"] = "CONSULTANT"
                consultant_profile = list(access.Profile().fetchProfiles(db, queryParams=" profile_name = 'CONSULTANT'", queryLimit="1"))
                formData["profile_id"] = consultant_profile[0].id
                response["messages"] = users.External().createExternalForm(db, formData)
            del formData["password"]
        elif action == "edit": 
            if table == "employees":
                response["messages"]  = users.Employee().editEmployeeForm(db, formData)          
                if "ERROR" not in response["messages"]:
                    return redirect("/people/employees?msg=" + response["messages"])      
            elif table == "contractors":
                pass
    
    if key != None:        
        if action == "read":
            pass
        elif action == "edit":
            if table == "employees": 
                result = users.Person().fetchByUserId(db, key)
                if result != None:
                    for row in result:                
                        formData["first_name"] = row.first_name
                        formData["last_name"] = row.last_name
                        formData["email"] = row.email       
                        formData["username"] = row.username        
        elif action == "delete":
            formData = dict(request.form)
            result = access.Profile().deleteProfiles(db, list(key))
            if result == "SUCCESS":
                return redirect("/access?msg=" + result)
            else:
                response["messages"] = result         
    elif key == None and action != None and table != None and request.method == 'GET':
        response["messages"] = "ERROR_ID_NOT_SPECIFIED"

    response["formData"] = formData
    response["employees"] = users.Employee().fetchEmployeesWithDetails(db, queryParams=" person.profile_id = profile.id AND person.user_type = 'employee' AND person.id = employee.person_id ORDER BY person.id DESC")
    response["contractors"] = users.External().fetchExternalsWithDetails(db, queryParams=" person.profile_id = profile.id AND external.ext_type = 'CONTRACTOR' AND person.user_type = 'external' AND person.id = external.person_id ORDER BY person.id DESC")
    response["consultants"] = users.External().fetchExternalsWithDetails(db, queryParams=" person.profile_id = profile.id AND external.ext_type = 'CONSULTANT' AND person.user_type = 'external' AND person.id = external.person_id ORDER BY person.id DESC")
    return render_template("people.html", response=response)   
    

@app.route("/access",  defaults={'table': None, 'action' : "read", 'key': None }, methods=['GET'])
@app.route("/access/<table>", defaults={'action' : None, 'key': None }, methods=['GET'])
@app.route("/access/<table>/<action>", defaults={'key': None}, methods=['GET','POST'])
@app.route("/access/<table>/<action>/<key>", methods=['GET','POST'])
def manageAccess(table, action, key):
    if 'userSession' not in session:        
        return redirect(url_for('login'))
        
    global db
    if db == None:
        db = DatabaseConnect(AppConfig.SQLALCHEMY_DATABASE_URI)

    response = formData = profileAccessLines = {}
    response["views"] = utils.fetchSidebarLinks(db, session['userSession']["username"])    
    response["hasSidebar"] = True
    response["userSession"] = session['userSession']
    response["table"] = table
    response["action"] = action
    response["key"] = key
    response["formData"] = formData
    response["profileAccessLines"] = profileAccessLines

    if request.args.get('msg') != None:
        response["messages"] = request.args.get('msg')

    if request.method == 'POST':
        formData = dict(request.form)
        if action == "create":            
            if table == "profiles":                
                response["messages"]  = access.Profile().createProfileWithAccess(db, None, formData)
            if "ERROR" not in response["messages"]:
                return redirect("/access?msg=" + response["messages"])
        elif action == "edit": 
            if table == "profiles":
                response["messages"]  = access.Profile().editProfileForm(db, formData)          
                if "ERROR" not in response["messages"]:
                    return redirect("/access?msg=" + response["messages"])      
            elif table == "profileaccess":
                pfaList = dict(request.form)
                del pfaList["profile_id"]
                response["messages"] = access.ProfileAccess().bulkEditProfileAccessForm(db, pfaList)
                return redirect("/access/profiles/read/" + request.form["profile_id"] + "?msg=" + response["messages"])

    if key != None:
        if action == "read":
            queryParams = " profile.id = '" + key + "' " 
            response["profileDetails"] = access.Profile().fetchProfiles(db, queryParams=queryParams, queryLimit="1")
            queryParams += " AND person.profile_id = profile.id" 
            response["profileAssignments"] = access.Profile().fetchProfileAssignment(db, queryParams=queryParams)
            response["profileAccess"] = access.ProfileAccess().fetchProfileAccessByProfile(db, key)
            return render_template("access.html", response=response)    
        elif action == "edit" and table == "profiles":
            queryParams = " profile.id = '" + key + "' " 
            result = access.Profile().fetchProfiles(db, queryFields="profile_name, profile_descr, profile_active",queryParams=queryParams, queryLimit="1")
            for row in result:                
                formData["profile_name"] = row.profile_name
                formData["profile_descr"] = row.profile_descr
                formData["profile_active"] = row.profile_active           
        elif action == "delete":
            formData = dict(request.form)
            response["messages"] = access.Profile().deleteProfiles(db, list(key))
            if "ERROR" not in response["messages"]:
                return redirect("/access?msg=" + response["messages"])
    elif key == None and action != None and table != None and request.method == 'GET':
        response["messages"] = "ERROR_ID_NOT_SPECIFIED"
    response["formData"] = formData
    response["profiles"] = access.Profile().fetchProfilesWithPersonCount(db)
    response["defaultviews"] = access.View().fetchViews(db)
    return render_template("access.html", response=response)   

@app.route("/fetchData/<table>", defaults={'limit': 30})
@app.route("/fetchData/<table>/<limit>")   
def fetchData(table, limit):
    global db
    if db == None:
        db = DatabaseConnect(AppConfig.SQLALCHEMY_DATABASE_URI)

    if table == "profiles":
        results = access.Profile().fetchProfiles(db)
        response = [{
            "id": row.id , 
            "field_name" : row.profile_name    
        } for row in results]
    elif table == "tiers":
        results = payroll.Tier().fetchTiers(db)
        response = [{
            "id": row.id , 
            "field_name" : row.tier_name    
        } for row in results]
    elif table == "views":
        results = utils.fetchSidebarLinks(db, session['userSession']["username"])    
        response = [{
            "crr": utils.validateUserAccess(db, session['userSession']["username"], request.path) , 
            "id": row.view_name , 
            "profile_name" : row.view_group    
        } for row in results]
    elif table =="consultants":
        results = users.External().fetchExternalsWithDetails(db, queryParams=" person.profile_id = profile.id AND external.ext_type = 'CONTRACTOR' AND person.user_type = 'external' AND person.id = external.person_id ORDER BY person.id DESC")
        response =str(results)
    if results != None:
        return jsonify({
            "results" : response})
    else:
        return jsonify({
             table : []
        }), 201

@app.route("/createDatabase")
def createDB():
    global db
    if db == None:
        db = DatabaseConnect(AppConfig.SQLALCHEMY_DATABASE_URI)
    
    try:
        results = db.createDatabase()
    except Exception as err:
        print(err)
        return jsonify({ "error": "error" })
    return jsonify({ "result": [ item for item in results] })

@app.route("/dropDatabase")
def dropDB():
    global db
    if db == None:
        db = DatabaseConnect(AppConfig.SQLALCHEMY_DATABASE_URI)
    
    try:
        db.dropDatabase()
    except Exception as err:
        print(err)
        return jsonify({ "error": "error" })
    return jsonify({ "result": "SUCCESS" })

@app.errorhandler(404)
@app.route("/unauthorized")
def unauthorized(e=None):
    if 'userSession' not in session:        
        return redirect(url_for('login'))
    else:
        global db
        if db == None:
            db = DatabaseConnect(AppConfig.SQLALCHEMY_DATABASE_URI)

        response = {}
        response["views"] = utils.fetchSidebarLinks(db, session['userSession']["username"])    
        response["hasSidebar"] = True 
        response["userSession"] = session['userSession'] 
        return render_template('404.html', response=response)

if __name__ == "__main__":
    app.run(debug=True)

