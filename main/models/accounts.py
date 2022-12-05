from . import base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

class Account(base.Model):
    __tablename__ = 'account'
    id = Column(Integer, primary_key=True)
    profile_name = Column(String, nullable=False, index=True)
    children = relationship("Project", back_populates="Account")

class Project(base.Model):
    __tablename__ = 'project'
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("account.id"))
    children = relationship("ProjectAssignment", back_populates="Project")
    
class ProjectAssignment(base.Model):
    __tablename__ = 'projectAssignment'
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey("project.id"))
