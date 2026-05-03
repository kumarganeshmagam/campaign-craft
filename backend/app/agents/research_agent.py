"""
Research & Discovery Agent
Autonomous agent that researches companies based on criteria.
Uses Gemini API for intelligent analysis and decision making.
"""

import json
import re
from typing import Dict, List, Any, Optional
from datetime import datetime
import asyncio
import logging
from app.controllers import ai_provider

logger = logging.getLogger(__name__)


class ResearchAgent:
    """
    Researches companies based on user query using Gemini API.
    
    Inputs:
    - query: str (e.g., "SaaS companies in fintech space with $10M+ revenue")
    
    Process:
    1. Use Gemini to parse query and identify criteria
    2. Generate research findings based on criteria
    3. Use Gemini to structure and analyze the data
    4. Return ranked company profiles with confidence scores
    
    Output:
    {
        "companies": [
            {
                "name": str,
                "industry": str,
                "revenue": str,
                "employees": int,
                "website": str,
                "description": str,
                "tech_stack": [str],
                "recent_news": [str],
                "pain_points": [str],
                "confidence_score": float (0-1),
                "sources": [url]
            }
        ],
        "reasoning": str,
        "search_criteria": dict,
        "total_researched": int
    }
    """
    
    def __init__(self):
        """Initialize Research Agent with Gemini API"""
        self.name = "ResearchAgent"
        self.agent_type = "research"
        self.ai_provider = ai_provider
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main execution function - research companies using Gemini API
        
        Args:
            task: {
                "query": str,
                "max_companies": int (default 5),
            }
        
        Returns:
            Structured company profiles with confidence scores from Gemini
        """
        query = task.get("query", "")
        max_companies = task.get("max_companies", 5)
        
        if not query:
            return {
                "status": "error",
                "error": "Query is required",
                "companies": []
            }
        
        try:
            logger.info(f"ResearchAgent: Starting research for query: {query}")
            
            # Step 1: Use Gemini to parse and understand the query
            criteria = await self._parse_criteria_with_gemini(query)
            logger.info(f"ResearchAgent: Parsed criteria: {criteria}")
            
            # Step 2: Use Gemini to generate company research based on query
            companies = await self._research_companies_with_gemini(query, criteria, max_companies)
            logger.info(f"ResearchAgent: Found {len(companies)} companies")
            
            # Step 3: Rank companies
            companies = self._rank_companies(companies, criteria)
            
            reasoning = f"Used Gemini API to research: '{query}'. Identified {len(companies)} companies matching criteria: {json.dumps(criteria)}"
            
            return {
                "status": "success",
                "companies": companies,
                "reasoning": reasoning,
                "search_criteria": criteria,
                "total_researched": len(companies),
                "confidence": self._calculate_confidence(companies),
                "source": "Gemini API"
            }
        
        except Exception as e:
            logger.error(f"ResearchAgent error: {str(e)}", exc_info=True)
            return {
                "status": "error",
                "error": str(e),
                "companies": []
            }
    
    async def _parse_criteria_with_gemini(self, query: str) -> Dict[str, Any]:
        """Parse query using Gemini API to extract search criteria"""
        prompt = f"""Parse this research query and extract structured search criteria. Return ONLY valid JSON.

Query: {query}

Extract and return as JSON with these fields:
- industries: list of relevant industries (strings)
- company_sizes: list of target company sizes (e.g., "startup", "SMB", "enterprise")
- revenue_range: revenue range if mentioned
- key_characteristics: important attributes (list of strings)
- geographic_focus: target regions or countries (list of strings)
- technology_focus: any specific technologies mentioned (list of strings)

Example output format:
{{"industries": ["SaaS", "FinTech"], "company_sizes": ["mid-market", "enterprise"], "revenue_range": "$10M-$100M", "key_characteristics": ["growing", "profitable"], "geographic_focus": ["US", "EU"], "technology_focus": ["AI", "Cloud"]}}

Parse the query and return only valid JSON."""
        
        try:
            response = await ai_provider.generate_text(
                prompt,
                temperature=0.3,
                max_tokens=500,
                json_mode=True
            )
            
            # Handle both dict and string responses
            if isinstance(response, dict):
                return response
            else:
                # Try to extract JSON from string
                match = re.search(r'\{.*\}', str(response), re.DOTALL)
                if match:
                    return json.loads(match.group())
        except Exception as e:
            logger.error(f"Error parsing criteria with Gemini: {str(e)}")
        
        # Fallback: simple parsing
        return {
            "industries": query.split(),
            "company_sizes": ["enterprise"],
            "key_characteristics": ["relevant"]
        }
    
    async def _research_companies_with_gemini(
        self,
        query: str,
        criteria: Dict[str, Any],
        max_companies: int
    ) -> List[Dict[str, Any]]:
        """Use Gemini API to research and generate company information"""
        
        prompt = f"""Research and identify {max_companies} companies based on this query and criteria.

