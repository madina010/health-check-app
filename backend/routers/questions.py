# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session
# from db.connection import get_db
# from db.models import Question

# router = APIRouter()

# @router.get("/questions")
# def get_questions(db: Session = Depends(get_db)):
#     questions = db.query(Question).all()
#     return [{"id": q.id, "text": q.text, "category": q.category} for q in questions]
