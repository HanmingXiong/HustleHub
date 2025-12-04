from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, CheckConstraint, TIMESTAMP, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class Users(Base):
    __tablename__ = 'users'
    
    user_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(100), unique=True, nullable=False)
    email = Column(String(150), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default='applicant', nullable=True)
    first_name = Column(String(100))
    last_name = Column(String(100))
    phone = Column(String(20))
    resume_file = Column(String(500))
    created_at = Column(TIMESTAMP, default=func.current_timestamp())
    
    employer = relationship("Employers", back_populates="user", uselist=False, cascade="all, delete")
    applications = relationship("Applications", back_populates="user", cascade="all, delete")
    notifications = relationship("Notifications", back_populates="user", cascade="all, delete")
    
    __table_args__ = (
        CheckConstraint("role IN ('applicant', 'employer', 'admin')", name='users_role_check'),
    )


class Employers(Base):
    __tablename__ = 'employers'
    
    employer_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    company_name = Column(String(150), nullable=False)
    description = Column(Text)
    website = Column(String(200))
    location = Column(String(100))
    
    user = relationship("Users", back_populates="employer")
    jobs = relationship("Jobs", back_populates="employer", cascade="all, delete")


class Jobs(Base):
    __tablename__ = 'jobs'
    
    job_id = Column(Integer, primary_key=True, autoincrement=True)
    employer_id = Column(Integer, ForeignKey('employers.employer_id', ondelete='CASCADE'), nullable=False)
    title = Column(String(150), nullable=False)
    description = Column(Text, nullable=False)
    job_type = Column(String(50))
    location = Column(String(100))
    pay_range = Column(String(50))
    date_posted = Column(TIMESTAMP, default=func.current_timestamp())
    is_active = Column(Boolean, default=True)
    
    employer = relationship("Employers", back_populates="jobs")
    applications = relationship("Applications", back_populates="job", cascade="all, delete")
    
    __table_args__ = (
        CheckConstraint("job_type IN ('full-time', 'part-time', 'gig', 'temporary', 'internship')", name='jobs_job_type_check'),
        Index('idx_jobs_location', 'location'),
        Index('idx_jobs_type', 'job_type'),
    )


class Applications(Base):
    __tablename__ = 'applications'
    
    application_id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(Integer, ForeignKey('jobs.job_id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    cover_letter = Column(Text)
    status = Column(String(20), default='pending')
    date_applied = Column(TIMESTAMP, default=func.current_timestamp())
    
    job = relationship("Jobs", back_populates="applications")
    user = relationship("Users", back_populates="applications")
    
    __table_args__ = (
        CheckConstraint("status IN ('pending', 'reviewed', 'accepted', 'rejected')", name='applications_status_check'),
        Index('idx_applications_user', 'user_id'),
        {'sqlite_autoincrement': True},
        
    )


class Notifications(Base):
    __tablename__ = 'notifications'
    
    notification_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, default=func.current_timestamp())
    
    user = relationship("Users", back_populates="notifications")
    
    __table_args__ = (
        Index('idx_notifications_user', 'user_id'),
    )

class FinancialResources(Base):
    __tablename__ = 'financial_resources'

    resource_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    website = Column(String(255), nullable=False)
    description = Column(Text)
    resource_type = Column(String(50), nullable=False)
    likes = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, default=func.current_timestamp())

    __table_args__ = (
        CheckConstraint("resource_type IN ('credit', 'budget', 'invest')", name='financial_resources_type_check'),
        Index('idx_financial_resources_type', 'resource_type'),
    )

class ResourceLikes(Base):
    __tablename__ = 'resource_likes'

    like_id = Column(Integer, primary_key=True, autoincrement=True)
    resource_id = Column(Integer, ForeignKey('financial_resources.resource_id', ondelete='CASCADE'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    created_at = Column(TIMESTAMP, default=func.current_timestamp())

    __table_args__ = (
        Index('idx_resource_likes_resource', 'resource_id'),
        Index('idx_resource_likes_user', 'user_id'),
        # Ensure a user can only like a resource once
        {'sqlite_autoincrement': True},
    )
