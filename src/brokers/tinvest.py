from datetime import datetime
from tinkoff.invest import Client
from tinkoff.invest.constants import INVEST_GRPC_API, INVEST_GRPC_API_SANDBOX

from ..config import settings


def get_historic_prices(figi: str, start: datetime, end: datetime):
    target = INVEST_GRPC_API if settings.tinvest_env == "prod" else INVEST_GRPC_API_SANDBOX
    with Client(settings.tinvest_token.get_secret_value(), target=target) as client:
        candles = client.get_all_candles(figi=figi, from_=start, to=end)
    return candles
