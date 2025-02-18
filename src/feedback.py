from ai.ai import generate_object
from prompt import system_prompt
from ai.providers import o3MiniModel
from pydantic import BaseModel
from typing import List

class FeedbackSchema(BaseModel):
    questions: List[str]

async def generate_feedback(query: str, num_questions: int = 3) -> List[str]:
    # Added explicit instruction: "Return your result in JSON..."
    prompt_text = (
        f"Given the following query from the user, ask some follow up questions to clarify the research direction.\n\n"
        f"Return your result in JSON format with the shape:\n"
        f'{{ "questions": [ "question1", "question2" ] }}\n\n'
        f"Return a maximum of {num_questions} questions, but feel free to return less if the original query is clear.\n"
        f"<query>{query}</query>"
    )

    result = await generate_object(
        model=o3MiniModel,
        system=system_prompt(),
        prompt=prompt_text,
        schema=FeedbackSchema
    )
    return result["object"].questions[:num_questions]
