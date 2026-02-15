# API Entry Point
# To run: uvicorn app.main:app --reload, go to http://127.0.0.1:8000
# must be in /backend directory to run command
# to check FastAPI configs, go to http://127.0.0.1:8000/docs

from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.database import engine, Base, get_db
from app import models, schemas

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

@app.post("/problems", response_model=schemas.ProblemResponse)
def create_problem(problem: schemas.ProblemCreate, db: Session = Depends(get_db)):
    db_problem = models.Problem(
        title=problem.title,
        description=problem.description,
        difficulty=problem.difficulty,
        category=problem.category
    )
    db.add(db_problem)
    db.commit()
    db.refresh(db_problem)
    return db_problem

@app.get("/problems", response_model=list[schemas.ProblemResponse])
def get_problems(db: Session = Depends(get_db)):
    problems = db.query(models.Problem).all()
    return problems
