from . import base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

class DailyStatus(base.Model):
    __tablename__ = 'dailyStatus'
    id = Column(Integer, primary_key=True)
    status_descr = Column(String, nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("project.id"))
    employee_id = Column(Integer, ForeignKey("employee.id"))

class Vacation(base.Model):
    __tablename__ = 'vacation'
    id = Column(Integer, primary_key=True)
    vac_type = Column(String, nullable=False, index=True)
    vac_comment = Column(String)
    employee_id = Column(Integer, ForeignKey("employee.id"))