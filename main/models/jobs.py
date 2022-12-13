from . import base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

class JobListing(base.Model):
    __tablename__ = 'joblisting'
    id = Column(Integer, primary_key=True)
    job_name = Column(String, nullable=False, index=True)
    job_descr = Column(String)
    job_exp = Column(String)
    job_type = Column(String)
    job_status = Column(String(10))
    created_at = Column(String)
    children = relationship("JobApplication", back_populates="jobListing")

    def __init__(self, formData = None):
        if formData != None:
            self.job_name = formData["job_name"]
            self.job_descr = formData["job_descr"] if "job_descr" in formData else ""
            self.job_exp = formData["job_exp"] if "job_exp" in formData else ""
            self.job_type = formData["job_type"] if "job_exp" in formData else ""
            self.job_status = formData["job_status"] if "job_exp" in formData else "OPEN"
            self.employee_id = formData["employee_id"] if "employee_id" in formData else None

    def createJobListing(self, db, formData):
        self.__init__(formData)
        return self.createJobListing(db)

    def createJobListing(self, db):
        try:
            session = db.initiateSession()
            session.add(self)
            commitStatus = db.commitSession(session)
            if commitStatus == "SUCCESS":
                return "INSERTED_JOBLISTING"
            else:
                return "ERROR_" + commitStatus
        except Exception as err:
            return "ERROR : " + str(err)

    def fetchJobListing(self, db, queryFields = None, queryParams = None, queryLimit = None):
        return db.fetchData('joblisting', queryFields, queryParams, queryLimit)

class JobApplication(base.Model):
    __tablename__ = 'jobapplication'
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey("joblisting.id"))
    candidate_id = Column(Integer, ForeignKey("candidate.id"))
    jobListing = relationship("JobListing", back_populates="children")