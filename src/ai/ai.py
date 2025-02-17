import json
from typing import Any, Callable, Optional, Dict

def generate_object(
    *,
    model: Callable[..., Dict[str, Any]],
    prompt: str,
    system: Optional[str] = None,
    schema: Optional[Any] = None,
    **kwargs,
) -> Dict[str, Any]:
    """
    Generates a structured object from a given prompt using the provided language model.

    Parameters:
      - model: A callable that takes a prompt (plus any additional kwargs) and returns a dict.
               It must include a "text" key in its response, where the text is a JSON string.
      - prompt: The user prompt to send to the model.
      - system: An optional system prompt to prefix the user prompt.
      - schema: An optional Pydantic model (or callable) to validate/transform the parsed JSON output.
      - kwargs: Additional keyword arguments to pass along to the model call.

    Returns:
      A dictionary with:
        - "object": The parsed (and optionally validated) structured object.
        - "raw": The raw response from the model.
    """
    final_prompt = f"{system}\n{prompt}" if system else prompt
    response = model(final_prompt, **kwargs)

    text_output = response.get("text", "")
    try:
        parsed_object = json.loads(text_output)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse model response as JSON: {e}\nResponse text: {text_output}")

    if schema:
        # If the schema is a Pydantic model, use its parse_obj method.
        if hasattr(schema, "parse_obj"):
            parsed_object = schema.parse_obj(parsed_object)
        else:
            parsed_object = schema(parsed_object)

    return {"object": parsed_object, "raw": response}
