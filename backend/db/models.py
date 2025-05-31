from sqlalchemy import Column, Integer, String, Float, ForeignKey, TIMESTAMP, Boolean, Date, Text
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    name = Column(String, nullable=False)
    birth_date = Column(Date, nullable=False)
    gender = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    avatar_path = Column(String, nullable=True)

    health_data = relationship("HealthData", back_populates="user", uselist=False)
    answers = relationship("UserAnswer", back_populates="user")
    results = relationship("Result", back_populates="user") 

class HealthData(Base):
    __tablename__ = "health_data"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    systolic_bp = Column(Integer, nullable=False)
    diastolic_bp = Column(Integer, nullable=False)
    pulse = Column(Integer, nullable=False)
    temperature = Column(Float, nullable=False)
    height = Column(Integer, nullable=False)
    weight = Column(Integer, nullable=False)
    age = Column(Integer, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)

    user = relationship("User", back_populates="health_data")

class Question(Base):
    __tablename__ = "questions"

    id = Column(Integer, primary_key=True)
    question_text = Column(String, nullable=False)
    weight = Column(Float, nullable=False)
    category = Column(String, nullable=False)
    positive_uns = Column(Boolean, nullable=False)

    answers = relationship("UserAnswer", back_populates="question")

class UserAnswer(Base):
    __tablename__ = "user_answers"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id"), nullable=False)
    answer = Column(Boolean, nullable=True)
    
    user = relationship("User", back_populates="answers")
    question = relationship("Question", back_populates="answers")

class Result(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    health_score = Column(Float, nullable=False)
    analysis_text = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    recommendation = Column(Text, nullable=True)

    user = relationship("User", back_populates="results")