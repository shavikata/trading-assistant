from typing import Any

MVP_WATCHLIST: list[dict[str, Any]] = [
    {
        "ticker": "USAR",
        "company_name": None,
        "exchange": None,
        "market_cap": None,
        "currency": "USD",
        "is_active": 1,
    },
    {
        "ticker": "LAC",
        "company_name": None,
        "exchange": None,
        "market_cap": None,
        "currency": "USD",
        "is_active": 1,
    },
    {
        "ticker": "ACHR",
        "company_name": None,
        "exchange": None,
        "market_cap": None,
        "currency": "USD",
        "is_active": 1,
    },
    {
        "ticker": "RKLB",
        "company_name": None,
        "exchange": None,
        "market_cap": None,
        "currency": "USD",
        "is_active": 1,
    },
    {
        "ticker": "JOBY",
        "company_name": None,
        "exchange": None,
        "market_cap": None,
        "currency": "USD",
        "is_active": 1,
    },
]


def get_mvp_watchlist() -> list[dict[str, Any]]:
    return MVP_WATCHLIST