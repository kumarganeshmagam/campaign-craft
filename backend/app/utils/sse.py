import json

def format_sse(data: dict) -> str:
    # Simple SSE formatter that sends JSON data
    payload = json.dumps(data, default=str)
    return f"data: {payload}\n\n"
