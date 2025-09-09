from fastapi import FastAPI, APIRouter, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pathlib import Path
import os
import logging
from typing import List
import uuid

from models import (
    RecommendationRequest, 
    RecommendationResponse, 
    FeedbackRequest, 
    SaveSolutionRequest,
    UserInteraction
)
from ai_engine import AIRecommendationEngine
from database import database
from solutions_data import AI_SOLUTIONS_DATASET, search_solutions, get_solutions_by_names

# Setup
ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(title="AI Solution Finder API", version="1.0.0")

# Create API router with /api prefix
api_router = APIRouter(prefix="/api")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize AI engine
ai_engine = AIRecommendationEngine()

@app.on_event("startup")
async def startup_event():
    """Initialize database connection on startup"""
    await database.connect()
    logger.info("AI Solution Finder API started successfully")

@app.on_event("shutdown")
async def shutdown_event():
    """Close database connection on shutdown"""
    await database.close()
    logger.info("AI Solution Finder API shutdown complete")

# Routes
@api_router.get("/")
async def root():
    return {"message": "AI Solution Finder API is running!", "version": "1.0.0"}

@api_router.post("/recommend", response_model=List[RecommendationResponse])
async def get_recommendations(request: RecommendationRequest):
    """Get AI-powered recommendations for user's problem statement"""
    try:
        logger.info(f"Getting recommendations for: {request.problem_statement[:100]}...")
        
        # Get AI recommendations
        recommendations = await ai_engine.get_recommendations(
            problem_statement=request.problem_statement,
            solutions_dataset=AI_SOLUTIONS_DATASET,
            excluded_solutions=request.excluded_solutions,
            user_preferences=request.user_preferences
        )
        
        # Save user interaction
        session_id = str(uuid.uuid4())
        interaction = UserInteraction(
            session_id=session_id,
            problem_statement=request.problem_statement,
            recommendations=[rec.dict() for rec in recommendations]
        )
        await database.save_user_interaction(interaction)
        
        logger.info(f"Generated {len(recommendations)} recommendations")
        return recommendations
        
    except Exception as e:
        logger.error(f"Error getting recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get recommendations")

@api_router.post("/feedback")
async def submit_feedback(request: FeedbackRequest):
    """Submit user feedback for a recommendation"""
    try:
        await database.save_feedback(
            session_id=request.session_id,
            solution_name=request.solution_name,
            feedback_type=request.feedback_type,
            rank=request.recommendation_rank,
            problem_statement=request.problem_statement
        )
        
        logger.info(f"Saved feedback: {request.feedback_type} for {request.solution_name}")
        return {"message": "Feedback saved successfully"}
        
    except Exception as e:
        logger.error(f"Error saving feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save feedback")

@api_router.post("/save-solution")
async def save_solution(request: SaveSolutionRequest):
    """Save a solution for the user"""
    try:
        await database.save_solution(
            session_id=request.session_id,
            solution_name=request.solution_name,
            problem_statement=request.problem_statement
        )
        
        logger.info(f"Saved solution: {request.solution_name} for session {request.session_id}")
        return {"message": "Solution saved successfully"}
        
    except Exception as e:
        logger.error(f"Error saving solution: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to save solution")

@api_router.get("/saved-solutions/{session_id}")
async def get_saved_solutions(session_id: str):
    """Get saved solutions for a user session"""
    try:
        saved_solution_names = await database.get_saved_solutions(session_id)
        saved_solutions = get_solutions_by_names(saved_solution_names)
        
        return {"saved_solutions": saved_solutions}
        
    except Exception as e:
        logger.error(f"Error getting saved solutions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get saved solutions")

@api_router.get("/solutions/search")
async def search_ai_solutions(q: str = "", category: str = "", limit: int = 20):
    """Search AI solutions by query and category"""
    try:
        if q:
            solutions = search_solutions(q, limit)
        else:
            solutions = AI_SOLUTIONS_DATASET[:limit]
            
        if category:
            solutions = [sol for sol in solutions if category.lower() in sol['category'].lower()]
            
        return {"solutions": solutions, "total": len(solutions)}
        
    except Exception as e:
        logger.error(f"Error searching solutions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to search solutions")

@api_router.get("/solutions/popular")
async def get_popular_solutions(limit: int = 10):
    """Get most popular solutions based on user interactions"""
    try:
        popular_solutions = await database.get_popular_solutions(limit)
        return {"popular_solutions": popular_solutions}
        
    except Exception as e:
        logger.error(f"Error getting popular solutions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get popular solutions")

@api_router.get("/analytics/summary")
async def get_analytics_summary():
    """Get analytics summary"""
    try:
        total_solutions = len(AI_SOLUTIONS_DATASET)
        popular_solutions = await database.get_popular_solutions(5)
        
        return {
            "total_solutions": total_solutions,
            "top_solutions": popular_solutions,
            "categories": list(set([sol['category'] for sol in AI_SOLUTIONS_DATASET]))
        }
        
    except Exception as e:
        logger.error(f"Error getting analytics: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get analytics")

# Include the API router
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)