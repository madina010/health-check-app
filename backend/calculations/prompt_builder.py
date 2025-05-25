def build_prompt(score: int, qa_pairs: list[dict], phys_data: dict) -> str:
    bp = f"{phys_data['systolic']}/{phys_data['diastolic']} мм рт.ст."
    pulse = phys_data['pulse']
    temp = phys_data['temperature']
    height = phys_data['height']
    weight = phys_data['weight']
    
    symptoms_block = "\n".join(
        f"- {item['question']} Ответ: {item['answer']}."
        for item in qa_pairs
    )

    prompt = (
        f"Пользователь прошёл тест на здоровье и получил {score} баллов из 100.\n"
        f"Физиологические данные:\n"
        f"- Артериальное давление: {bp}\n"
        f"- Пульс: {pulse} уд/мин\n"
        f"- Температура тела: {temp}°C\n"
        f"- Рост: {height} см\n"
        f"- Вес: {weight} кг\n\n"
        f"Ответы пользователя на вопросы о самочувствии и образе жизни:\n"
        f"{symptoms_block}\n\n"
        f"На основе этих данных, составь персонализированные рекомендации по улучшению здоровья. "
        f"Удели внимание выявленным проблемам, но также отметь, что в норме. "
        f"Формулируй рекомендации простым и понятным языком для человека без медицинского образования."
    )

    return prompt
