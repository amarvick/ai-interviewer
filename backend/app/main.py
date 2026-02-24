# API Entry Point
# To run via http://127.0.0.1:8000
#   source venv/bin/activate 
#   uvicorn app.main:app --reload
# must be in /backend directory to run command
# to check FastAPI configs, go to http://127.0.0.1:8000/docs

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.db.database import engine, Base
from app.api.routers import user, problem, submission

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "AI Interviewer Backend is running!"}

@app.get("/health/db")
def check_db():
    with engine.connect() as connection:
        result = connection.execute(text("SELECT 1"))
        return {"database": "connected", "result": result.scalar()}

# Ensures tables are created
Base.metadata.create_all(bind=engine)
app.include_router(user.router)
app.include_router(problem.router)
app.include_router(submission.router)
