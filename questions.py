import json
import random
from pathlib import Path

QUESTION_FILE = Path(__file__).with_name("questions.json")


def get_question():
    with QUESTION_FILE.open("r", encoding="utf-8") as file:
        pool = json.load(file)

    if not pool:
        return None

    return random.choice(pool)


def remove_question(question_id: int):
    with QUESTION_FILE.open("r", encoding="utf-8") as file:
        pool = json.load(file)

    pool = [question for question in pool if question["id"] != question_id]

    with QUESTION_FILE.open("w", encoding="utf-8") as file:
        json.dump(pool, file, indent=4)