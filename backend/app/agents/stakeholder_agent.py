"""
Stakeholder Intelligence Agent
Finds decision-makers and key stakeholders within companies.
Identifies contact information, roles, engagement signals.
"""

import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class StakeholderIntelligenceAgent:
    """
    Finds decision-makers and stakeholders for target companies.
    
    Inputs:
    - companies: List[Dict] (from Research Agent)
    - service_type: str (optional, to find relevant roles)
    
    Process:
    1. For each company, search for C-suite, VPs, department heads
    2. Use LinkedIn, company pages, press releases to find contacts
    3. Extract: name, title, email, LinkedIn, recent activity
    4. Score by: seniority, relevance to service, accessibility
    5. Return prioritized contact list
    
    Output:
    {
        "contacts": [
            {
                "name": str,
                "title": str,
                "department": str,
                "company_id": str,
                "email": str,
                "linkedin_url": str,
                "twitter": str,
                "seniority_level": "C-suite|VP|Director|Manager|IC",
                "recent_posts": [str],
                "interests": [str],
                "engagement_signals": dict,
                "priority_score": float (0-1),
                "confidence_score": float (0-1),
                "sources": [url]
            }
        ],
        "reasoning": str,
        "total_found": int
    }
    """
    
    def __init__(self, llm_provider, search_tools, linkedin_tool=None):
        """
        Initialize Stakeholder Intelligence Agent
        
        Args:
            llm_provider: LLM for analysis
            search_tools: Web search tools
            linkedin_tool: Optional LinkedIn scraper
        """
        self.llm_provider = llm_provider
        self.search_tools = search_tools
        self.linkedin_tool = linkedin_tool
        self.name = "StakeholderIntelligenceAgent"
        self.agent_type = "stakeholder"
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Find stakeholders for companies
        
        Args:
            task: {
                "companies": List[Dict],
                "max_contacts_per_company": int (default 5),
                "service_type": str (optional)
            }
        
        Returns:
            Contact list with priority scores
        """
        companies = task.get("companies", [])
        max_contacts = task.get("max_contacts_per_company", 5)
        service_type = task.get("service_type", "enterprise software")
        
        if not companies:
            return {
                "status": "error",
                "error": "Companies list is required",
                "contacts": []
            }
        
        try:
            contacts = []
            
            for company in companies:
                company_contacts = await self._find_contacts(
                    company, 
                    max_contacts, 
                    service_type
                )
                contacts.extend(company_contacts)
            
            # Rank all contacts
            contacts = self._rank_contacts(contacts)
            
            reasoning = f"Found {len(contacts)} stakeholders from {len(companies)} companies"
            
            return {
                "status": "success",
                "contacts": contacts,
                "reasoning": reasoning,
                "total_found": len(contacts),
                "confidence": self._calculate_confidence(contacts)
            }
        
        except Exception as e:
            logger.error(f"Stakeholder agent error: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "contacts": []
            }
    
    async def _find_contacts(self, company: Dict, limit: int, service_type: str) -> List[Dict]:
        """Find contacts in a specific company"""
        contacts = []
        company_name = company.get("name", "")
        
        if not company_name:
            return contacts
        
        # Search queries for different roles
        search_queries = [
            f"{company_name} CEO founder",
            f"{company_name} CTO VP technology",
            f"{company_name} VP sales marketing",
            f"{company_name} director product",
            f"{company_name} VP operations"
        ]
        
        found_names = set()
        
        for query in search_queries:
            try:
                results = await self.search_tools.search(query, limit=3)
                
                for result in results:
                    # Try LinkedIn first if available
                    if "linkedin.com" in result.get("link", ""):
                        contact = await self._parse_linkedin_contact(
                            result, 
                            company
                        )
                    else:
                        contact = await self._parse_contact(result, company)
                    
                    if contact and contact.get("name") not in found_names:
                        contacts.append(contact)
                        found_names.add(contact.get("name"))
            
            except Exception as e:
                logger.debug(f"Error searching for {query}: {str(e)}")
                continue
        
        return contacts[:limit]
    
    async def _parse_linkedin_contact(self, result: Dict, company: Dict) -> Optional[Dict]:
        """Parse LinkedIn profile"""
        link = result.get("link", "")
        snippet = result.get("snippet", "")
        
        contact = {
            "name": self._extract_name(snippet),
            "linkedin_url": link,
            "sources": [link]
        }
        
        # Use LLM to extract info from snippet
        prompt = f"""Extract contact information from this LinkedIn snippet:
{snippet}

