"""
Use Case Generation Agent
Generates contextual use cases matching companies to services.
Analyzes company profiles and matches them with service offerings.
"""

import json
import re
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class UseCaseGenerationAgent:
    """
    Generates relevant use cases for target companies.
    
    Inputs:
    - companies: List[Dict] (with tech stack, pain points)
    - services_catalog: List[Dict] (our service offerings)
    - industry_trends: Dict (optional, current trends)
    
    Process:
    1. Analyze each company's industry, size, pain points, tech stack
    2. Research current trends in their sector
    3. Match our services to their challenges
    4. Generate 3-5 specific, contextualized use cases per company
    5. Rank by relevance and value potential
    
    Output:
    {
        "use_cases": [
            {
                "company_id": str,
                "title": str,
                "problem_statement": str,
                "proposed_solution": str,
                "expected_roi": str,
                "value_metrics": [str],
                "implementation_timeline": str,
                "relevant_industry_trends": [str],
                "competitive_advantage": str,
                "relevance_score": float (0-1),
                "confidence_score": float (0-1),
                "implementation_approach": str,
                "required_integrations": [str]
            }
        ],
        "reasoning": str,
        "total_generated": int
    }
    """
    
    def __init__(self, llm_provider):
        """
        Initialize Use Case Generation Agent
        
        Args:
            llm_provider: LLM for analysis and generation
        """
        self.llm_provider = llm_provider
        self.name = "UseCaseGenerationAgent"
        self.agent_type = "usecase"
        
        # Default service catalog - customize per your business
        self.services_catalog = [
            {
                "name": "AI Automation",
                "description": "Automate business processes with AI",
                "typical_benefits": ["cost reduction", "efficiency", "speed"]
            },
            {
                "name": "Data Analytics",
                "description": "Extract insights from business data",
                "typical_benefits": ["decision making", "forecasting", "optimization"]
            },
            {
                "name": "Cloud Migration",
                "description": "Move infrastructure to cloud",
                "typical_benefits": ["scalability", "cost savings", "reliability"]
            },
            {
                "name": "Cybersecurity",
                "description": "Secure digital assets",
                "typical_benefits": ["risk reduction", "compliance", "protection"]
            },
            {
                "name": "Workflow Integration",
                "description": "Connect disparate systems",
                "typical_benefits": ["efficiency", "data flow", "visibility"]
            }
        ]
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate use cases for companies
        
        Args:
            task: {
                "companies": List[Dict],
                "services_catalog": List[Dict] (optional),
                "use_cases_per_company": int (default 3),
                "industry_trends": Dict (optional)
            }
        
        Returns:
            List of generated use cases with rankings
        """
        companies = task.get("companies", [])
        services = task.get("services_catalog", self.services_catalog)
        use_cases_per_company = task.get("use_cases_per_company", 3)
        
        if not companies:
            return {
                "status": "error",
                "error": "Companies list is required",
                "use_cases": []
            }
        
        try:
            all_use_cases = []
            
            for company in companies:
                company_use_cases = await self._generate_for_company(
                    company,
                    services,
                    use_cases_per_company
                )
                all_use_cases.extend(company_use_cases)
            
            # Rank all use cases
            all_use_cases = self._rank_use_cases(all_use_cases)
            
            reasoning = f"Generated {len(all_use_cases)} use cases from {len(companies)} companies"
            
            return {
                "status": "success",
                "use_cases": all_use_cases,
                "reasoning": reasoning,
                "total_generated": len(all_use_cases),
                "confidence": self._calculate_confidence(all_use_cases)
            }
        
        except Exception as e:
            logger.error(f"Use case agent error: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "use_cases": []
            }
    
    async def _generate_for_company(
        self,
        company: Dict,
        services: List[Dict],
        limit: int
    ) -> List[Dict]:
        """Generate use cases for a specific company"""
        
        # Build company profile
        company_profile = {
            "name": company.get("name", ""),
            "industry": company.get("industry", ""),
            "size": company.get("employees", ""),
            "revenue": company.get("revenue", ""),
            "tech_stack": company.get("tech_stack", []),
            "pain_points": company.get("pain_points", []),
            "recent_news": company.get("recent_news", [])
        }
        
        # Generate use cases using LLM
        prompt = self._build_generation_prompt(company_profile, services, limit)
        
        try:
            response = await self.llm_provider.generate(prompt)
            use_cases = self._parse_use_cases(response, company)
            return use_cases[:limit]
        except Exception as e:
            logger.error(f"Error generating use cases for {company.get('name')}: {str(e)}")
            return []
    
    def _build_generation_prompt(
        self,
        company_profile: Dict,
        services: List[Dict],
        limit: int
    ) -> str:
        """Build prompt for LLM to generate use cases"""
        
        services_str = "\n".join([
            f"- {s['name']}: {s['description']}"
            for s in services
        ])
        
        prompt = f"""Given this company profile, generate {limit} specific, actionable use cases 
