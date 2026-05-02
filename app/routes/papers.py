from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form, status
from typing import List, Optional
from datetime import datetime
import os, shutil, uuid, json
from app.schemas.paper import PaperResponse
from app.database.mongodb import get_database
from app.middleware.auth import get_current_active_user
from app.config import settings

router = APIRouter(prefix="/papers", tags=["Papers"])

@router.post("/submit", response_model=PaperResponse, status_code=status.HTTP_201_CREATED)
async def submit_paper(
    title: str = Form(...), 
    abstract: str = Form(...), 
    keywords: str = Form(...), 
    authors: str = Form(...), 
    corresponding_author: str = Form(...), 
    file: UploadFile = File(...), 
    current_user: dict = Depends(get_current_active_user)
):
    db = get_database()
    
    # Validate file
    file_extension = os.path.splitext(file.filename)[1].lower()
    if file_extension not in settings.ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed: {settings.ALLOWED_EXTENSIONS}"
        )
    
    # Check file size
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)
    
    if file_size > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File too large. Max size: {settings.MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    # Save file
    unique_filename = f"{uuid.uuid4()}{file_extension}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Parse data
    authors_list = json.loads(authors)
    keywords_list = [k.strip() for k in keywords.split(",")]
    
    # Create paper document
    paper_data = {
        "title": title,
        "abstract": abstract,
        "keywords": keywords_list,
        "authors": authors_list,
        "corresponding_author": corresponding_author,
        "file_url": f"/uploads/{unique_filename}",
        "file_name": file.filename,
        "status": "pending",
        "author_id": current_user["_id"],
        "submitted_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await db.papers.insert_one(paper_data)
    paper_data["_id"] = str(result.inserted_id)
    
    return paper_data

@router.get("/", response_model=List[PaperResponse])
async def get_papers(
    skip: int = 0, 
    limit: int = 10, 
    status: Optional[str] = None, 
    current_user: dict = Depends(get_current_active_user)
):
    db = get_database()
    
    query = {}
    if current_user["role"] == "author":
        query["author_id"] = current_user["_id"]
    
    if status:
        query["status"] = status
    
    cursor = db.papers.find(query).sort("submitted_at", -1).skip(skip).limit(limit)
    papers = await cursor.to_list(length=limit)
    
    for paper in papers:
        paper["_id"] = str(paper["_id"])
    
    return papers

@router.get("/{paper_id}", response_model=PaperResponse)
async def get_paper(paper_id: str, current_user: dict = Depends(get_current_active_user)):
    db = get_database()
    
    paper = await db.papers.find_one({"_id": paper_id})
    
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    if current_user["role"] == "author" and paper["author_id"] != current_user["_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    paper["_id"] = str(paper["_id"])
    
    return paper
