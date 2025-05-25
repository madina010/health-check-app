from sqlalchemy import text
from datetime import datetime
import uuid

log_id = uuid.uuid4()

def save_health_score(session, user_id, score_result, age, recommendation=None):
    print(f"save_health_score вызван ({log_id}) для user_id={user_id}")
    print("calculate_health_score вызван")
    
    total_score = round(score_result["total_score"], 2)
    interpretation = score_result.get("interpretation")
    analysis = f"Итоговое состояние здоровья: {total_score}/100 – {interpretation} (с учетом вашего возраста)"

    try:
        session.execute(text("""
            INSERT INTO results (user_id, health_score, analysis_text, created_at, recommendation)
            VALUES (:user_id, :health_score, :analysis_text, :created_at, :recommendation)
        """), {
            "user_id": user_id,
            "health_score": total_score,
            "analysis_text": analysis,
            "created_at": datetime.utcnow(),
            "recommendation": recommendation
        })

        session.commit()
        print(f"Данные успешно сохранены для user_id={user_id}")

    except Exception as e:
        session.rollback()
        print(f"Ошибка при сохранении данных: {e}")
        raise
