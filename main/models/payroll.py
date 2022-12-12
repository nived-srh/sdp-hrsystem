from . import base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

class Tier(base.Model):
    __tablename__ = 'tier'
    id = Column(Integer, primary_key=True)
    tier_name = Column(String, nullable=False)
    tier_payscale = Column(Integer, nullable=False)
    
class Payroll(base.Model):
    __tablename__ = 'payroll'
    id = Column(Integer, primary_key=True)
    proll_month = Column(String, nullable=False)
    proll_year = Column(String, nullable=False)
    proll_status = Column(String, nullable=False)
    proll_details = relationship("PayrollDetails", back_populates="payroll")
    
class PayrollDetails(base.Model):
    __tablename__ = 'payrolldetails'
    id = Column(Integer, primary_key=True)
    prdetail_amount = Column(Integer, nullable=False)
    prdetail_bonus = Column(Integer, nullable=False)
    prdetail_status = Column(String, nullable=False)
    payroll_id = Column(Integer, ForeignKey("payroll.id"))
    payroll = relationship("Payroll", back_populates="proll_details")