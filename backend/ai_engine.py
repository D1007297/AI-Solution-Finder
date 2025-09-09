import asyncio
import json
import logging
from typing import List, Dict, Optional
from dotenv import load_dotenv
import os
from emergentintegrations.llm.chat import LlmChat, UserMessage
from models import Solution, RecommendationResponse

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class AIRecommendationEngine:
    def __init__(self):
        self.api_key = os.getenv('EMERGENT_LLM_KEY')
        if not self.api_key:
            raise ValueError("EMERGENT_LLM_KEY not found in environment variables")
        
        self.system_message = """You are an expert AI Solution Finder that helps users discover the perfect AI tools for their specific needs.

Your task is to analyze user problem statements and recommend the most relevant AI solutions from the provided dataset.

Guidelines:
1. DEEP ANALYSIS: Understand the user's context, industry, skill level, and specific requirements
2. CONTEXTUAL MATCHING: Match problems to solutions based on actual capabilities, not just keywords
3. INTELLIGENT RANKING: Rank solutions by relevance, considering user preferences and constraints
4. CLEAR EXPLANATIONS: Provide specific reasons why each solution is recommended
5. HANDLE EXCLUSIONS: Respect user exclusions like "not ChatGPT" or "no paid tools"
6. CONSIDER PREFERENCES: Prioritize free tools if mentioned, enterprise solutions for business contexts

Response Format (JSON):
{
  "recommendations": [
    {
      "name": "Solution Name",
      "rank": 1,
      "confidence": 0.95,
      "explanation": "Specific reason why this solution fits the user's needs",
      "reasoning": "Detailed analysis of why this is the best match"
    }
  ]
}

Always return exactly 2-3 recommendations ranked by relevance."""

    async def get_recommendations(
        self, 
        problem_statement: str, 
        solutions_dataset: List[Dict],
        excluded_solutions: Optional[List[str]] = None,
        user_preferences: Optional[Dict] = None
    ) -> List[RecommendationResponse]:
        """Get AI recommendations for the given problem statement"""
        
        try:
            # Initialize chat with unique session ID
            session_id = f"recommendation_{hash(problem_statement) % 1000000}"
            
            chat = LlmChat(
                api_key=self.api_key,
                session_id=session_id,
                system_message=self.system_message
            ).with_model("openai", "gpt-4o-mini")

            # Create user message with context
            user_prompt = self._create_analysis_prompt(
                problem_statement, 
                solutions_dataset, 
                excluded_solutions,
                user_preferences
            )
            
            user_message = UserMessage(text=user_prompt)
            
            # Get AI response
            response = await chat.send_message(user_message)
            
            # Parse and validate response
            recommendations = self._parse_ai_response(response, solutions_dataset)
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error getting AI recommendations: {str(e)}")
            # Fallback to simple matching
            return self._fallback_recommendations(problem_statement, solutions_dataset)

    def _create_analysis_prompt(
        self, 
        problem_statement: str, 
        solutions_dataset: List[Dict],
        excluded_solutions: Optional[List[str]] = None,
        user_preferences: Optional[Dict] = None
    ) -> str:
        """Create detailed prompt for AI analysis"""
        
        # Filter out excluded solutions
        available_solutions = solutions_dataset
        if excluded_solutions:
            available_solutions = [
                sol for sol in solutions_dataset 
                if sol['name'] not in excluded_solutions
            ]
        
        # Create solutions summary for AI
        solutions_summary = []
        for sol in available_solutions[:50]:  # Limit to prevent token overflow
            solutions_summary.append(
                f"- {sol['name']} ({sol['category']}): {sol['description']}\n"
                f"  Use cases: {', '.join(sol['use_cases'])}\n"
                f"  Link: {sol['link']}"
            )
        
        prompt = f"""
PROBLEM STATEMENT:
"{problem_statement}"

USER PREFERENCES:
{json.dumps(user_preferences or {}, indent=2)}

EXCLUDED SOLUTIONS:
{excluded_solutions or "None"}

AVAILABLE AI SOLUTIONS:
{chr(10).join(solutions_summary)}

TASK:
Analyze the problem statement deeply and recommend the 2-3 most relevant AI solutions.
Consider:
1. User's specific needs and context
2. Solution capabilities and strengths
3. User skill level (beginner vs professional)
4. Budget preferences (free vs paid)
5. Use case alignment
6. Integration requirements

Provide detailed reasoning for each recommendation.
"""
        return prompt

    def _parse_ai_response(self, ai_response: str, solutions_dataset: List[Dict]) -> List[RecommendationResponse]:
        """Parse AI response and create structured recommendations"""
        
        try:
            # Try to parse JSON response
            if '{' in ai_response and '}' in ai_response:
                json_start = ai_response.find('{')
                json_end = ai_response.rfind('}') + 1
                json_str = ai_response[json_start:json_end]
                
                parsed_response = json.loads(json_str)
                recommendations_data = parsed_response.get('recommendations', [])
            else:
                # Fallback: extract solution names from text
                recommendations_data = self._extract_solutions_from_text(ai_response)
            
            recommendations = []
            solutions_dict = {sol['name']: sol for sol in solutions_dataset}
            
            for i, rec_data in enumerate(recommendations_data[:3]):
                solution_name = rec_data.get('name', '')
                
                # Find matching solution in dataset
                solution = solutions_dict.get(solution_name)
                if solution:
                    recommendation = RecommendationResponse(
                        name=solution['name'],
                        category=solution['category'],
                        description=solution['description'],
                        link=solution['link'],
                        use_cases=solution['use_cases'],
                        explanation=rec_data.get('explanation', f"{solution['name']} is recommended for this use case."),
                        rank=rec_data.get('rank', i + 1),
                        confidence=rec_data.get('confidence', 0.8),
                        reasoning=rec_data.get('reasoning', f"This solution aligns well with your requirements.")
                    )
                    recommendations.append(recommendation)
                    
            return recommendations
            
        except Exception as e:
            logger.error(f"Error parsing AI response: {str(e)}")
            return self._fallback_recommendations("", solutions_dataset)

    def _extract_solutions_from_text(self, text: str) -> List[Dict]:
        """Extract solution names from unstructured text response"""
        # This is a fallback method to extract solution names
        common_solutions = [
            "ChatGPT", "Google Gemini", "Claude Pro", "GitHub Copilot", 
            "MidJourney", "DALL-E 3", "AIaC", "Perplexity AI"
        ]
        
        found_solutions = []
        for solution in common_solutions:
            if solution in text:
                found_solutions.append({
                    'name': solution,
                    'explanation': f"{solution} was mentioned as a good fit for your needs.",
                    'rank': len(found_solutions) + 1,
                    'confidence': 0.7
                })
                if len(found_solutions) >= 3:
                    break
                    
        return found_solutions

    def _fallback_recommendations(self, problem_statement: str, solutions_dataset: List[Dict]) -> List[RecommendationResponse]:
        """Fallback method when AI fails"""
        
        # Simple keyword matching as fallback
        problem_lower = problem_statement.lower()
        
        recommendations = []
        
        # Default recommendations based on common patterns
        if any(word in problem_lower for word in ['infrastructure', 'terraform', 'cloudformation']):
            solutions = ['AIaC', 'GitHub Copilot', 'Amazon CodeWhisperer']
        elif any(word in problem_lower for word in ['code', 'programming', 'development']):
            solutions = ['GitHub Copilot', 'DeepSeek Coder', 'Cursor AI']
        elif any(word in problem_lower for word in ['image', 'art', 'visual']):
            solutions = ['MidJourney', 'DALL-E 3', 'Adobe Firefly']
        elif any(word in problem_lower for word in ['video', 'animation']):
            solutions = ['Runway ML Free', 'Leonardo AI Video', 'Synthesia']
        elif any(word in problem_lower for word in ['write', 'content', 'blog']):
            solutions = ['ChatGPT', 'Jasper AI', 'Claude Pro']
        else:
            solutions = ['ChatGPT', 'Google Gemini', 'Claude Pro']
        
        solutions_dict = {sol['name']: sol for sol in solutions_dataset}
        
        for i, solution_name in enumerate(solutions[:3]):
            solution = solutions_dict.get(solution_name)
            if solution:
                recommendation = RecommendationResponse(
                    name=solution['name'],
                    category=solution['category'],
                    description=solution['description'],
                    link=solution['link'],
                    use_cases=solution['use_cases'],
                    explanation=f"{solution['name']} is a reliable choice for your requirements.",
                    rank=i + 1,
                    confidence=0.6,
                    reasoning="This recommendation is based on keyword matching."
                )
                recommendations.append(recommendation)
        
        return recommendations