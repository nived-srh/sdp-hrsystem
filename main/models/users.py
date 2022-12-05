from . import base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker    

class User(base.Model):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    user_type = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False)
    __mapper_args__ = {'polymorphic_on': user_type}

    def __init__(self, email, password):
        self.is_active = True
        self.email = email
        self.username = email
        self.user_type = 'employee'
        self.hashed_password = generate_password_hash(password)

    def validateUser(self, db, username, password):
        try:
            result = self.fetchUsers(db, username)
            if result != None:
                for row in result:
                    if check_password_hash(row.hashed_password,password):
                        return row
                    else:
                        return None
        except Exception as err:
            return None
    
    def fetchUsers(self, db, usernames = []):
        session = db.initiateSession()
        sql = 'SELECT email, hashed_password, id, is_active FROM users'
        if usernames != [] and usernames != None:
            if isinstance(usernames, str):
                sql += ' WHERE email = \'' + usernames + '\'' 
            elif isinstance(usernames, list):
                sql += ' WHERE email IN (' + ','.join([ '\'' + usr + '\'' for usr in usernames]) + ')' 
        results = session.execute(sql)
        return results

    def insertUser(self, db, username, password):
        existingUsers = self.fetchUsers(db, username)
        if existingUsers == None or existingUsers == []:
            try:
                session = db.initiateSession()
                self.hashed_password = generate_password_hash(password)
                self.email = username
                session.add(self)
                commitStatus = db.commitSession(session, False)
                
                if commitStatus != "Success":
                    return "INSERTED_USER"
                else:
                    return "ERR:" + commitStatus
            except Exception as err:
                return "ERR:"
        else:
            return "DUPLICATE_USER"

    def insertUser(self, db, username, password):
        existingUsers = None #self.fetchUsers(db, username)
        if existingUsers == None or existingUsers == []:
            try:
                session = db.initiateSession()
                self.hashed_password = generate_password_hash(password)
                self.email = username
                session.add(self)
                commitStatus = db.commitSession(session, False)
                
                if commitStatus != "Success":
                    return "INSERTED_USER"
                else:
                    return "ERR:" + commitStatus
            except Exception as err:
                return "ERR:"
        else:
            return "DUPLICATE_USER"

class Employee(User):
    __mapper_args__ = {'polymorphic_identity': 'employee'}
    __tablename__ = 'employee'
    id = Column(None, ForeignKey('user.id'), primary_key=True)
    num_vacations = Column(Integer)

class External(User):
    __mapper_args__ = {'polymorphic_identity': 'external'}
    __tablename__ = 'external'
    id = Column(None, ForeignKey('user.id'), primary_key=True)
    ext_type = Column(String)

class Candidate(User):
    __mapper_args__ = {'polymorphic_identity': 'candidate'}
    __tablename__ = 'candidate'
    id = Column(None, ForeignKey('user.id'), primary_key=True)
    num_residents = Column(Integer)


