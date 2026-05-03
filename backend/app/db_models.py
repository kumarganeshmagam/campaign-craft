"""
SQLAlchemy database models for CampaignCraft v2.0
Supports PostgreSQL or SQLite backend
"""

from datetime import datetime
from typing import Optional, List, Dict
import json
from sqlalchemy import create_engine, Column, String, Integer, Float, DateTime, Text, ForeignKey, JSON, Boolean, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum

Base = declarative_base()


class CampaignStatus(str, enum.Enum):
    PENDING = "pending"
    RESEARCH = "research"
    STAKEHOLDER_ANALYSIS = "stakeholder_analysis"
    USE_CASE_GENERATION = "use_case_generation"
    PROPOSAL_GENERATION = "proposal_generation"
    OUTREACH_READY = "outreach_ready"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ContactPriority(str, enum.Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class OutreachChannel(str, enum.Enum):
    EMAIL = "email"
    LINKEDIN = "linkedin"
    CALL = "call"
    TWITTER = "twitter"


class OutreachStatus(str, enum.Enum):
    DRAFT = "draft"
    APPROVED = "approved"
    SENT = "sent"
    OPENED = "opened"
    CLICKED = "clicked"
    REPLIED = "replied"
    BOUNCED = "bounced"


class Campaign(Base):
    __tablename__ = "campaigns"
    
    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    query = Column(Text, nullable=False)
    status = Column(Enum(CampaignStatus), default=CampaignStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    companies = relationship("Company", back_populates="campaign", cascade="all, delete-orphan")
    contacts = relationship("Contact", back_populates="campaign", cascade="all, delete-orphan")
    use_cases = relationship("UseCase", back_populates="campaign", cascade="all, delete-orphan")
    proposals = relationship("Proposal", back_populates="campaign", cascade="all, delete-orphan")
    outreach = relationship("Outreach", back_populates="campaign", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="campaign", cascade="all, delete-orphan")
    agent_logs = relationship("AgentLog", back_populates="campaign", cascade="all, delete-orphan")


class Company(Base):
    __tablename__ = "companies"
    
    id = Column(String(36), primary_key=True)
    campaign_id = Column(String(36), ForeignKey("campaigns.id"), nullable=False)
    name = Column(String(255), nullable=False)
    industry = Column(String(255))
    revenue = Column(String(100))
    employees = Column(Integer)
    website = Column(String(500))
    description = Column(Text)
    
    # Data storage
    data_json = Column(JSON, default={})  # Full company profile from research
    pain_points = Column(JSON, default=[])  # Array of identified pain points
    tech_stack = Column(JSON, default=[])  # Technologies they use
    recent_news = Column(JSON, default=[])  # Recent news/updates
    
    # Scoring
    confidence_score = Column(Float, default=0.0)  # 0-1 research confidence
    relevance_score = Column(Float, default=0.0)  # 0-1 relevance to campaign
    
    # Metadata
    sources = Column(JSON, default=[])  # Where we found this company
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    campaign = relationship("Campaign", back_populates="companies")
    contacts = relationship("Contact", back_populates="company", cascade="all, delete-orphan")
    use_cases = relationship("UseCase", back_populates="company", cascade="all, delete-orphan")


class Contact(Base):
    __tablename__ = "contacts"
    
    id = Column(String(36), primary_key=True)
    campaign_id = Column(String(36), ForeignKey("campaigns.id"), nullable=False)
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False)
    
    name = Column(String(255), nullable=False)
    title = Column(String(255))
    department = Column(String(255))
    email = Column(String(255))
    phone = Column(String(20))
    linkedin_url = Column(String(500))
    twitter = Column(String(255))
    
    # Engagement data
    recent_posts = Column(JSON, default=[])
    interests = Column(JSON, default=[])
    engagement_signals = Column(JSON, default={})
    
    # Scoring
    priority_score = Column(Float, default=0.0)  # 0-1 priority for outreach
    confidence_score = Column(Float, default=0.0)  # 0-1 research confidence
    seniority_level = Column(String(50))  # C-suite, VP, Director, Manager, Individual Contributor
    
    # Metadata
    sources = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    campaign = relationship("Campaign", back_populates="contacts")
    company = relationship("Company", back_populates="contacts")
    outreach = relationship("Outreach", back_populates="contact", cascade="all, delete-orphan")


class UseCase(Base):
    __tablename__ = "use_cases"
    
    id = Column(String(36), primary_key=True)
    campaign_id = Column(String(36), ForeignKey("campaigns.id"), nullable=False)
    company_id = Column(String(36), ForeignKey("companies.id"), nullable=False)
    
    title = Column(String(255), nullable=False)
    problem_statement = Column(Text)
    proposed_solution = Column(Text)
    expected_roi = Column(String(255))
    value_metrics = Column(JSON, default=[])
    implementation_timeline = Column(String(255))
    
    # Ranking
    relevance_score = Column(Float, default=0.0)  # 0-1 relevance to company
    confidence_score = Column(Float, default=0.0)  # 0-1 generation confidence
    conversion_likelihood = Column(Float, default=0.0)  # Historical conversion rate
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_approved = Column(Boolean, default=False)
    
    # Relationships
    campaign = relationship("Campaign", back_populates="use_cases")
    company = relationship("Company", back_populates="use_cases")
    proposals = relationship("Proposal", back_populates="use_case", cascade="all, delete-orphan")


class Proposal(Base):
    __tablename__ = "proposals"
    
    id = Column(String(36), primary_key=True)
    campaign_id = Column(String(36), ForeignKey("campaigns.id"), nullable=False)
    use_case_id = Column(String(36), ForeignKey("use_cases.id"), nullable=False)
    
    variant_type = Column(String(50))  # executive, technical, roi_focused
    executive_summary = Column(Text)
    detailed_content = Column(Text)
    deliverables = Column(JSON, default=[])
    pricing_tiers = Column(JSON, default=[])
    case_studies = Column(JSON, default=[])
    
    version = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_approved = Column(Boolean, default=False)
    
    # Relationships
    campaign = relationship("Campaign", back_populates="proposals")
    use_case = relationship("UseCase", back_populates="proposals")
    outreach = relationship("Outreach", back_populates="proposal")


class Outreach(Base):
    __tablename__ = "outreach"
    
    id = Column(String(36), primary_key=True)
    campaign_id = Column(String(36), ForeignKey("campaigns.id"), nullable=False)
    contact_id = Column(String(36), ForeignKey("contacts.id"), nullable=False)
    proposal_id = Column(String(36), ForeignKey("proposals.id"))
    
    channel = Column(Enum(OutreachChannel), nullable=False)
    subject = Column(String(500))
    content = Column(Text, nullable=False)
    personalization_hooks = Column(JSON, default=[])
    
    sequence_step = Column(Integer, default=1)  # 1 = initial, 2+ = follow-ups
    status = Column(Enum(OutreachStatus), default=OutreachStatus.DRAFT)
    
    sent_at = Column(DateTime)
    opened_at = Column(DateTime)
    clicked_at = Column(DateTime)
    replied_at = Column(DateTime)
    
    engagement_score = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    campaign = relationship("Campaign", back_populates="outreach")
    contact = relationship("Contact", back_populates="outreach")
    proposal = relationship("Proposal", back_populates="outreach")


class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(String(36), primary_key=True)
    campaign_id = Column(String(36), ForeignKey("campaigns.id"), nullable=False)
    
    # Can be tied to different entity types
    entity_type = Column(String(50))  # campaign, company, use_case, proposal, contact
    entity_id = Column(String(36))
    
    context = Column(JSON, default={})  # Context for the conversation
    messages = Column(JSON, default=[])  # Array of {role, content, timestamp}
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    campaign = relationship("Campaign", back_populates="conversations")


class AgentLog(Base):
    __tablename__ = "agent_logs"
    
    id = Column(String(36), primary_key=True)
    campaign_id = Column(String(36), ForeignKey("campaigns.id"), nullable=False)
    
    agent_name = Column(String(255), nullable=False)
    agent_type = Column(String(50))  # research, stakeholder, usecase, proposal, outreach, manager
    
    task_input = Column(JSON)
    task_output = Column(JSON)
    reasoning = Column(Text)
    
    tools_used = Column(JSON, default=[])  # List of tools called
    sources = Column(JSON, default=[])  # Data sources used
    
    confidence_score = Column(Float)
    execution_time = Column(Float)  # seconds
    
    status = Column(String(50))  # success, error, partial
    error_message = Column(Text)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    campaign = relationship("Campaign", back_populates="agent_logs")


class Metrics(Base):
    __tablename__ = "metrics"
    
    id = Column(String(36), primary_key=True)
    
    # Aggregate metrics for learning
    industry = Column(String(255))
    use_case_type = Column(String(255))
    contact_role = Column(String(255))
    outreach_style = Column(String(255))
    
    # Success rates
    open_rate = Column(Float, default=0.0)
    click_rate = Column(Float, default=0.0)
    reply_rate = Column(Float, default=0.0)
    conversion_rate = Column(Float, default=0.0)
    
    total_attempts = Column(Integer, default=0)
    successful_conversions = Column(Integer, default=0)
    
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def init_db(database_url: str = "sqlite:///campaigncraft.db"):
    """Initialize database connection and create tables"""
    engine = create_engine(database_url, echo=False)
    Base.metadata.create_all(engine)
    return engine
