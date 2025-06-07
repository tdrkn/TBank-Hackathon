"""Helper utilities to analyse portfolio using Tinkoff Invest API."""
from __future__ import annotations

from collections import defaultdict
from typing import Dict

from tinkoff_invest import ProductionSession, SandboxSession

from ..config import settings


def fetch_portfolio_value(account_id: str, sandbox: bool = False) -> Dict[str, float]:
    """Return portfolio valuation grouped by currency.

    Parameters
    ----------
    account_id: str
        Identifier of the brokerage account.
    sandbox: bool, optional
        Use sandbox environment instead of production.

    Returns
    -------
    dict
        Mapping from currency code to total value of positions and free funds.
    """
    session_cls = SandboxSession if sandbox else ProductionSession
    with session_cls(settings.tinvest_token.get_secret_value()) as session:
        portfolio = session.get_portfolio()

    totals: Dict[str, float] = defaultdict(float)
    for cur in portfolio.currencies:
        totals[cur.name.value] += cur.balance.value
    for pos in portfolio.positions:
        price = pos.average_price
        totals[price.currency.value] += pos.balance * price.value
    return dict(totals)


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="Show portfolio value")
    parser.add_argument("account", help="Account identifier")
    parser.add_argument("--sandbox", action="store_true", help="Use sandbox mode")
    args = parser.parse_args()

    data = fetch_portfolio_value(args.account, args.sandbox)
    print(json.dumps(data, indent=2, ensure_ascii=False))
