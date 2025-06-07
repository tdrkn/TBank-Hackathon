from __future__ import annotations


import openai
from guardrails import Guard
from guardrails.classes.validation_outcome import ValidationOutcome
from pydantic import BaseModel
from typing import Optional

from ..config import settings

NEWS_SCHEMA = {
    "name": "news_digest",
    "parameters": {
        "type": "object",
        "properties": {
            "ticker": {"type": "string"},
            "headline": {"type": "string"},
            "summary": {"type": "string", "maxLength": 400},
            "sentiment": {"type": "number", "minimum": -1, "maximum": 1},
            "impact": {"type": "string", "enum": ["low", "medium", "high"]},
            "event_type": {
                "type": "string",
                "enum": ["earnings", "dividends", "macro", "regulation", "other"],
            },
        },
        "required": ["ticker", "summary", "sentiment"],
    },
}


class NewsDigest(BaseModel):
    ticker: str
    headline: Optional[str] = None
    summary: str
    sentiment: float
    impact: Optional[str] = None
    event_type: Optional[str] = None


guard = Guard.from_pydantic(NewsDigest)


async def extract_json(text: str) -> NewsDigest:
    prompt = (
        "Ты – финансовый аналитик. Извлеки ключевые данные и верни JSON строго по схеме."
    )
    for _ in range(2):
        response = await openai.ChatCompletion.acreate(
            model="gpt-4o-mini",
            temperature=0,
            messages=[{"role": "system", "content": prompt}, {"role": "user", "content": text}],
            functions=[NEWS_SCHEMA],
            function_call={"name": "news_digest"},
            api_key=settings.openai_api_key.get_secret_value(),
        )
        arguments = response.choices[0].message.function_call.arguments
        try:
            result = guard.parse(arguments)
            if isinstance(result, ValidationOutcome):
                return NewsDigest(**result.validated_output)
            return result
        except Exception:
            prompt = (
                "Ответ не соответствует схеме. Пожалуйста, верни JSON строго по схеме."
            )
    raise ValueError("Failed to parse OpenAI response")
