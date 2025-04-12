import ollama
import json

def get_user_input(competencies_str, difficulty_str):
    competencies = competencies_str.split(",")
    difficulty = difficulty_str.lower()
    return competencies, difficulty

def generate_tests(competencies, difficulty, model='llama3.2:latest'):
    tests = []

    for competency in competencies:
        competency = competency.strip()
        prompt = (
            f"Generate exactly 10 multiple-choice questions for the competency '{competency}' at a {difficulty} level. "
            f"The JSON response must contain exactly 10 objects, each representing a question. Each object should have: "
            f"'question' (string), 'choices' (list of strings), and 'correct_choice' (string). "
            f"Response format: "
            f'[{{"question": "What is 2+2?", "choices": ["1", "2", "4"], "correct_choice": "4"}}, ...]. '
            f"Only return JSON data, without explanations."
        )

        response = ollama.chat(model=model, messages=[{'role': 'user', 'content': prompt}])
        try:
            response_content = response.get('message', {}).get('content', '')
            test_data = json.loads(response_content)

            for test in test_data:
                tests.append({
                    "competency": competency,
                    "question": test.get("question", ""),
                    "choices": test.get("choices", []),
                    "correct_choice": test.get("correct_choice", "")
                })
        except (json.JSONDecodeError, TypeError) as e:
            print(f"Error processing response for '{competency}': {e}")

    return tests
