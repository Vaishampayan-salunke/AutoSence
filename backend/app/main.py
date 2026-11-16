"""
AutoSense Main FastAPI Application Entrypoint
Title: Big Data Sentiment Analysis for the Automobile Industry using Apache Sqoop
"""
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
import time
from pathlib import Path
from backend.app.routes.api import router as api_router

app = FastAPI(
    title="AutoSense: Big Data Automobile Sentiment Analysis Platform",
    description="Full-Stack Big Data & NLP Platform for Automobile Reviews using MySQL, Sqoop, HDFS, Hive, and Machine Learning",
    version="1.0.0"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request Timing Middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = f"{process_time:.4f}s"
    return response

# Mount API Router
app.include_router(api_router)

@app.get("/health")
def healthcheck():
    return {
        "status": "healthy",
        "service": "AutoSense Analytics API",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "version": "1.0.0"
    }

# Mount the frontend after API routes so it cannot shadow /health.
dist_dir = Path(__file__).resolve().parents[2] / "frontend" / "dist"
if dist_dir.is_dir():
    app.mount("/", StaticFiles(directory=str(dist_dir), html=True), name="static")

if __name__ == '__main__':
    import uvicorn
    uvicorn.run("backend.app.main:app", host="127.0.0.1", port=8000, reload=True)
