from flask import Flask, request, session, jsonify, render_template, redirect, url_for
from flask_cors import CORS
from config import AppConfig
from database import DatabaseConnect
from models import *

app = Flask(__name__)
CORS(app, supports_credentials=True)
app.config['SECRET_KEY'] = AppConfig.SECRET_KEY
app.config['PERMANENT_SESSION_LIFETIME'] = AppConfig.PERMANENT_SESSION_LIFETIME
db = None

@app.route("/")
def home():
    if 'userSession' not in session:        
        return redirect(url_for('login'))
    return render_template("base.html", hasSidebar=False)

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/login/submit", methods=['POST'])
def loginSubmit():
    global db
    if db == None:
        db = DatabaseConnect(AppConfig.SQLALCHEMY_DATABASE_URI)
    
    result = users.User().validateUser(db, request.form['username'], request.form['password'] )

    if result != None:
        session['userSession'] = result.email
        return redirect(url_for('home'))

@app.route("/jobs")
def jobs():
    global db
    if db == None:
        db = DatabaseConnect(AppConfig.SQLALCHEMY_DATABASE_URI)
    
    return render_template("jobs.html", hasSidebar=True, views="TestView")

@app.route("/logins", methods=['POST'])
def logins():
    global db
    if db == None:
        db = DatabaseConnect(AppConfig.SQLALCHEMY_DATABASE_URI)
    
    result = users.User().validateUser(db, request.json['username'], request.json['password'] )

    if result != None:
        session['userSession'] = result.email
        return jsonify({
            "id": result.id,
            "username": result.email,          
        })
    else:
        return jsonify({
             "error" : "UNAUTHORIZED",
             "errorDetail" : result
        }), 401

@app.route('/logout')
def logout():
    # remove the username from the session if it's there
    try:
        session.pop('userSession', None)
    except Exception as err:
        print(err)
    finally:         
        return redirect(url_for('login'))

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

@app.route("/createUser", methods=['POST'])
def createUser():
    global db
    if db == None:
        db = DatabaseConnect(AppConfig.SQLALCHEMY_DATABASE_URI)
    
    userId = users.User().insertUser(db, request.json["username"],request.json["password"])

    '''
    if userId != None:
        session['usersession'] = request.json["username"]
    '''
    return userId
    
@app.route("/fetchUsers", methods=['GET'])
def fetchUsers():
    global db
    if db == None:
        db = DatabaseConnect(AppConfig.SQLALCHEMY_DATABASE_URI)
    if request.args.getlist('username') != None:
        results = users.User().fetchUsers(db, request.args.getlist('username'))
    else:        
        results = users.User().fetchUsers(db)
    
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

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('404.html', hasSidebar=False), 404

if __name__ == "__main__":
    app.run(debug=True)