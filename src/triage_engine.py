# triage_engine.py (The Brain)
# This only handles the AI logic.

from openai import OpenAI
import json
from src.config import OPENAI_API_KEY, SYSTEM_PROMPT # Added 'src.' prefix

class TriageEngine:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def analyze(self, message):
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": message}
                ],
                response_format={ "type": "json_object" }
            )
            return json.loads(response.choices[0].message.content)
        except:
            # Our "Hackathon Fallback"
            sev = 5 if "bleed" in message.lower() else 3
            return {"severity": sev, "injured": "unknown"}