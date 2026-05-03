"""
Outreach Content Agent
Generates personalized outreach content across multiple channels.
Creates email sequences, LinkedIn messages, and call scripts.
"""

import json
import re
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class OutreachContentAgent:
    """
    Generates multi-channel outreach content.
    
    Inputs:
    - contacts: List[Dict]
    - proposals: List[Dict]
    - use_cases: List[Dict]
    - company_context: Dict
    
    Process:
    1. For each contact, analyze profile (seniority, interests, recent activity)
    2. Generate personalized content for:
       - Email sequence (initial + 2 follow-ups)
       - LinkedIn connection message + inmail
       - Call script with objection handling
    3. Adapt tone based on seniority and role
    4. Include personalization hooks from recent activity
    5. A/B test variations
    
    Output:
    {
        "outreach_content": [
            {
                "contact_id": str,
                "contact_name": str,
                "company": str,
                "content": {
                    "email": {
                        "initial": {"subject": str, "body": str},
                        "followup_1": {"subject": str, "body": str, "days_after": int},
                        "followup_2": {"subject": str, "body": str, "days_after": int}
                    },
                    "linkedin": {
                        "connection_message": str,
                        "inmail_subject": str,
                        "inmail_body": str
                    },
                    "call": {
                        "opening": str,
                        "value_prop": str,
                        "objection_handling": {objection: response},
                        "closing": str
                    }
                },
                "personalization_hooks": [str],
                "tone": str
            }
        ],
        "reasoning": str,
        "total_content_pieces": int
    }
    """
    
    def __init__(self, llm_provider):
        """
        Initialize Outreach Content Agent
        
        Args:
            llm_provider: LLM for content generation
        """
        self.llm_provider = llm_provider
        self.name = "OutreachContentAgent"
        self.agent_type = "outreach"
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate outreach content
        
        Args:
            task: {
                "contacts": List[Dict],
                "proposals": List[Dict],
                "use_cases": List[Dict],
                "company_context": Dict,
                "channels": List[str] (default: ["email", "linkedin", "call"])
            }
        
        Returns:
            Multi-channel outreach content ready to send
        """
        contacts = task.get("contacts", [])
        proposals = task.get("proposals", [])
        use_cases = task.get("use_cases", [])
        company_context = task.get("company_context", {})
        channels = task.get("channels", ["email", "linkedin", "call"])
        
        if not contacts:
            return {
                "status": "error",
                "error": "Contacts are required",
                "outreach_content": []
            }
        
        try:
            outreach_content = []
            
            for contact in contacts:
                # Find best proposal/use case for this contact
                best_proposal = self._select_best_proposal(contact, proposals, use_cases)
                
                # Generate content for each channel
                content = {}
                for channel in channels:
                    if channel == "email":
                        content["email"] = await self._generate_email_sequence(
                            contact, best_proposal, company_context
                        )
                    elif channel == "linkedin":
                        content["linkedin"] = await self._generate_linkedin_content(
                            contact, best_proposal, company_context
                        )
                    elif channel == "call":
                        content["call"] = await self._generate_call_script(
                            contact, best_proposal, company_context
                        )
                
                # Get personalization hooks
                personalization = self._extract_personalization_hooks(contact)
                
                # Determine tone
                tone = self._determine_tone(contact)
                
                outreach_item = {
                    "contact_id": contact.get("id", ""),
                    "contact_name": contact.get("name", ""),
                    "company": contact.get("company", ""),
                    "content": content,
                    "personalization_hooks": personalization,
                    "tone": tone,
                    "confidence_score": 0.75
                }
                
                outreach_content.append(outreach_item)
            
            reasoning = f"Generated multi-channel content for {len(outreach_content)} contacts"
            
            return {
                "status": "success",
                "outreach_content": outreach_content,
                "reasoning": reasoning,
                "total_content_pieces": len(outreach_content),
                "confidence": 0.75
            }
        
        except Exception as e:
            logger.error(f"Outreach agent error: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "outreach_content": []
            }
    
    def _select_best_proposal(
        self,
        contact: Dict,
        proposals: List[Dict],
        use_cases: List[Dict]
    ) -> Dict:
        """Select most relevant proposal for contact"""
        
        # For now, return first proposal
        # In production, could score based on contact role and company
        if proposals:
            return proposals[0]
        
        return {
            "title": "Our Solution",
            "summary": "We help businesses solve key challenges"
        }
    
    def _extract_personalization_hooks(self, contact: Dict) -> List[str]:
        """Extract personalization hooks from contact profile"""
        hooks = []
        
        if contact.get("recent_posts"):
            hooks.append(f"Saw your recent post on {contact['recent_posts'][0] if contact['recent_posts'] else 'your updates'}")
        
        if contact.get("interests"):
            hooks.append(f"We specialize in {', '.join(contact['interests'][:2])}")
        
        if contact.get("company"):
            hooks.append(f"Working with {contact.get('company')} on similar challenges")
        
        return hooks
    
    def _determine_tone(self, contact: Dict) -> str:
        """Determine appropriate communication tone for contact"""
        seniority = contact.get("seniority_level", "")
        
        if seniority == "C-suite":
            return "formal, executive-focused, results-oriented"
        elif seniority == "VP":
            return "professional, strategic, outcomes-focused"
        elif seniority == "Director":
            return "collaborative, detailed, solution-oriented"
        else:
            return "friendly, clear, straightforward"
    
    async def _generate_email_sequence(
        self,
        contact: Dict,
        proposal: Dict,
        company_context: Dict
    ) -> Dict:
        """Generate email sequence (initial + follow-ups)"""
        
        tone = self._determine_tone(contact)
        
        # Generate initial email
        initial_prompt = f"""Generate a professional, personalized cold email.

