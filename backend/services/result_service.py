from sqlalchemy import text
from datetime import datetime
import uuid
# from huggingface_client import get_recommendation

log_id = uuid.uuid4()

def save_health_score(session, user_id, score_data, age):
    print(f"save_health_score вызван ({log_id}) для user_id={user_id}")
    print("calculate_health_score вызван")
    # Сохранение результата расчёта здоровья в базу данных с использованием SQLAlchemy.
    total = round(score_data["total_score"], 2)
    interpretation = score_data.get("interpretation")
    analysis = f"Итоговое состояние здоровья: {total}/100 – {interpretation} (с учетом вашего возраста)"

    try:
        session.execute(text("""
            INSERT INTO results (user_id, health_score, analysis_text, created_at)
            VALUES (:user_id, :health_score, :analysis_text, :created_at)
        """), {
            "user_id": user_id,
            "health_score": total,
            "analysis_text": analysis,
            "created_at": datetime.utcnow()
        })

        session.commit()
        print(f"Данные успешно сохранены для user_id={user_id}")

    except Exception as e:
        session.rollback()
        print(f"Ошибка при сохранении данных: {e}")
        raise
