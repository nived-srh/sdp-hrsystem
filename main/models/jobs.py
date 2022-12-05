from . import base
from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

class JobListing(base.Model):
    __tablename__ = 'jobListing'
    id = Column(Integer, primary_key=True)
    job_name = Column(String, nullable=False, index=True)
    job_descr = Column(String)
    job_exp = Column(String)
    job_type = Column(String)
    job_status = Column(String(10))
    created_at = Column(String)
    children = relationship("JobApplication", back_populates="JobListing")

class JobApplication(base.Model):
    __tablename__ = 'jobApplication'
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey("profile.id"))
    candidate_id = Column(Integer, ForeignKey("candidate.id"))