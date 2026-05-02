from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from datetime import datetime, timedelta
from app.middleware.auth import require_role
from app.database.mongodb import get_database
router = APIRouter(prefix="/admin", tags=["Admin"])
@router.get("/dashboard/stats")
async def get_dashboard_stats(admin: dict = Depends(require_role(["admin", "editor"]))):
    db = get_database()
    total_users = await db.users.count_documents({})
    total_papers = await db.papers.count_documents({})
    pending_papers = await db.papers.count_documents({"status": "pending"})
    under_review = await db.papers.count_documents({"status": "under_review"})
    accepted = await db.papers.count_documents({"status": "accepted"})
    rejected = await db.papers.count_documents({"status": "rejected"})
    published = await db.papers.count_documents({"status": "published"})
    total_subscribers = await db.subscriptions.count_documents({"is_active": True})
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_submissions = await db.papers.count_documents({"submitted_at": {"$gte": week_ago}})
    return {"total_users": total_users, "total_papers": total_papers, "pending_papers": pending_papers, "under_review": under_review, "accepted": accepted, "rejected": rejected, "published": published, "total_subscribers": total_subscribers, "recent_submissions": recent_submissions}
@router.get("/papers")
async def get_all_papers(status: Optional[str] = None, skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100), admin: dict = Depends(require_role(["admin", "editor"]))):
    db = get_database()
    query = {}
    if status:
        query["status"] = status
    cursor = db.papers.find(query).sort("submitted_at", -1).skip(skip).limit(limit)
    papers = await cursor.to_list(length=limit)
    for paper in papers:
        paper["_id"] = str(paper["_id"])
        author = await db.users.find_one({"_id": paper["author_id"]})
        paper["author_name"] = author.get("full_name") or author.get("username") if author else "Unknown"
    total = await db.papers.count_documents(query)
    return {"papers": papers, "total": total, "skip": skip, "limit": limit}
@router.put("/papers/{paper_id}/review")
async def update_paper_status(paper_id: str, status: str, editor_comments: Optional[str] = None, admin: dict = Depends(require_role(["admin", "editor"]))):
    db = get_database()
    valid_statuses = ["pending", "under_review", "accepted", "rejected", "published"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")
    update_data = {"status": status, "updated_at": datetime.utcnow()}
    if editor_comments:
        update_data["editor_comments"] = editor_comments
    if status == "published":
        update_data["published_at"] = datetime.utcnow()
        update_data["doi"] = f"10.1234/scholarly.{paper_id}"
    result = await db.papers.update_one({"_id": paper_id}, {"$set": update_data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Paper not found")
    return {"message": "Paper status updated successfully"}
@router.get("/users")
async def get_all_users(skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100), admin: dict = Depends(require_role(["admin"]))):
    db = get_database()
    cursor = db.users.find({}, {"hashed_password": 0}).skip(skip).limit(limit)
    users = await cursor.to_list(length=limit)
    for user in users:
        user["_id"] = str(user["_id"])
    total = await db.users.count_documents({})
    return {"users": users, "total": total, "skip": skip, "limit": limit}
