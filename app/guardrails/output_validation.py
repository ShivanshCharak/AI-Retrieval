from .llm_guard import guard


def validate_output(answer: str):

    prompt = f"""
Task: Check if there is unsafe content in the AI assistant's response
according to the safety policy.

<BEGIN ASSISTANT RESPONSE>
{answer}
<END ASSISTANT RESPONSE>

Return exactly one of:
SAFE
UNSAFE
"""

    response = guard.invoke(prompt)

    verdict = response.content.strip().lower()

    is_safe = verdict.startswith("safe")

    print("OUTPUT VALIDATOR:", verdict)

    return {
        "is_safe": is_safe,
        "raw": response.content,
    }
