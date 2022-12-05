from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models.manageDB import createDB, dropDB

class DatabaseConnect():
    dbURI = ""
    session = None
    engine = None
    conn = None
    
    def __init__(self, dbURI):
        self.dbURI = dbURI

    def initiateEngine(self):        
        self.engine = create_engine(self.dbURI, echo=True)
        return self.engine

    def initiateConnection(self):        
        if self.engine == None:
            self.conn = self.initiateEngine().connect()
        else:
            self.conn = self.engine.connect()
        return self.conn

    def initiateSession(self):        
        if self.engine == None:
            Session = sessionmaker(bind=self.initiateEngine())
        else:
            Session = sessionmaker(bind=self.engine)
        
        self.session = Session()
        return self.session
    
    def commitSession(self):
        self.commitSession(self.session)

    def commitSession(self, session, autoClose = True):
        commitStatus = "Initiated"
        if session == None:
            session = self.initiateSession()
        
        try: 
            session.commit() 
            commitStatus = "Success"
        except Exception as err:
            print("Rollback Error", err)
            session.rollback()
            commitStatus = err
        finally: 
            if autoClose:
                self.closeSession(session)  
        return commitStatus          

    def closeSession(self, session):
        if self.session == session:
            session.close()
            self.session = None
        else:
            session.close()

    def executeQuery(self, sql, autoClose = True):        
        if self.session == None:
            self.session = self.initiateSession()

        try:
            results = self.session.execute(sql)
        except Exception as err:
            results = None
        finally: 
            if autoClose:
                self.closeSession(self.session)       
            return results     
            
    def createDatabase(self):
        print("Create DB")
        createDB(self.dbURI)

    def dropDatabase(self):
        print("Drop DB")
        dropDB(self.dbURI)
        
        
