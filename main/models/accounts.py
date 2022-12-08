from . import base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

class Account(base.Model):
    __tablename__ = 'account'
    id = Column(Integer, primary_key=True)
    acc_name = Column(String, nullable=False, index=True)
    acc_type = Column(String, nullable=False, index=True)
    acc_status = Column(String, nullable=False, index=True, default="ACTIVE")
    children = relationship("Project", back_populates="account")

class Project(base.Model):
    __tablename__ = 'project'
    id = Column(Integer, primary_key=True)
    description = Column(String)
    account_id = Column(Integer, ForeignKey("account.id"))
    account = relationship("Account", back_populates="children")
    children = relationship("ProjectAssignment", back_populates="project")
    
class ProjectAssignment(base.Model):
    __tablename__ = 'projectassignment'
    id = Column(Integer, primary_key=True)
    role = Column(String, nullable=False, index=True)
    account_id = Column(Integer, ForeignKey("project.id"))
    person_id = Column(Integer, ForeignKey("person.id"))
    project = relationship("Project", back_populates="children")