Query: {query}

Criteria:
- Industries: {', '.join(criteria.get('industries', []))}
- Company Sizes: {', '.join(criteria.get('company_sizes', []))}
- Revenue Range: {criteria.get('revenue_range', 'Not specified')}
- Key Characteristics: {', '.join(criteria.get('key_characteristics', []))}
- Geographic Focus: {', '.join(criteria.get('geographic_focus', ['Global']))}

Generate {max_companies} realistic company profiles that match this criteria. Return ONLY valid JSON array.

For each company, provide:
- name: Company name
- industry: Primary industry
- revenue: Estimated annual revenue
- employees: Estimated number of employees
- description: Brief company description (1-2 sentences)
- website: Realistic domain name
- tech_stack: List of technologies likely used (infer from industry/type)
- pain_points: List of likely business challenges they face
- recent_news: List of recent developments or trends they'd care about
- confidence_score: Your confidence in this match (0.0 to 1.0)

Return as a valid JSON array like:
[
  {{"name": "Company A", "industry": "SaaS", "revenue": "$50M", "employees": 200, "description": "...", "website": "companya.com", "tech_stack": ["AWS", "Node.js"], "pain_points": ["Scaling", "Customer retention"], "recent_news": ["Raised Series B"], "confidence_score": 0.85}},
  ...
]

Return ONLY the JSON array, no other text."""
        
        try:
            response = await ai_provider.generate_text(
                prompt,
                temperature=0.7,
                max_tokens=3000,
                json_mode=True
            )
            
            # Parse response
            companies = []
            if isinstance(response, dict):
                # If it's a dict, wrap in list
                if "companies" in response:
                    companies = response["companies"]
                else:
                    companies = [response]
            elif isinstance(response, list):
                companies = response
            else:
                # Try to extract JSON array from string
                match = re.search(r'\[.*\]', str(response), re.DOTALL)
                if match:
                    companies = json.loads(match.group())
            
            # Ensure companies have required fields
            for company in companies:
                if "sources" not in company:
                    company["sources"] = ["Gemini Research"]
                if "tech_stack" not in company:
                    company["tech_stack"] = []
                if "pain_points" not in company:
                    company["pain_points"] = []
                if "recent_news" not in company:
                    company["recent_news"] = []
                if "confidence_score" not in company:
                    company["confidence_score"] = 0.7
            
            return companies[:max_companies]
        
        except Exception as e:
            logger.error(f"Error researching companies with Gemini: {str(e)}")
            return []
    
    def _rank_companies(self, companies: List[Dict], criteria: Dict) -> List[Dict]:
        """Rank companies by relevance to criteria"""
        for company in companies:
            score = company.get("confidence_score", 0.5)
            
            # Boost score based on criteria match
            if "industries" in criteria:
                if any(ind.lower() in company.get("industry", "").lower() 
                       for ind in criteria.get("industries", [])):
                    score *= 1.1  # Slight boost for industry match
            
            company["relevance_score"] = min(score, 1.0)
        
        # Sort by confidence descending
        companies.sort(
            key=lambda c: c.get("confidence_score", 0),
            reverse=True
        )
        
        return companies
    
    def _calculate_confidence(self, companies: List[Dict]) -> float:
        """Calculate overall confidence in research results"""
        if not companies:
            return 0.0
        
        avg_confidence = sum(c.get("confidence_score", 0) for c in companies) / len(companies)
        return round(avg_confidence, 2)


# Module-level run_agent function for agent_router compatibility
async def run_agent(input_data: Dict[str, Any], queue=None) -> Dict[str, Any]:
    """
    Run the research agent with the given input.
    
    Args:
        input_data: Dict with 'topic' key containing the research topic
        queue: Optional asyncio.Queue for progress updates
    
    Returns:
        Dict with campaign analysis and research findings
    """
    topic = input_data.get("topic", "")
    
    if queue:
        await queue.put({
            "type": "progress",
            "agent": "ResearchAgent",
            "message": f"Starting AI research on: {topic}"
        })
    
    try:
        agent = ResearchAgent()
        
        # Create research task for the topic - execute() expects "query" key
        task = {
            "query": f"Research and analyze opportunities in: {topic}",
            "max_companies": 5
        }
        
        if queue:
            await queue.put({
                "type": "progress",
                "agent": "ResearchAgent",
                "message": "Analyzing with Gemini AI..."
            })
        
        # Execute the research
        result = await agent.execute(task)
        
        if queue:
            await queue.put({
                "type": "progress",
                "agent": "ResearchAgent",
                "message": "Research complete!"
            })
        
        return result
        
    except Exception as e:
        logger.error(f"Error in research agent: {str(e)}")
        if queue:
            await queue.put({
                "type": "error",
                "agent": "ResearchAgent",
                "error": str(e)
            })
        return {
            "error": str(e),
            "companies": [],
            "reasoning": f"Failed to complete research: {str(e)}"
        }