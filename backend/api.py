from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from typing import List, Optional
from backend.db.connection import get_db
from backend.db.models import Question, HealthData, UserAnswer, Result, User
from backend.calculate_service import calculate_for_user
from backend.services.result_service import save_health_score
from backend.auth import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import date
from typing import List
from backend.calculations.prompt_builder import build_prompt
from g4f import ChatCompletion
from g4f.models import (
    gpt_4, gpt_4o, gpt_3_5_turbo, claude_3_5_sonnet, llama_3_2_11b, mixtral_8x22b
)

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")  

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class UserCreate(BaseModel):
    full_name: str
    gender: Optional[str] = None
    birthdate: date
    email: EmailStr
    password: str

class AnswerInput(BaseModel):
    question_id: int
    answer: Optional[bool]

class UserInput(BaseModel):
    systolic_bp: int
    diastolic_bp: int
    pulse: int
    temperature: float
    height: int
    weight: int
    answers: List[AnswerInput]

# Вспомогательные функции

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict):
    from datetime import datetime, timedelta
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def authenticate_user(db: Session, email: str, password: str):
    user = get_user_by_email(db, email)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    user = get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

# Роуты регистрации и входа

@router.post("/auth/register", status_code=201)
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user.password)
    new_user = User(
        email=user.email,
        password=hashed_password,
        name=user.full_name,
        gender=user.gender,
        birth_date=user.birthdate
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return {"message": "User registered successfully"}

@router.post("/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

# Основные роуты (только для авторизованных пользователей)

@router.get("/")
def read_root():
    return {"message": "API is running"}

@router.get("/questions")
def get_questions(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return db.query(Question).all()

@router.get("/results")
def get_results(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    results = db.query(Result).filter(Result.user_id == current_user.id).all()
    return results

@router.get("/my_last_result")
def get_my_last_result(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    last_result = (
        db.query(Result)
        .filter(Result.user_id == current_user.id)
        .order_by(Result.created_at.desc())
        .first()
    )

    if last_result is None:
        return {"message": "Результаты ещё не рассчитаны"}

    return {
        "health_score": round(last_result.health_score, 2),
        "analysis_text": last_result.analysis_text,
        "created_at": last_result.created_at
    }

@router.post("/submit_health_data")
def submit_health_data(data: UserInput, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    # Сохранение физиологических данных
    health_entry = HealthData(
        user_id=current_user.id,
        systolic_bp=data.systolic_bp,
        diastolic_bp=data.diastolic_bp,
        pulse=data.pulse,
        temperature=data.temperature,
        height=data.height,
        weight=data.weight
    )
    db.add(health_entry)
    db.commit()

    # Сохранение ответов
    for answer in data.answers:
        if answer.answer is not None:
            new_answer = UserAnswer(
                user_id=current_user.id,
                question_id=answer.question_id,
                answer=answer.answer
            )
            db.add(new_answer)
    db.commit()

    # Вызов расчёта и сохранение результата
    result_data = calculate_for_user(current_user.id)

    if result_data:
        age = current_user.age if hasattr(current_user, 'age') else 0
        save_health_score(db, current_user.id, result_data, age)
        db.commit()  # коммит один раз в конце всего

        return {
            "total_score": round(result_data["total_score"], 2),
            "physiology_score": round(result_data["details"]["physiology_total"], 2),
            "answers_score": round(result_data["details"]["user_answers_score"], 2),
            "analysis": result_data.get("analysis_text", "")
        }

@router.get("/users/me")
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "email": current_user.email,
        "name": current_user.name,
        "gender": current_user.gender,
        "birth_date": current_user.birth_date
    }

models_to_try = [
    gpt_4, gpt_4o, gpt_3_5_turbo,
    claude_3_5_sonnet,
    llama_3_2_11b, mixtral_8x22b,
]

@router.post("/generate_recommendation")
def generate_recommendation(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    last_result = (
        db.query(Result)
        .filter(Result.user_id == current_user.id)
        .order_by(Result.created_at.desc())
        .first()
    )
    if not last_result:
        raise HTTPException(status_code=404, detail="Результаты не найдены")

    score = round(last_result.health_score, 2)

    user_answers = (
        db.query(UserAnswer, Question)
        .join(Question, UserAnswer.question_id == Question.id)
        .filter(UserAnswer.user_id == current_user.id)
        .all()
    )

    qa_pairs = []
    for ua, q in user_answers:
        ans_text = "Да" if ua.answer else "Нет" if ua.answer is not None else "Не знаю"
        qa_pairs.append({"question": q.question_text, "answer": ans_text})

    phys_data_entry = (
        db.query(HealthData)
        .filter(HealthData.user_id == current_user.id)
        .order_by(HealthData.created_at.desc())
        .first()
    )
    if not phys_data_entry:
        raise HTTPException(status_code=404, detail="Физиологические данные не найдены")

    phys_data = {
        "systolic": phys_data_entry.systolic_bp,
        "diastolic": phys_data_entry.diastolic_bp,
        "pulse": phys_data_entry.pulse,
        "temperature": phys_data_entry.temperature,
        "height": phys_data_entry.height,
        "weight": phys_data_entry.weight
    }

    prompt = build_prompt(score, qa_pairs, phys_data, age=phys_data_entry.age)

    last_exception = None
    recommendation = None

    for model in models_to_try:
        try:
            print(f"[INFO] Trying model: {model.name}")
            response = ChatCompletion.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                stream=False,
            )

            if response and isinstance(response, str) and response.strip():
                recommendation = response
                print(f"[INFO] Model {model.name} succeeded")
                break
        except Exception as e:
            last_exception = e
            print(f"[ERROR] Ошибка при вызове модели {model.name}: {e}")

    if not recommendation or not recommendation.strip():
        raise HTTPException(
            status_code=500,
            detail=f"Не удалось получить рекомендацию. Последняя ошибка: {last_exception}"
        )

    last_result.recommendation = recommendation
    db.commit()
    db.refresh(last_result)

    print(f"[INFO] Recommendation saved to DB. Type: {type(recommendation)}")
    print(f"[INFO] Recommendation content preview: {recommendation[:500]}")

    return {"recommendation": recommendation}