from sqlalchemy import text
from datetime import datetime
import uuid

log_id = uuid.uuid4()

def save_health_score(session, user_id, score_result, age, recommendation=None):
    total_score = round(score_result["total_score"], 2)
    interpretation = score_result.get("interpretation")
    analysis = f"Итоговое состояние здоровья: {total_score}/100 – {interpretation} (с учетом вашего возраста)"

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

    print(f"Данные подготовлены к сохранению для user_id={user_id}")
