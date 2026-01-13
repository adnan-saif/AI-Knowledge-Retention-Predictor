from pydantic import BaseModel
from typing import List
from datetime import date

class ConceptInput(BaseModel):
    topic: str
    last_revision: date
    quiz_score: int
    difficulty: str

class LearnerInput(BaseModel):
    learner_name: str
    concepts: List[ConceptInput]
