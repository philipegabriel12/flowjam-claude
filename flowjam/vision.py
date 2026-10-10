"""Read hours, project and date off a Clockify screenshot with Claude."""
import base64
import json

import anthropic

PROMPT = """This is a Clockify screenshot. List every time entry visible.
Return ONLY JSON: {"entries": [{"project": str, "date": "YYYY-MM-DD", "duration": "H:MM:SS"}]}
Use the entry's own date (or its day group header). If a value is unreadable, use null."""


def extract_entries(client: anthropic.Anthropic, model: str, image: bytes, media_type: str) -> list[dict]:
    msg = client.messages.create(
        model=model,
        max_tokens=1024,
        messages=[{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": media_type,
                                         "data": base64.b64encode(image).decode()}},
            {"type": "text", "text": PROMPT},
        ]}],
    )
    text = "".join(b.text for b in msg.content if b.type == "text")
    text = text[text.find("{"): text.rfind("}") + 1]
    return json.loads(text)["entries"]
