from backend.calculations.utils import calculate_physiological_score, calculate_user_answers_score, get_age_norms

def calculate_health_score(health_data, user_answers, age):
    print(f"DEBUG: возраст = {age}, тип = {type(age)}")  
    
    # Баллы за физиологию
    print(f"DEBUG: norms = {get_age_norms(age)}")
    physio_scores = calculate_physiological_score(health_data, age)

    # Баллы за опросник
    print(f"DEBUG: user_answers = {user_answers}")
    answers_score = calculate_user_answers_score(user_answers)

    # Итоговый балл
    total_score = physio_scores["physiology_total"] + answers_score
    total_score = min(max(total_score, 0), 100)  # Ограничение от 0 до 100

    total_score = round(total_score, 1)  # Округление до 1 знака

    score_result = {
        "total_score": total_score,
        "details": {
            **physio_scores,
            "user_answers_score": answers_score
        }
    }

    print(f"DEBUG: score_result = {score_result}, тип = {type(score_result)}")
    
    return score_result
