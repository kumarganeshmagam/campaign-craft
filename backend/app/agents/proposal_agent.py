"""
Proposal Generation Agent
Generates customized proposal variants for use cases.
Creates executive, technical, and ROI-focused versions.
"""

import json
import re
from typing import Dict, List, Any, Optional
import logging

logger = logging.getLogger(__name__)


class ProposalGenerationAgent:
    """
    Generates proposal variants for use cases.
    
    Inputs:
    - use_cases: List[Dict]
    - company_context: Dict (company info, contacts)
    - contact_profiles: List[Dict] (target contacts)
    
    Process:
    1. For each use case, create 3 proposal variants:
       - Executive Summary (1 page, high-level, for C-suite)
       - Technical Deep-Dive (detailed specs, for tech buyers)
       - ROI-Focused (metrics-heavy, for financial decision-makers)
    2. Personalize based on contact seniority and role
    3. Include case studies and proof points
    4. Structure with problem, solution, deliverables, timeline, pricing
    
    Output:
    {
        "proposals": [
            {
                "use_case_id": str,
                "company_id": str,
                "variants": [
                    {
                        "variant_type": "executive|technical|roi_focused",
                        "title": str,
                        "executive_summary": str,
                        "detailed_content": str,
                        "deliverables": [str],
                        "pricing_tiers": [{"tier": str, "price": str, "description": str}],
                        "case_studies": [str],
                        "target_audience": str
                    }
                ],
                "confidence_score": float (0-1)
            }
        ],
        "reasoning": str,
        "total_proposals": int
    }
    """
    
    def __init__(self, llm_provider):
        """
        Initialize Proposal Generation Agent
        
        Args:
            llm_provider: LLM for proposal generation
        """
        self.llm_provider = llm_provider
        self.name = "ProposalGenerationAgent"
        self.agent_type = "proposal"
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate proposals for use cases
        
        Args:
            task: {
                "use_cases": List[Dict],
                "company_context": Dict,
                "contact_profiles": List[Dict] (optional),
                "variants": List[str] (default: ["executive", "technical", "roi_focused"])
            }
        
        Returns:
            Proposals with multiple variants
        """
        use_cases = task.get("use_cases", [])
        company_context = task.get("company_context", {})
        contact_profiles = task.get("contact_profiles", [])
        variant_types = task.get("variants", ["executive", "technical", "roi_focused"])
        
        if not use_cases:
            return {
                "status": "error",
                "error": "Use cases are required",
                "proposals": []
            }
        
        try:
            proposals = []
            
            for use_case in use_cases:
                # Generate variants for this use case
                for variant_type in variant_types:
                    variant = await self._generate_variant(
                        use_case,
                        company_context,
                        contact_profiles,
                        variant_type
                    )
                    proposals.append(variant)
            
            reasoning = f"Generated {len(proposals)} proposal variants from {len(use_cases)} use cases"
            
            return {
                "status": "success",
                "proposals": proposals,
                "reasoning": reasoning,
                "total_proposals": len(proposals),
                "confidence": 0.75
            }
        
        except Exception as e:
            logger.error(f"Proposal agent error: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "proposals": []
            }
    
    async def _generate_variant(
        self,
        use_case: Dict,
        company_context: Dict,
        contact_profiles: List[Dict],
        variant_type: str
    ) -> Dict:
        """Generate a specific proposal variant"""
        
        # Build prompt based on variant type
        if variant_type == "executive":
            prompt = self._build_executive_prompt(use_case, company_context, contact_profiles)
        elif variant_type == "technical":
            prompt = self._build_technical_prompt(use_case, company_context)
        elif variant_type == "roi_focused":
            prompt = self._build_roi_prompt(use_case, company_context, contact_profiles)
        else:
            return {}
        
        try:
            content = await self.llm_provider.generate(prompt)
            
            variant = {
                "use_case_id": use_case.get("id", ""),
                "company_id": use_case.get("company_id", ""),
                "variant_type": variant_type,
                "title": use_case.get("title", ""),
                "executive_summary": self._extract_section(content, "Executive Summary"),
                "detailed_content": self._extract_section(content, "Detailed Content") or content[:1000],
                "deliverables": self._extract_list(content, "Deliverables"),
                "pricing_tiers": self._extract_pricing(content),
                "case_studies": self._extract_list(content, "Case Studies"),
                "target_audience": self._get_target_audience(variant_type),
                "confidence_score": 0.8
            }
            
            return variant
        
        except Exception as e:
            logger.error(f"Error generating {variant_type} variant: {str(e)}")
            return {}
    
    def _build_executive_prompt(
        self,
        use_case: Dict,
        company_context: Dict,
        contact_profiles: List[Dict]
    ) -> str:
        """Build prompt for executive proposal"""
        
        prompt = f"""Generate an executive summary proposal for a C-level executive.

