from . import base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

class Profile(base.Model):
    __tablename__ = 'profile'
    id = Column(Integer, primary_key=True)
    profile_name = Column(String, nullable=False, index=True)
    children = relationship("ProfileAssignment", back_populates="Profile")

class ProfileAssignment(base.Model):
    __tablename__ = 'profileAssignment'
    id = Column(Integer, primary_key=True)
    profile_id = Column(Integer, ForeignKey("profile.id"))
    user_id = Column(Integer, ForeignKey("user.id"))

class View(base.Model):
    __tablename__ = 'view'
    id = Column(Integer, primary_key=True)
    view_name = Column(String, nullable=False, index=True) 
    children = relationship("ViewAssignment", back_populates="View")

class ViewAssignment(base.Model):
    __tablename__ = 'viewAssignment'
    id = Column(Integer, primary_key=True)
    view_id = Column(Integer, ForeignKey("view.id"))
    profile_id = Column(Integer, ForeignKey("profile.id"))