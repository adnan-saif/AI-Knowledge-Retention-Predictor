class RecommendationEngine:
    @staticmethod
    def format_response(ai_result: dict) -> dict:
        return {
            "analysis": ai_result,
        }
