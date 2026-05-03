"""
Campaign Manager Agent (Orchestrator)
Central orchestrator managing the entire campaign workflow.
Routes tasks to agents and handles human-in-the-loop approval gates.
"""

import json
import logging
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class GateDecision(str, Enum):
    APPROVE = "approve"
    MODIFY = "modify"
    REJECT = "reject"


class CampaignManagerAgent:
    """
    Orchestrates the entire campaign workflow.
    
    Orchestration Flow:
    1. User provides campaign query
    2. Research Agent → finds companies (with approval gate)
    3. Stakeholder Agent → finds contacts
    4. Use Case Agent → generates use cases (with selection gate)
    5. Proposal Agent → generates proposals
    6. Outreach Agent → generates content (with review gate)
    7. Returns ready-to-execute campaign
    
    Includes human-in-the-loop gates at critical points.
    """
    
    def __init__(
        self,
        research_agent,
        stakeholder_agent,
        usecase_agent,
        proposal_agent,
        outreach_agent,
        db_service=None,
        approval_callback: Optional[Callable] = None
    ):
        """
        Initialize Campaign Manager
        
        Args:
            research_agent: Research agent instance
            stakeholder_agent: Stakeholder intelligence agent
            usecase_agent: Use case generation agent
            proposal_agent: Proposal generation agent
            outreach_agent: Outreach content agent
            db_service: Database service for persistence
            approval_callback: Callback for approval gates
        """
        self.research_agent = research_agent
        self.stakeholder_agent = stakeholder_agent
        self.usecase_agent = usecase_agent
        self.proposal_agent = proposal_agent
        self.outreach_agent = outreach_agent
        self.db_service = db_service
        self.approval_callback = approval_callback
        
        self.name = "CampaignManagerAgent"
        self.agent_type = "manager"
        
        # State for current campaign
        self.campaign_state = None
        self.agent_logs = []
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute full campaign orchestration
        
        Args:
            task: {
                "campaign_id": str,
                "query": str,
                "auto_approve": bool (default: False),
                "require_approval_at": List[str] (stages to require approval)
            }
        
        Returns:
            Complete campaign with all generated content
        """
        campaign_id = task.get("campaign_id", "")
        query = task.get("query", "")
        auto_approve = task.get("auto_approve", False)
        approval_stages = task.get("require_approval_at", [
            "research", "use_cases", "outreach"
        ])
        
        if not query:
            return {
                "status": "error",
                "error": "Query is required",
                "campaign_id": campaign_id
            }
        
        try:
            # Initialize campaign state
            self.campaign_state = {
                "id": campaign_id,
                "query": query,
                "status": "initializing",
                "created_at": datetime.utcnow(),
                "companies": [],
                "contacts": [],
                "use_cases": [],
                "proposals": [],
                "outreach_content": [],
                "gates": {}
            }
            
            # Step 1: Research
            logger.info(f"Starting research for campaign: {campaign_id}")
            await self._execute_stage(
                "research",
                self._research_stage,
                auto_approve,
                approval_stages
            )
            
            if not self.campaign_state.get("companies"):
                raise Exception("No companies found")
            
            # Step 2: Stakeholder Intelligence
            logger.info("Finding stakeholders...")
            await self._execute_stage(
                "stakeholder_analysis",
                self._stakeholder_stage,
                auto_approve,
                approval_stages
            )
            
            # Step 3: Use Case Generation
            logger.info("Generating use cases...")
            await self._execute_stage(
                "use_case_generation",
                self._usecase_stage,
                auto_approve,
                approval_stages
            )
            
            # Step 4: Proposal Generation
            logger.info("Generating proposals...")
            await self._execute_stage(
                "proposal_generation",
                self._proposal_stage,
                auto_approve,
                approval_stages
            )
            
            # Step 5: Outreach Content
            logger.info("Generating outreach content...")
            await self._execute_stage(
                "outreach",
                self._outreach_stage,
                auto_approve,
                approval_stages
            )
            
            self.campaign_state["status"] = "completed"
            
            # Log agent activity
            self._log_campaign_completion()
            
            return {
                "status": "success",
                "campaign_id": campaign_id,
                "campaign_state": self.campaign_state,
                "agent_logs": self.agent_logs,
                "message": "Campaign orchestration complete"
            }
        
        except Exception as e:
            logger.error(f"Campaign orchestration error: {str(e)}")
            self.campaign_state["status"] = "failed"
            self.campaign_state["error"] = str(e)
            
            return {
                "status": "error",
                "error": str(e),
                "campaign_id": campaign_id,
                "campaign_state": self.campaign_state,
                "agent_logs": self.agent_logs
            }
    
    async def _execute_stage(
        self,
        stage_name: str,
        stage_function: Callable,
        auto_approve: bool,
        approval_stages: List[str]
    ) -> bool:
        """Execute a stage with optional approval gate"""
        
        try:
            # Execute stage
            await stage_function()
            
            # Check if approval needed
            needs_approval = stage_name in approval_stages and not auto_approve
            
            if needs_approval:
                # Call approval callback
                if self.approval_callback:
                    decision = await self.approval_callback({
                        "stage": stage_name,
                        "campaign_id": self.campaign_state["id"],
                        "state": self.campaign_state
                    })
                    
                    self.campaign_state["gates"][stage_name] = decision
                    
                    if decision == GateDecision.REJECT:
                        raise Exception(f"Stage {stage_name} rejected by user")
                    elif decision == GateDecision.MODIFY:
                        logger.info(f"Stage {stage_name} requires modification")
                        # In real app, would ask user for modifications
            
            self.campaign_state["status"] = f"completed_{stage_name}"
            return True
        
        except Exception as e:
            logger.error(f"Error in stage {stage_name}: {str(e)}")
            raise
    
    async def _research_stage(self):
        """Execute research stage"""
        result = await self.research_agent.execute({
            "query": self.campaign_state["query"],
            "max_companies": 5
        })
        
        if result.get("status") == "success":
            self.campaign_state["companies"] = result.get("companies", [])
            self._log_agent_action("research", result)
        else:
            raise Exception(f"Research failed: {result.get('error')}")
    
    async def _stakeholder_stage(self):
        """Execute stakeholder intelligence stage"""
        result = await self.stakeholder_agent.execute({
            "companies": self.campaign_state["companies"],
            "max_contacts_per_company": 5
        })
        
        if result.get("status") == "success":
            self.campaign_state["contacts"] = result.get("contacts", [])
            self._log_agent_action("stakeholder", result)
        else:
            raise Exception(f"Stakeholder analysis failed: {result.get('error')}")
    
    async def _usecase_stage(self):
        """Execute use case generation stage"""
        result = await self.usecase_agent.execute({
            "companies": self.campaign_state["companies"],
            "use_cases_per_company": 3
        })
        
        if result.get("status") == "success":
            self.campaign_state["use_cases"] = result.get("use_cases", [])
            self._log_agent_action("usecase", result)
        else:
            raise Exception(f"Use case generation failed: {result.get('error')}")
    
    async def _proposal_stage(self):
        """Execute proposal generation stage"""
        result = await self.proposal_agent.execute({
            "use_cases": self.campaign_state["use_cases"],
            "company_context": self.campaign_state["companies"][0] if self.campaign_state["companies"] else {},
            "contact_profiles": self.campaign_state["contacts"]
        })
        
        if result.get("status") == "success":
            self.campaign_state["proposals"] = result.get("proposals", [])
            self._log_agent_action("proposal", result)
        else:
            raise Exception(f"Proposal generation failed: {result.get('error')}")
    
    async def _outreach_stage(self):
        """Execute outreach content generation stage"""
        result = await self.outreach_agent.execute({
            "contacts": self.campaign_state["contacts"],
            "proposals": self.campaign_state["proposals"],
            "use_cases": self.campaign_state["use_cases"],
            "company_context": self.campaign_state["companies"][0] if self.campaign_state["companies"] else {}
        })
        
        if result.get("status") == "success":
            self.campaign_state["outreach_content"] = result.get("outreach_content", [])
            self._log_agent_action("outreach", result)
        else:
            raise Exception(f"Outreach generation failed: {result.get('error')}")
    
    def _log_agent_action(self, agent_name: str, result: Dict):
        """Log agent activity"""
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "agent": agent_name,
            "status": result.get("status"),
            "reasoning": result.get("reasoning", ""),
            "confidence": result.get("confidence", 0),
            "output_count": result.get("total_found") or result.get("total_generated") or result.get("total_proposals") or 0
        }
        self.agent_logs.append(log_entry)
    
    def _log_campaign_completion(self):
        """Log campaign completion"""
        completion_log = {
            "timestamp": datetime.utcnow().isoformat(),
            "campaign_id": self.campaign_state["id"],
            "total_companies": len(self.campaign_state.get("companies", [])),
            "total_contacts": len(self.campaign_state.get("contacts", [])),
            "total_use_cases": len(self.campaign_state.get("use_cases", [])),
            "total_proposals": len(self.campaign_state.get("proposals", [])),
            "total_outreach_content": len(self.campaign_state.get("outreach_content", []))
        }
        self.agent_logs.append(completion_log)
    
    async def update_campaign_state(
        self,
        campaign_id: str,
        updates: Dict
    ) -> Dict:
        """Allow user to modify campaign state"""
        
        if campaign_id != self.campaign_state.get("id"):
            return {"status": "error", "error": "Campaign ID mismatch"}
        
        # Update specific fields
        for key, value in updates.items():
            if key in self.campaign_state:
                self.campaign_state[key] = value
        
        return {
            "status": "success",
            "campaign_state": self.campaign_state
        }
    
    async def get_agent_reasoning(self, agent_name: str) -> Dict:
        """Retrieve reasoning trails for a specific agent"""
        
        logs = [
            log for log in self.agent_logs
            if log.get("agent") == agent_name
        ]
        
        return {
            "agent": agent_name,
            "logs": logs,
            "decision_summary": self._summarize_decisions(logs)
        }
    
    def _summarize_decisions(self, logs: List[Dict]) -> str:
        """Summarize agent decisions"""
        if not logs:
            return "No activity"
        
        items = sum(log.get("output_count", 0) for log in logs)
        avg_confidence = sum(log.get("confidence", 0) for log in logs) / len(logs) if logs else 0
        
        return f"Generated {items} items with {avg_confidence:.1%} average confidence"
