import openai
from sqlalchemy.orm import Session
from crud import update_translation_task
from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

def perform_translation(task_id: int, text: str, languages: list, db: Session):
    translations = {}

    for language in languages:
        try:
            translation = openai.ChatCompletion.create(
                model='gpt-4o',
                messages=[
                    {"role": "system", "content": f"Translate the following text to {language}:"},
                    {"role": "user", "content": text}
                ],
                max_tokens=1000,
            )
            print('utils', translation['choices'][0]['message']['content'].strip())
            translations[language] = translation['choices'][0]['message']['content'].strip()
        except Exception as e:
            print(f'Unexpected error: {e}')
            translations[language] = f'Error: {e}'

    update_translation_task(db, task_id, translations)  # Update the task with the translations