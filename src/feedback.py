from ai import generate_object
from prompt import system_prompt
from ai.providers import o3MiniModel

async def generate_feedback(query: str, num_questions: int = 3):
    prompt_text = (
        f"Given the following query from the user, ask some follow up questions to clarify the research direction. "
        f"Return a maximum of {num_questions} questions, but feel free to return less if the original query is clear: "
        f"<query>{query}</query>"
    )

    result = await generate_object(
        model=o3MiniModel,
        system=system_prompt(),
        prompt=prompt_text,
        schema={"questions": list}  # Placeholder schema
    )

    return result["object"]["questions"][:num_questions]
