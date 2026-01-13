import json
from src.gemini_client import GeminiClient

class QuizGenerator:
    def __init__(self, prompt_template: str):
        self.client = GeminiClient()
        self.prompt_template = prompt_template

    def generate_quiz(self, topic_data: dict) -> dict:
        prompt = f"""
{self.prompt_template}

Topic Data:
{json.dumps(topic_data, indent=2)}
"""

        response = self.client.generate(prompt)

        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "error": "Invalid quiz JSON returned",
                "raw_response": response
            }
