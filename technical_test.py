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

# technical_test.py
def generate_tests(competencies, difficulty, model='llama3.2:latest'):
    tests = []

    for competency in competencies.split(', '):
        competency = competency.strip()
        prompt = (
            f"Générez exactement 10 questions à choix multiples pour la compétence '{competency}' au niveau {difficulty}. "
            f"La réponse JSON doit contenir exactement 10 objets, chacun représentant une question. Chaque objet doit avoir : "
            f"'question' (chaîne), 'choices' (liste de chaînes), et 'correct_choice' (chaîne). "
            f"Format de réponse : "
            f'[{{"question": "Quelle est la capitale de la France ?", "choices": ["Paris", "Londres", "Berlin"], "correct_choice": "Paris"}}, ...]. '
            f"Ne retournez que les données JSON, sans explications."
        )

        response = ollama.chat(model=model, messages=[{'role': 'user', 'content': prompt}])
        try:
            response_content = response.get('message', {}).get('content', '')
            try:
                test_data = json.loads(response_content)
            except json.JSONDecodeError as e:
                print(f"Erreur lors du traitement de la réponse pour '{competency}': {e}. Réponse non valide.")
                continue

            for test in test_data:
                tests.append({
                    "competency": competency,
                    "question": test.get("question", ""),
                    "choices": test.get("choices", []),
                    "correct_choice": test.get("correct_choice", "")
                })
        except Exception as e:
            print(f"Erreur lors du traitement de la réponse pour '{competency}': {e}")

    return tests


def select_random_test(tests):
    return random.choice(tests) if tests else None
