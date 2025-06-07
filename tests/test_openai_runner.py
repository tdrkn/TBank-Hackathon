import pytest
from unittest.mock import AsyncMock, patch

from src.llm.openai_runner import extract_json, NewsDigest


@pytest.mark.asyncio
async def test_extract_json_retry(monkeypatch):
    bad_resp = AsyncMock()
    bad_resp.choices = [
        type("obj", (), {"message": type("m", (), {"function_call": type("f", (), {"arguments": "{"})})})
    ]
    good_resp = AsyncMock()
    good_resp.choices = [
        type(
            "obj",
            (),
            {
                "message": type(
                    "m",
                    (),
                    {
                        "function_call": type(
                            "f",
                            (),
                            {
                                "arguments": '{"ticker":"GAZP","summary":"ok","sentiment":0.5}',
                            },
                        )
                    },
                )
            },
        )
    ]

    with patch("openai.ChatCompletion.acreate", new=AsyncMock(side_effect=[bad_resp, good_resp])):
        result = await extract_json("text")
        assert isinstance(result, NewsDigest)
        assert result.ticker == "GAZP"
