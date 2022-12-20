from . import base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from datetime import date

class JobListing(base.Model):
    __tablename__ = 'joblisting'
    id = Column(Integer, primary_key=True)
    job_title = Column(String, nullable=False, index=True)
    job_descr = Column(String)
    job_exp = Column(String)
    job_role = Column(String)
    job_location = Column(String)
    job_status = Column(String(10))
    created_at = Column(String)
    children = relationship("JobApplication", back_populates="jobListing")

    def __init__(self, formData = None):
        if formData != None:
            self.job_title = formData["job_title"]
            self.job_descr = formData["job_descr"] if "job_descr" in formData else ""
            self.job_exp = formData["job_exp"] if "job_exp" in formData else ""
            self.job_role = formData["job_role"] if "job_role" in formData else ""
            self.job_status = formData["job_status"] if "job_status" in formData else "OPEN"
            self.job_location = formData["job_status"] if "job_status" in formData else "TBD"

    def createJobListingForm(self, db, formData):
        self.__init__(formData)
        self.created_at = date.today()
        return self.createJobListing(db)

    def createJobListing(self, db):
        try:
            session = db.initiateSession()
            session.add(self)
            commitStatus = db.commitSession(session)
            if commitStatus == "SUCCESS":
                return "INSERTED_JOBLISTING"
            else:
                return "ERROR_DBCOMMIT"
        except Exception as err:
            if "duplicate key" in str(err):
                return "ERROR : DUPLICATE KEY" 
            return "ERROR_INS_JOBLISTING" 

    def editJobListingForm(self, db, formData):
        session = db.initiateSession()
        joblistingToEdit = session.query(JobListing).filter(JobListing.id==formData["joblisting_id"]).first()
        joblistingToEdit.job_title = formData["job_title"] if "job_title" in formData else ""
        joblistingToEdit.job_descr = formData["job_descr"] if "job_descr" in formData else ""
        joblistingToEdit.job_exp = formData["job_exp"] if "job_exp" in formData else ""
        joblistingToEdit.job_role = formData["job_role"] if "job_role" in formData else ""
        joblistingToEdit.job_status = formData["job_status"] if "job_status" in formData else "OPEN"
        joblistingToEdit.job_location = formData["job_status"] if "job_status" in formData else "TBD"
        commitStatus = db.commitSession(session)
        return commitStatus

    def deleteJobListing(self, db, recordIds):
        queryParams = "id IN (" + ','.join([ '\'' + rcid + '\'' for rcid in recordIds]) + ") "
        return db.deleteData('joblisting', queryParams)

    def fetchByJobListingId(self, db, jobListingIds = []):
        if jobListingIds != [] and jobListingIds != None:
            if isinstance(jobListingIds, str):   
                params = 'id = \'' + jobListingIds + '\'' 
            elif isinstance(jobListingIds, list):
                params = 'id IN (' + ','.join([ '\'' + jl + '\'' for jl in jobListingIds]) + ')' 
            return db.fetchData('joblisting', None, params, None) 
        return "ERROR_MISSING_JOBLISTINGIDS"

    def fetchJobListingWithApplicantCount(self, db, queryFields = None, queryParams = None, queryLimit = None):
        return db.fetchData('joblisting', "id, job_title, job_descr, job_exp, job_location, job_status, job_role, (SELECT COUNT(id) FROM jobapplication WHERE jobapplication.job_id = joblisting.id)" , queryParams, queryLimit)

    def fetchJobListings(self, db, queryFields = None, queryParams = None, queryLimit = None):
        return db.fetchData('joblisting', queryFields, queryParams, queryLimit)

class JobApplication(base.Model):
    __tablename__ = 'jobapplication'
    id = Column(Integer, primary_key=True)
    application_status = Column(String, default="APPLIED")
    application_comment = Column(String, default="")
    job_id = Column(Integer, ForeignKey("joblisting.id"))
    candidate_id = Column(Integer, ForeignKey("candidate.id"))
    jobListing = relationship("JobListing", back_populates="children")

    def __init__(self, formData = None):
        if formData != None:
            self.job_id = formData["job_id"]
            self.candidate_id = formData["candidate_id"]
            self.application_status = formData["application_status"] if "application_status" in formData else "APPLIED"

    def createJobApplicationForm(self, db, formData):
        if "job_id" in formData and "candidate_id" in formData:
            self.__init__(formData)
            self.createJobApplication(db)
            
        return "ERROR_MISSING_REQUIRED_IDS"

    def createJobApplication(self, db):
        try:
            session = db.initiateSession()
            session.add(self)
            commitStatus = db.commitSession(session)
            if commitStatus == "SUCCESS":
                return "INSERTED_JOBAPPLICATION"
            else:
                return "ERROR_DBCOMMIT"
        except Exception as err:
            if "duplicate key" in str(err):
                return "ERROR : DUPLICATE KEY" 
            return "ERROR_INS_JOBAPPLCATION" 

    def updateApplicationStatus(self, db, recordId, status):
        session = db.initiateSession()
        itemToEdit = session.query(JobApplication).filter(JobApplication.id==str(recordId)).first()
        itemToEdit.application_status = status.upper()        
        commitStatus = db.commitSession(session)
        return commitStatus

    def deleteJobApplication(self, db, recordIds):
        queryParams = "id IN (" + ','.join([ '\'' + rcid + '\'' for rcid in recordIds]) + ") "
        return db.deleteData('jobapplication', queryParams)

    def fetchJobApplication(self, db, queryFields = None, queryParams = None, queryLimit = None):
        return db.fetchData('jobapplication', queryFields, queryParams, queryLimit)
        
    def fetchJobApplicationWithDetails(self, db, queryFields = None, queryParams = None, queryLimit = None):
        if queryParams == None:
            queryParams = " jobapplication.job_id = joblisting.id AND jobapplication.candidate_id = candidate.id AND candidate.id = person.id ORDER BY joblisting.job_title"
        return db.fetchData('jobapplication, joblisting, candidate, person', "jobapplication.id, application_status, application_comment, job_title, job_descr, email, first_name, last_name, candidate_id", queryParams, queryLimit)
