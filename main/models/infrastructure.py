from . import base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

class ITResource(base.Model):
    __tablename__ = 'itresource'
    id = Column(Integer, primary_key=True)
    resource_name = Column(String, nullable=False)
    resource_descr = Column(String)
    resource_status = Column(Boolean, default="ACTIVE")
    resource_type = Column(String, default="HARDWARE")
    resource_serialnumber = Column(String, unique=True)
    resource_assignedto = Column(Integer, ForeignKey("person.id"))
    
    def __init__(self, formData = None):
        if formData != None:
            self.resource_name = formData["resource_name"]
            self.resource_descr = formData["resource_descr"] if "resource_descr" in formData else ""
            self.resource_status = str(formData["resource_status"] if "resource_status"  in formData else "ACTIVE").upper
            self.resource_type = formData["resource_status"] if "resource_status"  in formData else "HARDWARE"            
            self.resource_assignedto = formData["resource_assignedto"] if "resource_assignedto" in formData else None

    def createITResourceForm(self, db, formData):
        self.__init__(formData)
        return self.createITResource(db)

    def createITResource(self, db):
        try:
            session = db.initiateSession()
            session.add(self)
            commitStatus = db.commitSession(session)
            if commitStatus == "SUCCESS":
                return "INSERTED_ITRESOURCE"
            else:
                return "ERROR_" + commitStatus
        except Exception as err:
            return "ERROR : " + str(err)

    def editITResourceForm(self, db, formData):
        session = db.initiateSession()
        recordToEdit = session.query(ITResource).filter(ITResource.id==formData["resource_id"]).first()
        recordToEdit.tier_name = formData["tier_name"] 
        recordToEdit.tier_descr = formData["tier_descr"] 
        recordToEdit.tier_payscale = formData["tier_payscale"] 
        recordToEdit.tier_active = True if "tier_active" in formData else False
        recordToEdit.tier_default = True if "tier_default" in formData else False
        commitStatus = db.commitSession(session)
        return commitStatus

    def deleteITResources(self, db, recordIds):
        queryParams = "id IN (" + ','.join([ '\'' + rcdId + '\'' for rcdId in recordIds]) + ") AND tier_default != true"
        return db.deleteData('itresource', queryParams)

    def fetchByITResourceId(self, db, recordIds = []):
        params = ""
        if recordIds != [] and recordIds != None:
            if isinstance(recordIds, str):   
                params = 'id = \'' + recordIds + '\'' 
            elif isinstance(recordIds, list):
                params = 'id IN (' + ','.join([ '\'' + rcdId + '\'' for rcdId in recordIds]) + ')' 
            return db.fetchData('itresource', None, params, None) 
        return "ERROR_MISSING_ITRESOURCE_IDS"

    def fetchITResourcesWithDetails(self, db, queryFields = None, queryParams = None, queryLimit = None):
        return db.fetchData('itresource, person', "id, resource_name, resource_descr, resource_status, resource_type " , queryParams, queryLimit)

    def fetchITResources(self, db, queryFields = None, queryParams = None, queryLimit = None):
        return db.fetchData('itresource', queryFields, queryParams, queryLimit)
