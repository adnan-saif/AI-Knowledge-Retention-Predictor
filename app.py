from fastapi import FastAPI
from src.schemas import LearnerInput
from src.retention_analyzer import RetentionAnalyzer
from src.recommendation_engine import RecommendationEngine
from src.quiz_generator import QuizGenerator


app = FastAPI(title="AI Knowledge Retention Predictor")

with open("prompts/retention_reasoning_prompt.txt") as f:
    PROMPT = f.read()

analyzer = RetentionAnalyzer(PROMPT)

with open("prompts/quiz_generation_prompt.txt") as f:
    QUIZ_PROMPT = f.read()

quiz_generator = QuizGenerator(QUIZ_PROMPT)


@app.post("/predict")
def predict(data: LearnerInput):
    analysis = analyzer.analyze(data)

    quizzes = []
    for concept in analysis.get("concepts_analysis", []):
        quiz = quiz_generator.generate_quiz(concept)
        quizzes.append(quiz)

    return {
        "analysis": analysis,
        "quizzes": quizzes
    }