To: {contact.get('name')} ({contact.get('title')})
Company: {contact.get('company')}

Tone: {tone}

Our service: {proposal.get('title', 'Our Solution')}
Summary: {proposal.get('summary', '')}

Create an email with:
- Subject line (compelling, specific)
- Personalized opening (reference their company or role)
- Problem they face (based on their industry)
- How we solve it (specific to them)
- Social proof or relevant example
- Clear CTA (meeting request)

Make it conversational but professional, 150-200 words.

Return JSON:
{{"subject": "...", "body": "..."}}"""
        
        initial_response = await self.llm_provider.generate(initial_prompt)
        
        try:
            initial_email = json.loads(
                re.search(r'\{.*\}', initial_response, re.DOTALL).group()
            )
        except:
            initial_email = {
                "subject": f"Partnership opportunity for {contact.get('company')}",
                "body": "Hi " + contact.get('name', 'there') + ",\n\nWould love to connect."
            }
        
        # Generate follow-up 1 (3 days later)
        followup1_prompt = f"""Generate a follow-up email (3 days after initial).

Original context:
- To: {contact.get('name')}
- Original subject: {initial_email.get('subject')}

Make this a light, friendly follow-up that:
- References the original email
- Adds new value/insight
- Keeps it short (100-150 words)
- Maintains same tone: {tone}

Return JSON:
{{"subject": "...", "body": "..."}}"""
        
        followup1_response = await self.llm_provider.generate(followup1_prompt)
        
        try:
            followup1_email = json.loads(
                re.search(r'\{.*\}', followup1_response, re.DOTALL).group()
            )
        except:
            followup1_email = {
                "subject": f"Re: {initial_email.get('subject')}",
                "body": "Just checking in..."
            }
        
        # Generate follow-up 2 (5 days later)
        followup2_email = {
            "subject": f"Quick question for {contact.get('name')}",
            "body": f"Hi {contact.get('name')},\n\nOne last thing I wanted to share..."
        }
        
        return {
            "initial": initial_email,
            "followup_1": {**followup1_email, "days_after": 3},
            "followup_2": {**followup2_email, "days_after": 5}
        }
    
    async def _generate_linkedin_content(
        self,
        contact: Dict,
        proposal: Dict,
        company_context: Dict
    ) -> Dict:
        """Generate LinkedIn connection message and inmail"""
        
        tone = self._determine_tone(contact)
        
        prompt = f"""Generate LinkedIn outreach content.

Contact: {contact.get('name')} ({contact.get('title')})
Company: {contact.get('company')}

Tone: {tone}

Our service: {proposal.get('title')}

Create:
1. Connection message (short, 150 chars max)
2. Inmail subject (compelling, 50 chars max)
3. Inmail body (conversational, 300-400 words)

Return JSON:
{{
  "connection_message": "...",
  "inmail_subject": "...",
  "inmail_body": "..."
}}"""
        
        response = await self.llm_provider.generate(prompt)
        
        try:
            linkedin_content = json.loads(
                re.search(r'\{.*\}', response, re.DOTALL).group()
            )
        except:
            linkedin_content = {
                "connection_message": f"Hi {contact.get('name')}, would love to connect",
                "inmail_subject": "Partnership opportunity",
                "inmail_body": "Hi there, I think we could help you with..."
            }
        
        return linkedin_content
    
    async def _generate_call_script(
        self,
        contact: Dict,
        proposal: Dict,
        company_context: Dict
    ) -> Dict:
        """Generate call script with objection handling"""
        
        tone = self._determine_tone(contact)
        
        prompt = f"""Generate a phone call script.

Caller: Sales Representative
Contact: {contact.get('name')} ({contact.get('title')})
Company: {contact.get('company')}

Tone: {tone}

Our service: {proposal.get('title')}
Goal: Schedule a 15-minute discovery call

Create a script with:
1. Opening (friendly, specific)
2. Value proposition (their benefit)
3. Objection handling for 3 common objections
4. Closing (clear next step)

Return JSON:
{{
  "opening": "...",
  "value_prop": "...",
  "objection_handling": {{
    "We're happy with current solution": "...",
    "Not interested right now": "...",
    "Need to talk to my team": "..."
  }},
  "closing": "..."
}}"""
        
        response = await self.llm_provider.generate(prompt)
        
        try:
            call_script = json.loads(
                re.search(r'\{.*\}', response, re.DOTALL).group()
            )
        except:
            call_script = {
                "opening": "Hi, how are you doing today?",
                "value_prop": "We help companies like yours...",
                "objection_handling": {
                    "We're happy with current solution": "I understand, many of our clients started the same way.",
                    "Not interested right now": "Perfect timing - that's why I'm calling.",
                    "Need to talk to my team": "Great idea, let's all get on a quick call."
                },
                "closing": "Does next Tuesday work for a quick call?"
            }
        
        return call_script
