from pydantic import BaseModel, Field, validator, EmailStr
from typing import List, Optional
from datetime import datetime
class Author(BaseModel):
    name: str
    email: EmailStr
    affiliation: str
    orcid: Optional[str] = None
class PaperCreate(BaseModel):
    title: str = Field(..., min_length=5, max_length=500)
    abstract: str = Field(..., min_length=50, max_length=5000)
    keywords: List[str] = Field(default_factory=list)
    authors: List[Author]
    corresponding_author: str
    @validator('keywords')
    def validate_keywords(cls, v):
        if len(v) > 10:
            raise ValueError('Maximum 10 keywords allowed')
        return v
class PaperResponse(BaseModel):
    id: str
    title: str
    abstract: str
    keywords: List[str]
    authors: List[dict]
    status: str
    submitted_at: datetime
    file_url: str
    file_name: str
class PaperUpdate(BaseModel):
    title: Optional[str] = None
    abstract: Optional[str] = None
    keywords: Optional[List[str]] = None
    status: Optional[str] = None
