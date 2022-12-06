from . import base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from werkzeug.security import generate_password_hash, check_password_hash

class Person(base.Model):
    __tablename__ = 'person'
    id = Column(Integer, primary_key=True)
    user_type = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, nullable=False)
    __mapper_args__ = {'polymorphic_on': user_type}

    def __init__(self):
        self.is_active = True

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
        sql = 'SELECT email, hashed_password, id, is_active FROM person'
        if usernames != [] and usernames != None:
            if isinstance(usernames, str):
                sql += ' WHERE email = \'' + usernames + '\'' 
            elif isinstance(usernames, list):
                sql += ' WHERE email IN (' + ','.join([ '\'' + usr + '\'' for usr in usernames]) + ')' 
        results = session.execute(sql)
        return results

    def insertUser(self, db, username, password, userType = 'employee'):
        existingUsers = None #self.fetchUsers(db, username)
        if existingUsers == None or existingUsers == []:
            try:
                session = db.initiateSession()
                self.hashed_password = generate_password_hash(password)
                self.email = username
                self.username = username
                self.user_type = userType
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

class Employee(Person):
    __mapper_args__ = {'polymorphic_identity': 'employee'}
    __tablename__ = 'employee'
    id = Column(None, ForeignKey('person.id'), primary_key=True)
    num_vacations = Column(Integer)

class External(Person):
    __mapper_args__ = {'polymorphic_identity': 'external'}
    __tablename__ = 'external'
    id = Column(None, ForeignKey('person.id'), primary_key=True)
    ext_type = Column(String)

class Candidate(Person):
    __mapper_args__ = {'polymorphic_identity': 'candidate'}
    __tablename__ = 'candidate'
    id = Column(None, ForeignKey('person.id'), primary_key=True)
    num_residents = Column(Integer)


