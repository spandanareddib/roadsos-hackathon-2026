# triage_engine.py (The Brain)
# This only handles the AI logic.

import json
import logging

from openai import OpenAI
from src.config import OPENAI_API_KEY, SYSTEM_PROMPT

logger = logging.getLogger(__name__)

# Appended to the dispatcher prompt so the model returns machine-readable JSON.
EXTRACTION_INSTRUCTIONS = """

OUTPUT FORMAT FOR THIS ANALYSIS STEP
Return ONLY a valid JSON object, with no other text, using these keys:
{"severity": <integer 1-5, using the severity scoring rules above>,
 "injured": <integer, or "unknown">,
 "hazards": [<short strings>],
 "vehicles": "<description, or unknown>"}
"""

# Keyword fallback (used only if the LLM call fails)
CRITICAL_WORDS = ("bleed", "unconscious", "not breathing", "trapped", "fire", "fuel")


class TriageEngine:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def analyze(self, message):
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT + EXTRACTION_INSTRUCTIONS},
                    {"role": "user", "content": message},
                ],
                response_format={"type": "json_object"},
                temperature=0,
            )
            data = json.loads(response.choices[0].message.content)
            data["severity"] = max(1, min(5, int(data["severity"])))
            data.setdefault("injured", "unknown")
            return data
        except Exception:
            logger.exception("LLM triage failed; using keyword fallback")
            text = message.lower()
            sev = 5 if any(word in text for word in CRITICAL_WORDS) else 3
            return {"severity": sev, "injured": "unknown"}