from . import base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

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

    def editJobListingForm(self, db, formData):
        session = db.initiateSession()
        '''profileToEdit = session.query(Profile).filter(Profile.id==formData["profile_id"]).first()
        profileToEdit.profile_name = formData["profile_name"] 
        profileToEdit.profile_descr = formData["profile_descr"] 
        profileToEdit.profile_active = True if "profile_active" in formData else False'''
        commitStatus = db.commitSession(session)
        return commitStatus

    def deleteJobListing(self, db, recordIds):
        queryParams = "id IN (" + ','.join([ '\'' + prfid + '\'' for prfid in recordIds]) + ") AND profile_custom = true"
        return db.deleteData('profile', queryParams)

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
    application_status = Column(String)
    application_comment = Column(String)
    job_id = Column(Integer, ForeignKey("joblisting.id"))
    candidate_id = Column(Integer, ForeignKey("candidate.id"))
    jobListing = relationship("JobListing", back_populates="children")

    def __init__(self, formData = None):
        if formData != None:
            self.job_id = formData["job_title"]
            self.job_descr = formData["job_descr"] if "job_descr" in formData else ""
            self.job_exp = formData["job_exp"] if "job_exp" in formData else ""
            self.job_role = formData["job_role"] if "job_exp" in formData else ""
            self.job_status = formData["job_status"] if "job_exp" in formData else "OPEN"

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
