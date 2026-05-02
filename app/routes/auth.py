from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.auth import UserCreate, UserLogin, Token, UserResponse
from app.utils.auth import get_password_hash, verify_password, create_access_token
from app.database.mongodb import get_database
from app.middleware.auth import get_current_user
from datetime import datetime
from bson import ObjectId

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate):
    db = get_database()
    
    # Check if user exists
    existing_user = await db.users.find_one({
        "$or": [
            {"email": user_data.email},
            {"username": user_data.username}
        ]
    })
    
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email or username already exists"
        )
    
    # Create new user
    user_dict = user_data.dict()
    user_dict["hashed_password"] = get_password_hash(user_dict.pop("password"))
    user_dict["created_at"] = datetime.utcnow()
    user_dict["updated_at"] = datetime.utcnow()
    user_dict["role"] = "author"
    user_dict["is_active"] = True
    user_dict["is_verified"] = False
    
    result = await db.users.insert_one(user_dict)
    created_user = await db.users.find_one({"_id": result.inserted_id})
    created_user["_id"] = str(created_user["_id"])
    created_user.pop("hashed_password", None)
    
    return created_user

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin):
    db = get_database()
    
    user = await db.users.find_one({"email": user_data.email})
    
    if not user or not verify_password(user_data.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    
    # Create access token with string ID
    user_id_str = str(user["_id"])
    access_token = create_access_token(
        data={"sub": user_id_str, "email": user["email"], "role": user["role"]}
    )
    
    user_response = {
        "id": user_id_str,
        "username": user["username"],
        "email": user["email"],
        "full_name": user.get("full_name"),
        "institution": user.get("institution"),
        "role": user["role"],
        "is_verified": user["is_verified"],
        "created_at": user["created_at"]
    }
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user_response
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information"""
    return current_user