USE CASE:
- Title: {use_case.get('title')}
- Problem: {use_case.get('problem_statement')}
- Solution: {use_case.get('proposed_solution')}
- Expected ROI: {use_case.get('expected_roi')}

COMPANY: {company_context.get('name')}

Create a 1-page executive summary with:
1. Executive Summary (3-4 sentences, high impact)
2. Key Benefits (3-4 bullet points)
3. Expected ROI (clear numbers)
4. Next Steps (clear call to action)

Format as clear, concise text suitable for C-level review."""
        
        return prompt
    
    def _build_technical_prompt(
        self,
        use_case: Dict,
        company_context: Dict
    ) -> str:
        """Build prompt for technical proposal"""
        
        prompt = f"""Generate a detailed technical proposal.

USE CASE:
- Title: {use_case.get('title')}
- Problem: {use_case.get('problem_statement')}
- Solution: {use_case.get('proposed_solution')}
- Required Integrations: {use_case.get('required_integrations', [])}

COMPANY: {company_context.get('name')}
Current Tech Stack: {company_context.get('tech_stack', [])}

Create a technical deep-dive with:
1. Detailed Content (technical approach, architecture)
2. Deliverables (specific deliverables)
3. Implementation Approach (step-by-step)
4. Integration Points (with their systems)
5. Timeline (phases with durations)

Be specific and technical."""
        
        return prompt
    
    def _build_roi_prompt(
        self,
        use_case: Dict,
        company_context: Dict,
        contact_profiles: List[Dict]
    ) -> str:
        """Build prompt for ROI-focused proposal"""
        
        prompt = f"""Generate an ROI-focused proposal for financial decision-makers.

USE CASE:
- Title: {use_case.get('title')}
- Expected ROI: {use_case.get('expected_roi')}
- Value Metrics: {use_case.get('value_metrics', [])}
- Implementation Timeline: {use_case.get('implementation_timeline')}

COMPANY: {company_context.get('name')}
Industry: {company_context.get('industry')}

Create a ROI-focused proposal with:
1. Executive Summary (problem, solution, impact)
2. Financial Impact (cost savings, revenue increase, efficiency gains with numbers)
3. Pricing Tiers (Basic, Professional, Enterprise with prices and features)
4. ROI Calculation (payback period, 3-year NPV)
5. Risk Mitigation (what could go wrong, how we prevent it)
6. Case Studies (similar company results)

Use specific numbers and industry benchmarks."""
        
        return prompt
    
    def _extract_section(self, content: str, section_name: str) -> str:
        """Extract a section from generated content"""
        try:
            pattern = f"{section_name}.*?(?=\\n\\n[A-Z]|$)"
            match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group().replace(section_name, "").strip()
        except:
            pass
        return ""
    
    def _extract_list(self, content: str, section_name: str) -> List[str]:
        """Extract a bulleted list from content"""
        items = []
        try:
            section = self._extract_section(content, section_name)
            # Extract bullet points
            bullets = re.findall(r'[-•]\s*(.+)', section)
            items = [b.strip() for b in bullets]
        except:
            pass
        return items
    
    def _extract_pricing(self, content: str) -> List[Dict]:
        """Extract pricing tiers from content"""
        pricing_tiers = []
        try:
            # Look for pricing tier patterns
            section = self._extract_section(content, "Pricing")
            
            # Simple extraction - look for tier names and prices
            tier_matches = re.findall(r'(\w+)\s*(?:Tier|Plan)?\s*:?\s*(?:\$[\d,]+|[\d,]+)', section)
            for tier in tier_matches:
                pricing_tiers.append({
                    "tier": tier[0] if isinstance(tier, tuple) else tier,
                    "description": "Custom pricing available"
                })
        except:
            pass
        
        # Return default if empty
        if not pricing_tiers:
            pricing_tiers = [
                {"tier": "Starter", "description": "For small implementations"},
                {"tier": "Professional", "description": "For enterprise deployments"},
                {"tier": "Enterprise", "description": "Custom solution"}
            ]
        
        return pricing_tiers
    
    def _get_target_audience(self, variant_type: str) -> str:
        """Get target audience for variant type"""
        if variant_type == "executive":
            return "C-level executives, board members"
        elif variant_type == "technical":
            return "CTO, VP Technology, engineering leads"
        elif variant_type == "roi_focused":
            return "CFO, finance directors, budget decision-makers"
        return "General audience"
