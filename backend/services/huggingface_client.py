import requests
import os

HUGGINGFACE_API_TOKEN = os.getenv("HUGGINGFACE_API_TOKEN")  

MODEL = "tiiuae/falcon-7b-instruct"

API_URL = f"https://api-inference.huggingface.co/models/{MODEL}"
HEADERS = {"Authorization": f"Bearer {HUGGINGFACE_API_TOKEN}"}


def get_recommendation(prompt: str) -> str:
    payload = {
        "inputs": prompt,
        "options": {
            "wait_for_model": True  # Подождать, если модель спит
        }
    }

    response = requests.post(API_URL, headers=HEADERS, json=payload)

    if response.status_code != 200:
        return f"Ошибка запроса: {response.status_code}, {response.text}"

    result = response.json()

    if isinstance(result, list) and "generated_text" in result[0]:
        return result[0]["generated_text"]

    return str(result)
