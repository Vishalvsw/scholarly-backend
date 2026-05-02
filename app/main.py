from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from app.config import settings
from app.database.mongodb import connect_to_mongo, close_mongo_connection
from app.routes import auth, papers, subscriptions, admin
app = FastAPI(title=settings.APP_NAME, description="Scholarly Publishing Platform Backend API", version="1.0.0", docs_url="/docs", redoc_url="/redoc")
app.add_middleware(CORSMiddleware, allow_origins=[settings.FRONTEND_URL, "http://localhost:3000", "http://localhost:8000"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
if os.path.exists(settings.UPLOAD_DIR):
    app.mount("/uploads", StaticFiles(directory=settings.UPLOAD_DIR), name="uploads")
app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(papers.router, prefix=settings.API_V1_PREFIX)
app.include_router(subscriptions.router, prefix=settings.API_V1_PREFIX)
app.include_router(admin.router, prefix=settings.API_V1_PREFIX)
@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()
    print(f"{settings.APP_NAME} started successfully!")
@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()
    print(f"{settings.APP_NAME} shut down successfully!")
@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.APP_NAME} API", "version": "1.0.0", "docs": "/docs", "status": "running"}
@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": settings.APP_NAME}
