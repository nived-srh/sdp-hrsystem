from . import base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

class DailyStatus(base.Model):
    __tablename__ = 'dailystatus'
    id = Column(Integer, primary_key=True)
    status_descr = Column(String, nullable=False, index=True)
    work_hours = Column(Integer, nullable=False, index=True)
    project_id = Column(Integer, ForeignKey("project.id"))
    employee_id = Column(Integer, ForeignKey("person.id"))

    def __init__(self, formData = None):
        if formData != None:
            self.status_descr = formData["status_descr"]
            self.work_hours = formData["work_hours"]
            self.employee_id = formData["employee_id"]

    def fetchDailyStatus(self, db, queryFields = None, queryParams = None, queryLimit = None):
        return db.fetchData('dailystatus', queryFields, queryParams, queryLimit)

class Vacation(base.Model):
    __tablename__ = 'vacation'
    id = Column(Integer, primary_key=True)
    vac_type = Column(String, nullable=False, index=True)
    vac_comment = Column(String)
    employee_id = Column(Integer, ForeignKey("person.id"))

    def __init__(self, formData = None):
        if formData != None:
            self.vac_type = formData["vac_type"]
            self.vac_comment = formData["vac_comment"]
            self.employee_id = formData["employee_id"]
