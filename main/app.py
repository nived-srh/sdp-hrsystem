from flask import Flask, request, session, jsonify, render_template, redirect, url_for
from flask_cors import CORS
from .config import AppConfig
from .database import DatabaseConnect
from .models import *
from . import utils 

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['SECRET_KEY'] = AppConfig.SECRET_KEY
app.config['PERMANENT_SESSION_LIFETIME'] = AppConfig.PERMANENT_SESSION_LIFETIME
db = None

@app.route("/")
def home():
    if 'userSession' not in session:        
        return redirect(url_for('login'))    
    global db
    if db == None:
        db = DatabaseConnect(AppConfig.SQLALCHEMY_DATABASE_URI)
    views = utils.fetchSidebarLinks(db, session['userSession'])    
    return render_template("base.html", hasSidebar=True, views=views)

@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'POST':
        global db
        if db == None:
            db = DatabaseConnect(AppConfig.SQLALCHEMY_DATABASE_URI)
        
        result = users.Person().validatePerson(db, request.form['username'], request.form['password'] )
        
        if result != None:
            session['userSession'] = result.email
            return redirect("/access")

    return render_template("login.html")

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
    views = utils.fetchSearchableViews(db, session['userSession'])    

    searchResults = {}
    if "accounts" in views:
        searchResults["accounts"] = None#accounts.Account().search(db, session['userSession'], views["accounts"])
    elif "projects" in views:
        searchResults["projects"] = None
    elif "employee" in views:
        searchResults["employee"] = None
    elif "consultants" in views:
        searchResults["consultants"] = None
    elif "contractors" in views:
        searchResults["contractors"] = None
    elif "profiles" in views:
        searchResults["profiles"] = None
    elif "views" in views:
        searchResults["views"] = None

    return jsonify({
        "results " : [{
            "id": row.view_name
        } for row in views]
    })

@app.route("/jobs")
@app.route("/jobs/myapplication")
def jobs():
    global db
    if db == None:
        db = DatabaseConnect(AppConfig.SQLALCHEMY_DATABASE_URI)

    views = utils.fetchSidebarLinks(db, None)    
    person = None

    if request.path == "/jobs":
        return render_template("jobs.html", hasSidebar=True, views=views)
    elif request.path == "/jobs/myapplication":
        if 'userSession' not in session:        
            return render_template("candidateApplications.html", hasSidebar=True, views=views, candidate=None)
        else:
            return render_template("candidateApplications.html", hasSidebar=True, views=views, candidate=session['userSession'])
        
@app.route("/people", defaults={'table': None, 'action' : "read", 'key': None }, methods=['GET'])
@app.route("/people/<table>", defaults={'action' : "read", 'key': None }, methods=['GET'])
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

    views = utils.fetchSidebarLinks(db, session['userSession'])    
    messages = {}
    employees = users.Person().fetchPersons(db, queryParams=" user_type = 'employee' ORDER BY id DESC")
    contractors = users.Person().fetchPersons(db, queryParams=" user_type = 'external' AND ext_type = 'CONTRACTOR' ORDER BY id DESC")
    consultants = users.Person().fetchPersons(db, queryParams=" user_type = 'external' AND ext_type = 'CONSULTANT' ORDER BY id DESC")
    response = { "employees" : employees, "contractors" : contractors, "consultants" : consultants  }    
    if request.method == 'GET':
        return render_template("people.html", hasSidebar=True, table=table, action=action, key=key, views=views, response=response)                
    elif request.method == 'POST':
        if action == "create":
            formData = dict(request.form)
            formData["password"] = AppConfig.DFLT_PASSWORD
            if table == "employees": 
                new_employee = users.Employee().createEmployeeForm(db, formData)
                response["messages"] = new_employee
            elif table == "contractors":
                formData["ext_type"] = "CONTRACTOR"
                new_contractor = users.External().createExternalForm(db, formData)
                response["messages"] = new_contractor
            elif table == "consultants":
                formData["ext_type"] = "CONSULTANT"
                consultant_profile = list(access.Profile().fetchProfiles(db, queryParams=" profile_name = 'HR'", queryLimit="1"))
                formData["profile_id"] = consultant_profile[0].id
                new_consultant = users.External().createExternalForm(db, formData)
                response["messages"] = new_consultant
            return render_template("people.html", hasSidebar=True, table=table, action=action, key=key, views=views, response=response)   
    return jsonify({
        "results " : request.method
    })

@app.route("/access",  defaults={'table': None, 'action' : "read", 'key': None }, methods=['GET'])
@app.route("/access/<table>/<action>", defaults={'key': None}, methods=['POST'])
@app.route("/access/<table>/<action>/<key>", methods=['GET','POST'])
def manageAccess(table, action, key):
    if 'userSession' not in session:        
        return redirect(url_for('login'))
        
    global db
    if db == None:
        db = DatabaseConnect(AppConfig.SQLALCHEMY_DATABASE_URI)

    views = utils.fetchSidebarLinks(db, session['userSession'])    

    if request.method == 'GET':
        if request.path == "/access":
            profiles = access.Profile().fetchProfilesWithPersonCount(db)
            viewList = access.View().fetchViews(db)
            response = { "profiles" : profiles, "views" : viewList }    
            return render_template("access.html", hasSidebar=True, action=action, key=key, views=views, response=response)
        elif "/access/profile/read" in request.path :
            pass

@app.route("/fetchData/<table>", defaults={'limit': 10})
@app.route("/fetchData/<table>/<limit>")   
def fetchData(table, limit):
    global db
    if db == None:
        db = DatabaseConnect(AppConfig.SQLALCHEMY_DATABASE_URI)

    if table == "profiles":
        results = access.Profile().fetchProfiles(db)
        response = [{
            "id": row.id , 
            "profile_name" : row.profile_name    
        } for row in results]
    elif table == "views":
        results = access.ProfileAccess().fetchProfileAccessByUsername(db, session['userSession'])
        response = [{
            "id": row.view_name , 
            "profile_name" : row.allow_read    
        } for row in results]
    
    if results != None:
        return jsonify({
            table : response})
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
def page_not_found(e):
    if 'userSession' not in session:        
        return redirect(url_for('login'))
    else:
        global db
        if db == None:
            db = DatabaseConnect(AppConfig.SQLALCHEMY_DATABASE_URI)

        views = utils.fetchSidebarLinks(db, session['userSession'])    
        return render_template('404.html', hasSidebar=True, views=views)

if __name__ == "__main__":
    app.run(debug=True)

