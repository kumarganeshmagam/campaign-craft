"""
V2.0 Campaign API Endpoints
New endpoints for agentic workflow with approval gates and detailed agent tracking.
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from pydantic import BaseModel
from typing import List, Dict, Optional
import uuid
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2", tags=["campaigns"])


class CreateCampaignRequest(BaseModel):
    """Request to create a new campaign"""
    query: str  # "top 5 financial institutes with $1B+ revenue"
    auto_approve: bool = False  # Skip approval gates
    channels: List[str] = ["email", "linkedin", "call"]


class ApproveCampaignGateRequest(BaseModel):
    """Request to approve/reject a campaign gate"""
    campaign_id: str
    stage: str  # research, stakeholder_analysis, use_case_generation, etc.
    decision: str  # approve, modify, reject
    modifications: Optional[Dict] = None


class UpdateCampaignRequest(BaseModel):
    """Request to update campaign state"""
    campaign_id: str
    updates: Dict


# In-memory campaign store (replace with DB in production)
campaigns_store = {}


@router.post("/campaigns")
async def create_campaign(
    req: CreateCampaignRequest,
    background_tasks: BackgroundTasks
) -> Dict:
    """
    Create a new campaign and start orchestration.
    
    Returns campaign_id and stream URL for real-time updates.
    """
    
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query is required")
    
    campaign_id = str(uuid.uuid4())
    
    # Store campaign
    campaigns_store[campaign_id] = {
        "id": campaign_id,
        "query": req.query,
        "status": "initializing",
        "auto_approve": req.auto_approve,
        "channels": req.channels,
        "gates": {},
        "created_at": None
    }
    
    # Start orchestration in background
    # background_tasks.add_task(_orchestrate_campaign, campaign_id, req)
    
    logger.info(f"Campaign created: {campaign_id}")
    
    return {
        "campaign_id": campaign_id,
        "query": req.query,
        "status": "initializing",
        "stream_url": f"/api/v2/campaigns/{campaign_id}/stream",
        "details_url": f"/api/v2/campaigns/{campaign_id}"
    }


@router.get("/campaigns/{campaign_id}")
async def get_campaign(campaign_id: str) -> Dict:
    """Get campaign details and current state"""
    
    campaign = campaigns_store.get(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return campaign


@router.get("/campaigns/{campaign_id}/stream")
async def stream_campaign(campaign_id: str):
    """
    Stream campaign progress in real-time using Server-Sent Events.
    
    Returns:
    - Agent activity updates
    - Approval gate requests
    - Progress messages
    - Final results
    """
    
    campaign = campaigns_store.get(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Implementation would use FastAPI StreamingResponse with SSE
    # Placeholder for now
    return {
        "status": "streaming",
        "campaign_id": campaign_id
    }


@router.get("/campaigns/{campaign_id}/agents")
async def get_agent_logs(campaign_id: str) -> Dict:
    """Get detailed agent activity logs and reasoning"""
    
    campaign = campaigns_store.get(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return {
        "campaign_id": campaign_id,
        "agents": campaign.get("agent_logs", []),
        "total_agents": 6,
        "execution_summary": {
            "research": campaign.get("research_status"),
            "stakeholder_analysis": campaign.get("stakeholder_status"),
            "use_case_generation": campaign.get("usecase_status"),
            "proposal_generation": campaign.get("proposal_status"),
            "outreach_generation": campaign.get("outreach_status")
        }
    }


@router.post("/campaigns/{campaign_id}/gates/{stage}/approve")
async def approve_gate(
    campaign_id: str,
    stage: str,
    req: ApproveCampaignGateRequest
) -> Dict:
    """Approve a campaign stage gate"""
    
    campaign = campaigns_store.get(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign["gates"][stage] = {
        "decision": "approved",
        "timestamp": None
    }
    
    logger.info(f"Gate approved: {campaign_id} - {stage}")
    
    return {
        "status": "approved",
        "stage": stage,
        "campaign_id": campaign_id
    }


@router.post("/campaigns/{campaign_id}/gates/{stage}/reject")
async def reject_gate(
    campaign_id: str,
    stage: str
) -> Dict:
    """Reject a campaign stage gate"""
    
    campaign = campaigns_store.get(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    campaign["gates"][stage] = {
        "decision": "rejected",
        "timestamp": None
    }
    
    logger.info(f"Gate rejected: {campaign_id} - {stage}")
    
    return {
        "status": "rejected",
        "stage": stage,
        "campaign_id": campaign_id
    }


@router.get("/campaigns/{campaign_id}/companies")
async def get_companies(campaign_id: str) -> Dict:
    """Get researched companies for campaign"""
    
    campaign = campaigns_store.get(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return {
        "campaign_id": campaign_id,
        "companies": campaign.get("companies", []),
        "total": len(campaign.get("companies", []))
    }


@router.get("/campaigns/{campaign_id}/contacts")
async def get_contacts(
    campaign_id: str,
    company_id: Optional[str] = None
) -> Dict:
    """Get contacts for campaign, optionally filtered by company"""
    
    campaign = campaigns_store.get(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    contacts = campaign.get("contacts", [])
    
    if company_id:
        contacts = [c for c in contacts if c.get("company_id") == company_id]
    
    return {
        "campaign_id": campaign_id,
        "contacts": contacts,
        "total": len(contacts)
    }


@router.get("/campaigns/{campaign_id}/use-cases")
async def get_use_cases(campaign_id: str) -> Dict:
    """Get generated use cases for campaign"""
    
    campaign = campaigns_store.get(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return {
        "campaign_id": campaign_id,
        "use_cases": campaign.get("use_cases", []),
        "total": len(campaign.get("use_cases", []))
    }


@router.get("/campaigns/{campaign_id}/proposals")
async def get_proposals(campaign_id: str) -> Dict:
    """Get generated proposals for campaign"""
    
    campaign = campaigns_store.get(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return {
        "campaign_id": campaign_id,
        "proposals": campaign.get("proposals", []),
        "total": len(campaign.get("proposals", []))
    }


@router.get("/campaigns/{campaign_id}/outreach")
async def get_outreach(campaign_id: str) -> Dict:
    """Get generated outreach content for campaign"""
    
    campaign = campaigns_store.get(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    return {
        "campaign_id": campaign_id,
        "outreach_content": campaign.get("outreach_content", []),
        "total": len(campaign.get("outreach_content", []))
    }


@router.post("/campaigns/{campaign_id}/update")
async def update_campaign(
    campaign_id: str,
    req: UpdateCampaignRequest
) -> Dict:
    """Update campaign state (e.g., select use cases, modify proposals)"""
    
    campaign = campaigns_store.get(campaign_id)
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    
    # Apply updates
    for key, value in req.updates.items():
        if key in campaign:
            campaign[key] = value
    
    logger.info(f"Campaign updated: {campaign_id}")
    
    return {
        "status": "updated",
        "campaign_id": campaign_id,
        "campaign": campaign
    }


@router.get("/campaigns")
async def list_campaigns(
    status: Optional[str] = None,
    limit: int = Query(10, ge=1, le=100)
) -> Dict:
    """List all campaigns, optionally filtered by status"""
    
    campaigns = list(campaigns_store.values())
    
    if status:
        campaigns = [c for c in campaigns if c.get("status") == status]
    
    campaigns = campaigns[-limit:]  # Most recent first
    
    return {
        "campaigns": campaigns,
        "total": len(campaigns),
        "limit": limit
    }
