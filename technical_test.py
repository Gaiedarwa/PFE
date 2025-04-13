import ollama
import json
import random

def get_user_input(competencies, difficulty):
    if isinstance(competencies, list):
        competencies_str = ", ".join(competencies)
    else:
        competencies_str = competencies

    difficulty_str = difficulty.capitalize()

    return competencies_str, difficulty_str


def select_random_test(tests):
    return random.choice(tests) if tests else None
import ollama
import json
import random

def generate_tests(competencies, difficulty, model='llama3.2:latest'):
    tests = []
    for comp in competencies:
        try:
            prompt = f"""Générer 5 QCM pour {comp} (niveau {difficulty}) au format JSON :
            [{
                "question": "Question?",
                "choices": ["A", "B", "C"],
                "correct_choice": "A"
            }]"""
            
            response = ollama.chat(model=model, messages=[{'role': 'user', 'content': prompt}])
            cleaned_response = response['message']['content'].replace('``````', '')
            tests.extend(json.loads(cleaned_response))
        except Exception as e:
            print(f"Erreur avec {comp}: {str(e)}")
    return tests

def select_random_test(tests):
    return random.choice(tests) if tests else None