Extract:
- title (job title)
- department (sales, marketing, product, engineering, etc.)
- seniority_level (C-suite, VP, Director, Manager, IC)

Return as JSON."""
        
        try:
            response = await self.llm_provider.generate(prompt)
            match = re.search(r'\{.*\}', response, re.DOTALL)
            if match:
                data = json.loads(match.group())
                contact.update(data)
        except:
            pass
        
        return contact
    
    async def _parse_contact(self, result: Dict, company: Dict) -> Optional[Dict]:
        """Parse contact from search result"""
        title = result.get("title", "")
        snippet = result.get("snippet", "")
        link = result.get("link", "")
        
        contact = {
            "name": self._extract_name(title),
            "sources": [link]
        }
        
        # Extract job title from result
        if " - " in title:
            parts = title.split(" - ")
            contact["title"] = parts[1] if len(parts) > 1 else ""
        
        # Try to extract email
        email_match = re.search(r'[\w\.-]+@[\w\.-]+', snippet)
        if email_match:
            contact["email"] = email_match.group()
        
        return contact if contact.get("name") else None
    
    def _extract_name(self, text: str) -> str:
        """Extract name from text"""
        # Simple name extraction - first capitalized words
        words = text.split()[:3]
        name = " ".join(w for w in words if w[0].isupper())
        return name[:100] if name else ""
    
    def _determine_seniority(self, title: str) -> str:
        """Determine seniority level from title"""
        title_lower = title.lower()
        
        if any(word in title_lower for word in ["ceo", "cfo", "cto", "coo", "founder"]):
            return "C-suite"
        elif "vp" in title_lower or "vice president" in title_lower:
            return "VP"
        elif "director" in title_lower:
            return "Director"
        elif "manager" in title_lower or "lead" in title_lower:
            return "Manager"
        else:
            return "IC"
    
    async def _extract_engagement_signals(self, contact: Dict) -> Dict:
        """Extract engagement signals (interests, activity)"""
        signals = {
            "recent_posts_count": 0,
            "interests": [],
            "last_activity": None
        }
        
        # TODO: If LinkedIn tool available, get recent posts and interests
        
        return signals
    
    def _rank_contacts(self, contacts: List[Dict]) -> List[Dict]:
        """Rank contacts by priority for outreach"""
        for contact in contacts:
            priority = 0.5
            
            # Boost for seniority
            seniority = contact.get("seniority_level", "")
            if seniority == "C-suite":
                priority += 0.3
            elif seniority == "VP":
                priority += 0.2
            elif seniority == "Director":
                priority += 0.1
            
            # Boost for email availability
            if contact.get("email"):
                priority += 0.1
            
            # Boost for engagement signals
            signals = contact.get("engagement_signals", {})
            if signals.get("recent_posts_count", 0) > 0:
                priority += 0.05
            
            contact["priority_score"] = min(priority, 1.0)
            contact["confidence_score"] = contact.get("confidence_score", 0.6)
        
        # Sort by priority
        contacts.sort(
            key=lambda c: c.get("priority_score", 0),
            reverse=True
        )
        
        return contacts
    
    def _calculate_confidence(self, contacts: List[Dict]) -> float:
        """Calculate overall confidence"""
        if not contacts:
            return 0.0
        
        avg_confidence = sum(c.get("confidence_score", 0.5) for c in contacts) / len(contacts)
        return avg_confidence
