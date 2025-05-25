from decimal import Decimal

def validate_positive(value, name="value"):
    """Проверка, что значение положительное."""
    if value is None:
        raise ValueError(f"{name} не может быть None")
    if not isinstance(value, (int, float)):
        raise TypeError(f"{name} должно быть числом, но получено {type(value)}")
    if value <= 0:
        raise ValueError(f"{name} должно быть положительным числом, получено {value}")
    return value


def get_age_norms(age):
    """
    Возвращает возрастные нормы для АД, пульса и ИМТ.
    """
    # Валидация возраста
    age = validate_positive(age, "age")
    
    age_norms = {
        "bp": {  # Артериальное давление
            (18, 30): (120, 80),
            (31, 45): (125, 85),
            (46, 60): (130, 85),
            (61, 100): (135, 90),
        },
        "pulse": {  # Пульс
            (18, 30): (60, 80),
            (31, 45): (62, 82),
            (46, 60): (64, 84),
            (61, 100): (66, 86),
        },
        "bmi": {  # Индекс массы тела (ИМТ)
            (18, 30): (18.5, 24.9),
            (31, 45): (19, 25.5),
            (46, 60): (19.5, 26),
            (61, 100): (20, 27),
        },
    }

    def get_norm(category):
        for age_range, norm in age_norms[category].items():
            if age_range[0] <= age <= age_range[1]:
                return norm
        return None  # Если возраст не найден

    return {
        "bp": get_norm("bp"),
        "pulse": get_norm("pulse"),
        "bmi": get_norm("bmi"),
    }


def calculate_physiological_score(health_data, age):
    """
    Рассчитывает баллы на основе физиологических данных (АД, пульс, температура, BMI) с учетом возраста.
    """
    # Валидация данных здоровья
    health_data["weight"] = validate_positive(health_data.get("weight"), "weight")
    health_data["height"] = validate_positive(health_data.get("height"), "height")
    health_data["temperature"] = validate_positive(health_data.get("temperature"), "temperature")
    
    # Валидация возраста
    age = validate_positive(age, "age")
    
    scores = {}
    norms = get_age_norms(age)

    # Индекс массы тела (BMI)
    height_m = float(health_data["height"]) / 100
    weight_kg = float(health_data["weight"])
    bmi = weight_kg / (height_m ** 2)

    def score_from_norm(value, norm_range, max_score=10):
        """Функция для вычисления баллов на основе нормальных значений."""
        lower, upper = norm_range
        if lower <= value <= upper:
            return max_score  # Идеальное значение
        elif value < lower:
            return max(max_score - ((lower - value) * 2), 5)  # Чем ниже, тем хуже
        else:
            return max(max_score - ((value - upper) * 2), 5)  # Чем выше, тем хуже

    # Извдечение нормального давления
    if norms["bp"] is not None:
        bp_norm_systolic, bp_norm_diastolic = norms["bp"]

        # Оценка давления раздельно
        scores["systolic_bp_score"] = score_from_norm(health_data["systolic_bp"], (bp_norm_systolic - 10, bp_norm_systolic + 10))
        scores["diastolic_bp_score"] = score_from_norm(health_data["diastolic_bp"], (bp_norm_diastolic - 5, bp_norm_diastolic + 5))

    # Оценка пульса
    if norms["pulse"] is not None:
        scores["pulse_score"] = score_from_norm(health_data["pulse"], norms["pulse"], max_score=10)

    # Температура тела
    temp = health_data["temperature"]
    scores["temperature_score"] = 10 if Decimal("36.0") <= temp <= Decimal("37.0") else 6

    # Оценка BMI
    if norms["bmi"] is not None:
        scores["bmi_score"] = score_from_norm(bmi, norms["bmi"])

    # Итоговые баллы физиологии
    scores["physiology_total"] = sum(scores.values())

    return scores


def calculate_user_answers_score(user_answers):
    # Валидация ответов
    if not isinstance(user_answers, list):
        raise TypeError("user_answers должно быть списком")
    
    raw_score = 0
    for ans in user_answers:
        if "answer" not in ans or "weight" not in ans:
            raise ValueError("Каждый ответ должен содержать ключи 'answer' и 'weight'")
        
        if not isinstance(ans["answer"], bool):
            raise TypeError("Ответ должен быть типа bool")
        
        if not isinstance(ans["weight"], (int, float)):
            raise TypeError("Вес ответа должен быть числом")
        
        if not ans["answer"]:  # Если ответ "Нет"
            raw_score += ans["weight"]

    # Определение максимального возможного балла
    max_possible_score = sum(ans["weight"] for ans in user_answers if isinstance(ans.get("weight"), (int, float)))

    # Нормализация до 50-балльной шкалы
    if max_possible_score > 0:
        normalized_score = (raw_score / max_possible_score) * 50
    else:
        normalized_score = 0  # Если нет ответов, ставим 0

    return normalized_score

def get_interpretation(score: float, age: int) -> str:
    print(f"DEBUG: Вызов get_interpretation(score={score}, age={age})")

    # Допустим, для пожилых людей (старше 60) границы могут быть чуть мягче
    if age >= 60:
        if score >= 80:
            return "Отличное состояние здоровья с учетом возраста"
        elif score >= 65:
            return "Хорошее состояние здоровья с учетом возраста"
        elif score >= 45:
            return "Удовлетворительное состояние здоровья с учетом возраста"
        elif score >= 25:
            return "Состояние здоровья требует внимания с учетом возраста"
        else:
            return "Низкий уровень здоровья с учетом возраста"
    else:
        # Текущие стандартные пороги
        if score >= 85:
            return "Отличное состояние здоровья"
        elif score >= 70:
            return "Хорошее состояние здоровья"
        elif score >= 50:
            return "Удовлетворительное состояние здоровья"
        elif score >= 30:
            return "Состояние здоровья требует внимания"
        else:
            return "Низкий уровень здоровья"

