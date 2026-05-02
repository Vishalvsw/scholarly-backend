from fastapi import APIRouter, HTTPException, status
from datetime import datetime
from urllib.parse import unquote
from app.database.mongodb import get_database
from pydantic import BaseModel, EmailStr

class SubscriptionCreate(BaseModel):
    email: EmailStr

class SubscriptionResponse(BaseModel):
    id: str
    email: EmailStr
    subscribed_at: datetime
    is_active: bool

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])

@router.post("/subscribe", response_model=SubscriptionResponse, status_code=status.HTTP_201_CREATED)
async def subscribe(subscription: SubscriptionCreate):
    db = get_database()
    try:
        existing = await db.subscriptions.find_one({"email": subscription.email})
        if existing:
            if existing.get("is_active"):
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already subscribed")
            else:
                await db.subscriptions.update_one(
                    {"email": subscription.email}, 
                    {"$set": {"is_active": True, "unsubscribed_at": None}}
                )
                existing["is_active"] = True
                existing["_id"] = str(existing["_id"])
                return existing
        
        subscription_data = {
            "email": subscription.email, 
            "subscribed_at": datetime.utcnow(), 
            "is_active": True
        }
        result = await db.subscriptions.insert_one(subscription_data)
        subscription_data["_id"] = str(result.inserted_id)
        return subscription_data
    except HTTPException:
        raise
    except Exception as e:
        print(f"Subscription error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail=f"Failed to subscribe: {str(e)}"
        )

@router.post("/unsubscribe")
async def unsubscribe(email: str):
    db = get_database()
    result = await db.subscriptions.update_one(
        {"email": email}, 
        {"$set": {"is_active": False, "unsubscribed_at": datetime.utcnow()}}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Email not found")
    return {"message": "Successfully unsubscribed"}

@router.get("/verify/{email}")
async def verify_subscription(email: str):
    db = get_database()
    decoded_email = unquote(email)
    subscription = await db.subscriptions.find_one({"email": decoded_email})
    if not subscription:
        return {"subscribed": False, "email": decoded_email}
    return {
        "subscribed": subscription.get("is_active", False), 
        "email": decoded_email
    }
