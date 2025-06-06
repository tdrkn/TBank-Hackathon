from __future__ import annotations

import google.generativeai as genai

from ..config import settings


genai.configure(api_key=settings.gemini_api_key.get_secret_value())


async def tldr(text: str) -> str:
    model = genai.GenerativeModel("gemini-pro")
    resp = await model.generate_content_async(text + "\nКоротко опиши суть новости")
    return resp.text
