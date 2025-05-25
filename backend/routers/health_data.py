# from datetime import datetime
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.orm import Session
# from db.connection import get_db
# from db.models import HealthData, User, UserAnswer
# from pydantic import BaseModel
# from typing import List, Optional

# router = APIRouter()

# class HealthDataInput(BaseModel):
#     user_id: int
#     systolic_bp: int
#     diastolic_bp: int
#     pulse: int
#     temperature: float
#     height: int
#     weight: int
#     answers: List[Optional[dict]]

# @router.post("/submit_data")
# def submit_health_data(data: HealthDataInput, db: Session = Depends(get_db)):
#     user = db.query(User).filter(User.id == data.user_id).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="Пользователь не найден")

#     # Рассчет возраста пользователя на основе birth_date
#     age = (datetime.now() - user.birth_date).days // 365  # В годах

#     health_entry = HealthData(
#         user_id=data.user_id,
#         systolic_bp=data.systolic_bp,
#         diastolic_bp=data.diastolic_bp,
#         pulse=data.pulse,
#         temperature=data.temperature,
#         height=data.height,
#         weight=data.weight,
#         age=age  # Сохранение рассчитанного возраста
#     )
#     db.add(health_entry)
#     db.commit()

#     for answer in data.answers:
#         if answer and "question_id" in answer and "answer" in answer:
#             db.add(UserAnswer(user_id=data.user_id, question_id=answer["question_id"], answer=answer["answer"]))
    
#     db.commit()
#     return {"message": "Данные сохранены"}
