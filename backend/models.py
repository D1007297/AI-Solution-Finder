from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
import uuid


class Solution(BaseModel):
    name: str
    category: str
    description: str
    link: str
    use_cases: List[str]
    tags: List[str] = []
    popularity_score: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class RecommendationRequest(BaseModel):
    problem_statement: str
    excluded_solutions: Optional[List[str]] = []
    user_preferences: Optional[Dict] = {}


class RecommendationResponse(BaseModel):
    name: str
    category: str
    description: str
    link: str
    use_cases: List[str]
    explanation: str
    rank: int
    confidence: float
    reasoning: str


class FeedbackRequest(BaseModel):
    session_id: str
    solution_name: str
    feedback_type: str  # "up" or "down"
    recommendation_rank: int
    problem_statement: str


class SaveSolutionRequest(BaseModel):
    session_id: str
    solution_name: str
    problem_statement: str


class UserInteraction(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    problem_statement: str
    recommendations: List[Dict]
    feedback: List[Dict] = []
    saved_solutions: List[str] = []
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Analytics(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    solution_name: str
    query_category: str
    recommendation_count: int = 0
    positive_feedback: int = 0
    negative_feedback: int = 0
    save_count: int = 0
    date: str = Field(default_factory=lambda: datetime.utcnow().strftime("%Y-%m-%d"))