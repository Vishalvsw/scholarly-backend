from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field
from bson import ObjectId
class Review(BaseModel):
    reviewer_id: str
    comments: str
    rating: int
    status: str
    submitted_at: Optional[datetime] = None
class Paper(BaseModel):
    id: Optional[str] = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    title: str
    abstract: str
    keywords: List[str] = []
    authors: List[dict]
    corresponding_author: str
    file_url: str
    file_name: str
    status: str = "pending"
    author_id: str
    submitted_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    reviews: List[Review] = []
    editor_comments: Optional[str] = None
    published_at: Optional[datetime] = None
    doi: Optional[str] = None
    class Config:
        allow_population_by_field_name = True
