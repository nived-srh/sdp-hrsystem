from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker    
from .base import Model
from .access import Profile, ProfileAssignment, View, ViewAssignment
from .jobs import JobListing, JobApplication
from .accounts import Account, Project, ProjectAssignment
from .users import User, Employee, External, Candidate

def createDB(dbURL):
    engine = create_engine(dbURL, echo=True)
    Model.metadata.create_all(bind=engine)

def dropDB(dbURL):
    engine = create_engine(dbURL, echo=True)
    Model.metadata.drop_all(bind=engine)
