# technical_test.py
import ollama
import json
import random
import logging
from sentence_transformers import SentenceTransformer, util
import torch

# Configure logging (optional, but helpful)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Load pre-trained model for semantic similarity
model = SentenceTransformer('all-MiniLM-L6-v2')

def is_reasonable_test(question, correct_choice, choices):
    """
    Check if a test question is reasonable by verifying that:
    1. The correct choice is within the choices.
    2. The question and correct choice have a reasonable semantic similarity.
    """
    if correct_choice not in choices:
        return False, "Correct choice not in available choices"

    # Create embeddings for the question and the correct choice
    question_embedding = model.encode(question, convert_to_tensor=True)
    correct_choice_embedding = model.encode(correct_choice, convert_to_tensor=True)

    # Calculate cosine similarity
    similarity = util.pytorch_cos_sim(question_embedding, correct_choice_embedding)[0][0]

    # Define a threshold for semantic similarity
    threshold = 0.5  # Adjust this threshold as needed

    if similarity.item() < threshold:
        return False, f"Question and correct choice are not semantically similar (Similarity: {similarity.item():.2f})"

    return True, None

def get_user_input(competencies, difficulty):
    if isinstance(competencies, list):
        competencies_str = ", ".join(competencies)
    else:
        competencies_str = competencies
    difficulty_str = difficulty.capitalize()
    return competencies_str, difficulty_str

def select_random_test(tests):
    return random.choice(tests) if tests else None

def generate_tests(competencies, difficulty, model='llama3.2:latest'):
    tests = []
    for comp in competencies.split(','):
        comp = comp.strip()  # Remove whitespace
        try:
            prompt = f"""
            Generate 5 multiple-choice questions for competency '{comp}' at difficulty level '{difficulty}'.
            Return ONLY valid JSON objects in this format:
            [
                {{
                    "question": "What is Python?",
                    "choices": ["A programming language", "A snake", "A car"],
                    "correct_choice": "A programming language"
                }},
                {{
                    "question": "What is 2 + 2?",
                    "choices": ["3", "4", "5"],
                    "correct_choice": "4"
                }}
            ]
            Do NOT include any explanations or text outside of JSON.
            """

            logging.debug(f"Sending prompt to Ollama for competency: {comp}")
            response = ollama.chat(model=model, messages=[{'role': 'user', 'content': prompt}])
            cleaned_response = response['message']['content']
            logging.debug(f"Raw response from Ollama: {cleaned_response}")
            try:
                new_tests = json.loads(cleaned_response)
                tests.extend(new_tests)
                logging.info(f"Successfully generated {len(new_tests)} tests for {comp}")
            except json.JSONDecodeError as e:
                logging.error(f"JSONDecodeError for {comp}: {e}. Response: {cleaned_response}")
        except Exception as e:
            logging.exception(f"Erreur avec {comp}: {str(e)}")
    return tests
