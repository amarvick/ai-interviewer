# API Entry Point
# To run: uvicorn app.main:app --reload, go to http://127.0.0.1:8000
# must be in /backend directory to run command
# to check FastAPI configs, go to http://127.0.0.1:8000/docs

from fastapi import FastAPI
from sqlalchemy import text
from app.db.database import engine, Base
from app.api.routers import user, problem, attempt, testcase

app = FastAPI()

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
app.include_router(attempt.router)
app.include_router(testcase.router)
