import json


def sse_event(event_type: str, **fields) -> str:
    """Build a single Server-Sent-Events frame.

    Centralizing this avoids the awkward inline f-string + json.dumps
    formatting that was repeated ~10 times in the original router, and
    `default=str` is applied uniformly so trace/datetime objects never
    crash the stream.
    """
    payload = {"type": event_type, **fields}
    return f"data: {json.dumps(payload, default=str)}\n\n"
