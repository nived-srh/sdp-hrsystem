from flask import Flask, request, session, jsonify, render_template, redirect, url_for
from flask_cors import CORS
from .config import AppConfig
from .database import DatabaseConnect
from .models import *

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['SECRET_KEY'] = AppConfig.SECRET_KEY
app.config['PERMANENT_SESSION_LIFETIME'] = AppConfig.PERMANENT_SESSION_LIFETIME
db = None

@app.route("/")
def home():
    if 'userSession' not in session:        
        return redirect(url_for('login'))
    return render_template("base.html", hasSidebar=True)

@app.route("/login", methods=['GET','POST'])
def login():
    if request.method == 'POST':
        global db
        if db == None:
            db = DatabaseConnect(AppConfig.SQLALCHEMY_DATABASE_URI)
        
        result = users.Person().validatePerson(db, request.form['username'], request.form['password'] )
        
        if result != None:
            session['userSession'] = result.email
            return redirect(url_for('home'))

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

@app.route("/createUser", methods=['POST'])
def createUser():
    global db
    if db == None:
        db = DatabaseConnect(AppConfig.SQLALCHEMY_DATABASE_URI)
    
    response = users.Person().createPersonForm(db, request.form)

    '''
    if userId != None:
        session['usersession'] = request.json["username"]
    '''
    #return render_template("jobs.html", hasSidebar=True, views=[ userId ,"Logout"])

    return jsonify({
        "results " : response
    })
    
@app.route("/fetchUsers", methods=['GET'])
def fetchUsers():
    global db
    if db == None:
        db = DatabaseConnect(AppConfig.SQLALCHEMY_DATABASE_URI)
    if request.args.getlist('username') != None:
        results = users.Person().fetchUsers(db, request.args.getlist('username'))
    else:        
        results = users.Person().fetchUsers(db)
    
    if results != None:
        return jsonify({
            "users" : [{
            "id": row.id,
            "username": row.email,          
        } for row in results]})
    else:
        return jsonify({
             "error" : "UNAUTHORIZED",
             "errorDetail" : results
        }), 401

@app.route("/jobs")
def jobs():
    global db
    if db == None:
        db = DatabaseConnect(AppConfig.SQLALCHEMY_DATABASE_URI)
    
    return render_template("jobs.html", hasSidebar=True, views=["Home","Logout"])

@app.route("/emp/<action>", defaults={'key': None})
@app.route("/emp/<action>/<key>")
def emp(action,key):
    global db
    if db == None:
        db = DatabaseConnect(AppConfig.SQLALCHEMY_DATABASE_URI)
    
    return jsonify({
        "results " : action + '' +  (key if key != None else "noo")
    })

@app.route("/employee")
def employee():
    if 'userSession' not in session:        
        return redirect(url_for('login'))
    global db
    if db == None:
        db = DatabaseConnect(AppConfig.SQLALCHEMY_DATABASE_URI)
    
    return render_template("employees.html", hasSidebar=True, views=["Home","Logout"])

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
    # note that we set the 404 status explicitly
    return render_template('404.html', hasSidebar=False), 404

if __name__ == "__main__":
    app.run(debug=True)

'''
@app.route("/validateSession", methods=['POST'])
def validateSession():
    if 'userSession' in session:
        if session['userSession'] == request.json['usersession']:
            return "AUTHORIZED", 200
    return "UNAUTHORIZED", 401
 
@app.route("/getSession", methods=['GET'])
def getSession():
    if 'userSession' in session:
        return jsonify({"userSession" : session['userSession']})
    return 'NO_SESSION_FOUND', 404
'''
