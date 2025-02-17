import json
from typing import Any, Callable, Optional, Dict, Awaitable

async def generate_object(
    *,
    model: Callable[..., Awaitable[Any]],
    prompt: str,
    system: Optional[str] = None,
    schema: Optional[Any] = None,
    **kwargs,
) -> Dict[str, Any]:
    """
    Generates a structured object from a given prompt using the provided language model (async).

    Parameters:
      - model: An async callable that takes a prompt (plus any additional kwargs) and returns a ChatCompletion object.
      - prompt: The user prompt to send to the model.
      - system: An optional system prompt to prefix the user prompt.
      - schema: An optional Pydantic model (or callable) to validate/transform the parsed output.
      - kwargs: Additional keyword arguments to pass along to the model call.

    Returns:
      A dictionary with:
        - "object": The parsed (and optionally validated) structured object.
        - "raw": The raw response from the model.
    """
    final_prompt = f"{system}\n{prompt}" if system else prompt
    response = await model(final_prompt, **kwargs)

    try:
        text_output = response.choices[0].message.content
    except (AttributeError, IndexError) as e:
        raise ValueError(f"Failed to extract text from model response: {e}\nResponse: {response}")

    try:
        parsed_object = json.loads(text_output)
    except json.JSONDecodeError as e:
        # Fallback: if the text doesn't start with JSON, try to extract numbered list items.
        stripped = text_output.lstrip()
        if not stripped or stripped[0] not in ('{', '['):
            items = []
            for line in text_output.splitlines():
                line = line.strip()
                if not line:
                    continue
                # Look for lines starting with a number followed by a dot.
                if line[0].isdigit():
                    parts = line.split('.', 1)
                    if len(parts) > 1:
                        items.append(parts[1].strip())
                    else:
                        items.append(line)
            if items:
                parsed_object = items
            else:
                raise ValueError(f"Failed to parse model response as JSON: {e}\nResponse text: {text_output}")
        else:
            raise ValueError(f"Failed to parse model response as JSON: {e}\nResponse text: {text_output}")

    if schema:
        if hasattr(schema, "parse_obj"):
            # Check if the schema expects a field 'questions' or 'queries'
            if isinstance(parsed_object, list) and ("questions" in schema.__fields__ or "queries" in schema.__fields__):
                key = "questions" if "questions" in schema.__fields__ else "queries"
                if key == "queries":
                    new_list = []
                    for item in parsed_object:
                        if isinstance(item, dict):
                            new_list.append(item)
                        else:
                            new_list.append({"query": item, "researchGoal": ""})
                    parsed_object = schema.parse_obj({key: new_list})
                else:
                    parsed_object = schema.parse_obj({key: parsed_object})
            else:
                parsed_object = schema.parse_obj(parsed_object)
        else:
            parsed_object = schema(parsed_object)

    return {"object": parsed_object, "raw": response}
