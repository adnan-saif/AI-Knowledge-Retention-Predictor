import json
from datetime import date
from src.gemini_client import GeminiClient
from src.schemas import LearnerInput

class RetentionAnalyzer:
    def __init__(self, prompt_template: str):
        self.client = GeminiClient()
        self.prompt_template = prompt_template

    def _clean_gemini_output(self, text: str) -> str:
        """
        Removes markdown code fences if present.
        """
        text = text.strip()

        if text.startswith("```"):
            text = text.replace("```json", "")
            text = text.replace("```", "")

        return text.strip()

    def analyze(self, learner_data: LearnerInput) -> dict:
        structured_data = learner_data.model_dump()

        for concept in structured_data["concepts"]:
            if isinstance(concept["last_revision"], date):
                concept["last_revision"] = concept["last_revision"].isoformat()

        prompt = f"""
{self.prompt_template}

Learner Study Data:
{json.dumps(structured_data, indent=2)}
"""

        raw_response = self.client.generate(prompt)

        cleaned_response = self._clean_gemini_output(raw_response)

        try:
            result = json.loads(cleaned_response)

            if "concepts_analysis" not in result:
                if "concepts" in result:
                    result["concepts_analysis"] = result["concepts"]
                else:
                    result["concepts_analysis"] = []

            return result

        except json.JSONDecodeError:
            return {
                "error": "Gemini returned invalid JSON",
                "raw_response": raw_response
            }