that match our services to their business needs:

COMPANY PROFILE:
- Name: {company_profile.get('name')}
- Industry: {company_profile.get('industry')}
- Size: {company_profile.get('size')} employees
- Revenue: {company_profile.get('revenue')}
- Tech Stack: {', '.join(company_profile.get('tech_stack', []))}
- Pain Points: {', '.join(company_profile.get('pain_points', []))}
- Recent News: {', '.join(company_profile.get('recent_news', []))}

OUR SERVICES:
{services_str}

For each use case, generate JSON with these fields:
{{
    "title": "Clear, benefit-focused title",
    "problem_statement": "Their specific problem based on profile",
    "proposed_solution": "How our service solves it",
    "expected_roi": "e.g., '25% cost reduction, 3 month payback'",
    "value_metrics": ["metric1", "metric2"],
    "implementation_timeline": "e.g., '4-6 weeks'",
    "competitive_advantage": "Why this matters to them specifically",
    "required_integrations": ["system1", "system2"]
}}

Return ONLY a JSON array of {limit} use cases, no other text."""
        
        return prompt
    
    def _parse_use_cases(self, response: str, company: Dict) -> List[Dict]:
        """Parse use cases from LLM response"""
        use_cases = []
        
        try:
            # Extract JSON array from response
            match = re.search(r'\[.*\]', response, re.DOTALL)
            if match:
                data = json.loads(match.group())
                
                for item in data:
                    use_case = {
                        "company_id": company.get("id", ""),
                        "company_name": company.get("name", ""),
                        **item
                    }
                    use_case["relevance_score"] = 0.8
                    use_case["confidence_score"] = 0.7
                    use_cases.append(use_case)
        except Exception as e:
            logger.debug(f"Error parsing use cases: {str(e)}")
        
        return use_cases
    
    def _rank_use_cases(self, use_cases: List[Dict]) -> List[Dict]:
        """Rank use cases by relevance and potential value"""
        
        for use_case in use_cases:
            # Score based on various factors
            score = 0.5
            
            # Clear problem statement
            if use_case.get("problem_statement"):
                score += 0.15
            
            # Specific ROI numbers
            roi_text = use_case.get("expected_roi", "").lower()
            if any(char.isdigit() for char in roi_text):
                score += 0.2
            
            # Implementation timeline is reasonable (not too long)
            timeline = use_case.get("implementation_timeline", "")
            if timeline and any(
                period in timeline.lower()
                for period in ["week", "month", "quarter"]
            ):
                score += 0.1
            
            # Competitive advantage defined
            if use_case.get("competitive_advantage"):
                score += 0.05
            
            use_case["relevance_score"] = min(score, 1.0)
            use_case["confidence_score"] = use_case.get("confidence_score", 0.7)
        
        # Sort by relevance
        use_cases.sort(
            key=lambda uc: uc.get("relevance_score", 0),
            reverse=True
        )
        
        return use_cases
    
    def _calculate_confidence(self, use_cases: List[Dict]) -> float:
        """Calculate overall confidence"""
        if not use_cases:
            return 0.0
        
        avg_confidence = sum(uc.get("confidence_score", 0.7) for uc in use_cases) / len(use_cases)
        return avg_confidence
