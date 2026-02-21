from __future__ import annotations
import os
from dataclasses import dataclass

def _bool(name: str, default: bool) -> bool:
    raw = (os.getenv(name) or ("true" if default else "false")).strip().lower()
    return raw in {"1", "true", "yes", "on", "y"}
def _int(name: str, default: int) -> int:
    raw = (os.getenv(name) or str(default)).strip()
    try:
        return int(raw)
    except Exception:
        return default

@dataclass
class Settings:
    PUBG_NICK_LOOKUP_URL_TEMPLATE: str | None = None
    PUBG_NICK_LOOKUP_URLS: str = ""
    PUBG_NICK_LOOKUP_METHOD: str = "GET"
    PUBG_NICK_LOOKUP_API_KEY: str | None = None
    PUBG_NICK_LOOKUP_APPID: str = "1450015065"
    PUBG_NICK_LOOKUP_TIMEOUT_SECONDS: int = 3
    PUBG_NICK_LOOKUP_USER_AGENT: str = "Mozilla/5.0 BedaBot/1.0"
    PUBG_NICK_STATIC_MAP: str = ""
    PUBG_NICK_BROWSER_FALLBACK: bool = True
    PUBG_NICK_BROWSER_URL: str = "https://www.midasbuy.com/midasbuy/de/buy/pubgm"
    PUBG_NICK_BROWSER_URLS: str = ""
    PUBG_NICK_BROWSER_TIMEOUT_SECONDS: int = 6

settings = Settings(
    PUBG_NICK_LOOKUP_URL_TEMPLATE=(os.getenv("PUBG_NICK_LOOKUP_URL_TEMPLATE") or "").strip() or None,
    PUBG_NICK_LOOKUP_URLS=(os.getenv("PUBG_NICK_LOOKUP_URLS") or "").strip(),
    PUBG_NICK_LOOKUP_METHOD=(os.getenv("PUBG_NICK_LOOKUP_METHOD") or "GET").strip(),
    PUBG_NICK_LOOKUP_API_KEY=(os.getenv("PUBG_NICK_LOOKUP_API_KEY") or "").strip() or None,
    PUBG_NICK_LOOKUP_APPID=(os.getenv("PUBG_NICK_LOOKUP_APPID") or "1450015065").strip(),
    PUBG_NICK_LOOKUP_TIMEOUT_SECONDS=_int("PUBG_NICK_LOOKUP_TIMEOUT_SECONDS", 3),
    PUBG_NICK_LOOKUP_USER_AGENT=(os.getenv("PUBG_NICK_LOOKUP_USER_AGENT") or "Mozilla/5.0 BedaBot/1.0").strip(),
    PUBG_NICK_STATIC_MAP=(os.getenv("PUBG_NICK_STATIC_MAP") or "").strip(),
    PUBG_NICK_BROWSER_FALLBACK=_bool("PUBG_NICK_BROWSER_FALLBACK", True),
    PUBG_NICK_BROWSER_URL=(os.getenv("PUBG_NICK_BROWSER_URL") or "https://www.midasbuy.com/midasbuy/de/buy/pubgm").strip(),
    PUBG_NICK_BROWSER_URLS=(os.getenv("PUBG_NICK_BROWSER_URLS") or "").strip(),
    PUBG_NICK_BROWSER_TIMEOUT_SECONDS=_int("PUBG_NICK_BROWSER_TIMEOUT_SECONDS", 6),
)
