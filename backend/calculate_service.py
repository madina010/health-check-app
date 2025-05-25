import time
from backend.db.connection import get_db
from backend.calculations.score_calculator import calculate_health_score
from backend.db.models import User, HealthData, UserAnswer, Question
from datetime import datetime
import traceback

start_time = time.time()

conn_gen = get_db()
session = next(conn_gen) 
print(f"Подключение заняло {time.time() - start_time:.4f} сек")

def calculate_for_user(user_id: int):
    if user_id is None:
        raise ValueError("user_id не может быть None. Авторизация обязательна.")
    
    try:
        # Получение возраста пользователя
        user = session.query(User).filter(User.id == user_id).first()
        if not user:
            print("Ошибка: Пользователь не найден.")
            return None

        birth_date = user.birth_date
        age = (datetime.now().date() - birth_date).days // 365 
        print(f"DEBUG: возраст = {age}")

        # Получение данных о здоровье пользователя
        health_data = session.query(HealthData).filter(HealthData.user_id == user_id).order_by(HealthData.created_at.desc()).first()
        if not health_data:
            print("Ошибка: Данные о здоровье отсутствуют.")
            return None

        health_data_dict = {
            "systolic_bp": int(health_data.systolic_bp),
            "diastolic_bp": int(health_data.diastolic_bp),
            "pulse": int(health_data.pulse),
            "temperature": float(health_data.temperature),
            "weight": float(health_data.weight),
            "height": float(health_data.height),
        }
        
        # Получение ответов пользователя
        user_answers_raw = session.query(UserAnswer, Question.weight).join(Question).filter(UserAnswer.user_id == user_id).all()

        user_answers = [
            {"question_id": row[0].question_id, "weight": float(row[1]), "answer": bool(row[0].answer) if row[0].answer is not None else False}
            for row in user_answers_raw
        ]

        # Расчёт итогового балла
        print("DEBUG: Запуск calculate_health_score()")
        score_result = calculate_health_score(health_data_dict, user_answers, age)
        
        print(f"DEBUG: Интерпретация = {score_result.get('interpretation')}")

        # Возврат результата
        session.commit()
        print(f"Расчёт завершён. Баллы: {score_result['total_score']:.2f}")

        return score_result

    except Exception as e:
        print(f"Ошибка: {e}")
        print(traceback.format_exc())
        session.rollback()
        return None
    finally:
        session.close()
