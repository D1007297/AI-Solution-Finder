from motor.motor_asyncio import AsyncIOMotorClient
from typing import List, Dict, Optional
import os
from datetime import datetime
from models import UserInteraction, Analytics
import logging

logger = logging.getLogger(__name__)

class Database:
    def __init__(self):
        self.client = None
        self.db = None
        
    async def connect(self):
        """Connect to MongoDB"""
        mongo_url = os.environ['MONGO_URL']
        db_name = os.environ['DB_NAME']
        
        self.client = AsyncIOMotorClient(mongo_url)
        self.db = self.client[db_name]
        
        logger.info("Connected to MongoDB")
        
    async def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            
    async def save_user_interaction(self, interaction: UserInteraction) -> str:
        """Save user interaction to database"""
        try:
            result = await self.db.user_interactions.insert_one(interaction.dict())
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error saving user interaction: {str(e)}")
            return ""
            
    async def get_user_interactions(self, session_id: str) -> List[Dict]:
        """Get user interactions by session ID"""
        try:
            cursor = self.db.user_interactions.find({"session_id": session_id})
            interactions = await cursor.to_list(length=100)
            return interactions
        except Exception as e:
            logger.error(f"Error getting user interactions: {str(e)}")
            return []
            
    async def save_feedback(self, session_id: str, solution_name: str, feedback_type: str, rank: int, problem_statement: str):
        """Save user feedback"""
        try:
            # Update user interaction with feedback
            await self.db.user_interactions.update_one(
                {"session_id": session_id},
                {"$push": {
                    "feedback": {
                        "solution_name": solution_name,
                        "feedback_type": feedback_type,
                        "rank": rank,
                        "timestamp": datetime.utcnow()
                    }
                }},
                upsert=True
            )
            
            # Update analytics
            await self._update_analytics(solution_name, feedback_type, "feedback")
            
        except Exception as e:
            logger.error(f"Error saving feedback: {str(e)}")
            
    async def save_solution(self, session_id: str, solution_name: str, problem_statement: str):
        """Save solution for user"""
        try:
            await self.db.user_interactions.update_one(
                {"session_id": session_id},
                {"$addToSet": {"saved_solutions": solution_name}},
                upsert=True
            )
            
            # Update analytics
            await self._update_analytics(solution_name, None, "save")
            
        except Exception as e:
            logger.error(f"Error saving solution: {str(e)}")
            
    async def get_saved_solutions(self, session_id: str) -> List[str]:
        """Get saved solutions for user"""
        try:
            interaction = await self.db.user_interactions.find_one({"session_id": session_id})
            if interaction:
                return interaction.get("saved_solutions", [])
            return []
        except Exception as e:
            logger.error(f"Error getting saved solutions: {str(e)}")
            return []
            
    async def _update_analytics(self, solution_name: str, feedback_type: Optional[str], action_type: str):
        """Update analytics data"""
        try:
            today = datetime.utcnow().strftime("%Y-%m-%d")
            
            update_query = {"$inc": {"recommendation_count": 1}}
            
            if action_type == "feedback" and feedback_type:
                if feedback_type == "up":
                    update_query["$inc"]["positive_feedback"] = 1
                elif feedback_type == "down":
                    update_query["$inc"]["negative_feedback"] = 1
            elif action_type == "save":
                update_query["$inc"]["save_count"] = 1
                
            await self.db.analytics.update_one(
                {"solution_name": solution_name, "date": today},
                update_query,
                upsert=True
            )
            
        except Exception as e:
            logger.error(f"Error updating analytics: {str(e)}")
            
    async def get_popular_solutions(self, limit: int = 10) -> List[Dict]:
        """Get most popular solutions"""
        try:
            pipeline = [
                {"$group": {
                    "_id": "$solution_name",
                    "total_recommendations": {"$sum": "$recommendation_count"},
                    "total_positive_feedback": {"$sum": "$positive_feedback"},
                    "total_saves": {"$sum": "$save_count"}
                }},
                {"$sort": {"total_recommendations": -1}},
                {"$limit": limit}
            ]
            
            cursor = self.db.analytics.aggregate(pipeline)
            popular_solutions = await cursor.to_list(length=limit)
            return popular_solutions
            
        except Exception as e:
            logger.error(f"Error getting popular solutions: {str(e)}")
            return []

# Global database instance
database = Database()