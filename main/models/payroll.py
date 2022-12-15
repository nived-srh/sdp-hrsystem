from . import base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

class Tier(base.Model):
    __tablename__ = 'tier'
    id = Column(Integer, primary_key=True)
    tier_name = Column(String, nullable=False)
    tier_descr = Column(String)
    tier_payscale = Column(Integer, default=0)
    tier_active = Column(Boolean, default=True)
    tier_default = Column(Boolean, default=False)
    persons = relationship("Employee", back_populates="tier")
    
    def __init__(self, formData = None):
        if formData != None:
            self.tier_name = formData["tier_name"]
            self.tier_descr = formData["tier_descr"] if "tier_descr" in formData else ""
            self.tier_payscale = formData["tier_payscale"] if "tier_payscale" in formData else 0
            self.tier_active = formData["tier_active"] if "tier_active" in formData else False
            self.tier_default = formData["tier_default"] if "tier_default" in formData else False

    def createTierForm(self, db, formData):
        self.__init__(formData)
        return self.createTier(db)

    def createTier(self, db):
        try:
            session = db.initiateSession()
            session.add(self)
            commitStatus = db.commitSession(session)
            if commitStatus == "SUCCESS":
                return "INSERTED_TIER"
            else:
                return "ERROR_" + commitStatus
        except Exception as err:
            return "ERROR : " + str(err)

    def editTierForm(self, db, formData):
        session = db.initiateSession()
        recordToEdit = session.query(Tier).filter(Tier.id==formData["tier_id"]).first()
        recordToEdit.tier_name = formData["tier_name"] 
        recordToEdit.tier_descr = formData["tier_descr"] 
        recordToEdit.tier_payscale = formData["tier_payscale"] 
        recordToEdit.tier_active = True if "tier_active" in formData else False
        recordToEdit.tier_default = True if "tier_default" in formData else False
        commitStatus = db.commitSession(session)
        return commitStatus

    def deleteTier(self, db, recordIds):
        queryParams = "id IN (" + ','.join([ '\'' + rcdId + '\'' for rcdId in recordIds]) + ") AND tier_default != true"
        return db.deleteData('tier', queryParams)

    def fetchByTierId(self, db, recordIds = []):
        params = ""
        if recordIds != [] and recordIds != None:
            if isinstance(recordIds, str):   
                params = 'id = \'' + recordIds + '\'' 
            elif isinstance(recordIds, list):
                params = 'id IN (' + ','.join([ '\'' + rcdId + '\'' for rcdId in recordIds]) + ')' 
            return db.fetchData('tier', None, params, None) 
        return "ERROR_MISSING_TIERIDS"

    def fetchTierWithUserCount(self, db, queryFields = None, queryParams = None, queryLimit = None):
        return db.fetchData('tier, person', "id, tier_name, tier_descr, tier_active, tier_default, tier_payscale, (SELECT COUNT(id) FROM person WHERE person.tier_id = tier.id)" , queryParams, queryLimit)

    def fetchTiers(self, db, queryFields = None, queryParams = None, queryLimit = None):
        return db.fetchData('tier', queryFields, queryParams, queryLimit)

class Payroll(base.Model):
    __tablename__ = 'payroll'
    id = Column(Integer, primary_key=True)
    proll_month = Column(String, nullable=False)
    proll_year = Column(String, nullable=False)
    proll_status = Column(String, nullable=False, default="DRAFT")
    proll_externalid = Column(String, unique=True, nullable=False)
    proll_details = relationship("PayrollDetails", back_populates="payroll")
    
    def __init__(self, formData = None):
        if formData != None:
            if formData["proll_period"] != None:
                period = formData["proll_period"].split("-")
                self.proll_month = period[1]
                self.proll_year = period[0]
                self.proll_status = str(formData["proll_status"] if "proll_status" in formData else "DRAFT").upper()
                self.proll_externalid = self.proll_month.lower() + '_' + self.proll_year.lower()  + '_' +  self.proll_status

    def createPayrollForm(self, db, formData):
        self.__init__(formData)
        return self.createPayroll(db)

    def createPayroll(self, db):
        try:
            session = db.initiateSession()
            session.add(self)
            commitStatus = db.commitSession(session)
            if commitStatus == "SUCCESS":
                return "INSERTED_PAYROLL"
            else:
                return "ERROR_" + commitStatus
        except Exception as err:
            return "ERROR : " + str(err)

    def editPayrollForm(self, db, formData):
        session = db.initiateSession()
        recordToEdit = session.query(Payroll).filter(Payroll.id==formData["payroll_id"]).first()
        recordToEdit.proll_month = formData["proll_month"] 
        recordToEdit.proll_year = formData["proll_year"] 
        recordToEdit.proll_status = formData["proll_status"] 
        commitStatus = db.commitSession(session)
        return commitStatus

    def deletePayroll(self, db, recordIds):
        queryParams = "id IN (" + ','.join([ '\'' + rcdId + '\'' for rcdId in recordIds]) + ") AND proll_status = 'DRAFT'"
        return db.deleteData('payroll', queryParams)

    def fetchByPayrollId(self, db, recordIds = []):
        params = ""
        if recordIds != [] and recordIds != None:
            if isinstance(recordIds, str):   
                params = 'id = \'' + recordIds + '\'' 
            elif isinstance(recordIds, list):
                params = 'id IN (' + ','.join([ '\'' + rcdId + '\'' for rcdId in recordIds]) + ')' 
            return db.fetchData('payroll', None, params, None) 
        return "ERROR_MISSING_PAYROLLIDS"

    def fetchPayrolls(self, db, queryFields = None, queryParams = None, queryLimit = None):
        return db.fetchData('payroll', queryFields, queryParams, queryLimit)

    '''
    def fetchTierWithUserCount(self, db, queryFields = None, queryParams = None, queryLimit = None):
        return db.fetchData('tier, person', "id, tier_name, tier_descr, tier_active, tier_default, tier_payscale, (SELECT COUNT(id) FROM person WHERE person.tier_id = tier.id)" , queryParams, queryLimit)
    '''

class PayrollDetails(base.Model):
    __tablename__ = 'payrolldetails'
    id = Column(Integer, primary_key=True)
    prdetail_amount = Column(Integer, nullable=False)
    prdetail_bonus = Column(Integer, nullable=False)
    prdetail_status = Column(String, nullable=False)
    payroll_id = Column(Integer, ForeignKey("payroll.id"))
    payroll = relationship("Payroll", back_populates="proll_details")