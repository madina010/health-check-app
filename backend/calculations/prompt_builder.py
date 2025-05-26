def build_prompt(score: int, qa_pairs: list[dict], phys_data: dict, age: int | None = None) -> str:
    bp = f"{phys_data['systolic']}/{phys_data['diastolic']} мм рт.ст."
    pulse = phys_data['pulse']
    temp = phys_data['temperature']
    height = phys_data['height']
    weight = phys_data['weight']

    symptoms_block = "\n".join(
        f"- {item['question']} Ответ: {item['answer']}."
        for item in qa_pairs
    )

    age_info = f"Возраст пользователя: {age} лет.\n" if age is not None else ""

    prompt = (
        f"Ты медицинский AI-ассистент. На основе предоставленных данных составь персонализированные советы по улучшению здоровья.\n\n"
        f"{age_info}"
        f"Оценка состояния здоровья пользователя: {score} из 100.\n"
        f"Физиологические данные:\n"
        f"- Артериальное давление: {bp}\n"
        f"- Пульс: {pulse} уд/мин\n"
        f"- Температура тела: {temp}°C\n"
        f"- Рост: {height} см\n"
        f"- Вес: {weight} кг\n\n"
        f"Ответы на вопросы о самочувствии и образе жизни:\n"
        f"{symptoms_block}\n\n"
        f"Составь рекомендации простым и понятным языком, избегая медицинских терминов. "
        f"Укажи, какие показатели находятся в пределах нормы, а на что стоит обратить внимание. "
        f"Если всё в порядке — сообщи об этом, но всё равно посоветуй, как поддерживать хорошее состояние здоровья."
        f"Не забудь предупредить, что прохождение подобного теста лишь поверхностная оценка здоровья, поэтому лучше обратиться в профессиональные учреждения."
    )

    return prompt
