from __future__ import annotations
import asyncio
import json
import typing as t
from urllib.parse import unquote
from settings import settings
_BAD_NICK_VALUES = {"none", "null", "nil", "n/a", "-", "unknown"}
def _normalize_nick(raw: t.Any) -> str | None:
    nick = str(raw or "").strip()
    if not nick:
        return None
    if nick.casefold() in _BAD_NICK_VALUES:
        return None
    return nick
def _browser_urls_from_settings() -> list[str]:
    out: list[str] = []
    raw_urls = (settings.PUBG_NICK_BROWSER_URLS or "").strip()
    if raw_urls:
        for item in raw_urls.split(","):
            u = item.strip()
            if u:
                out.append(u)
    one = (settings.PUBG_NICK_BROWSER_URL or "").strip()
    if one:
        out.append(one)
    return out or ["https://www.midasbuy.com/midasbuy/us/buy/pubgm"]
def _static_nick_from_settings(pubg_id: str) -> str | None:
    raw = (settings.PUBG_NICK_STATIC_MAP or "").strip()
    if not raw:
        return None
    for part in raw.split(","):
        item = part.strip()
        if not item or ":" not in item:
            continue
        key, value = item.split(":", 1)
        if key.strip() == pubg_id:
            return _normalize_nick(value)
    return None
class MidasbuyParser:
    def __init__(self, user_id: int):
        self.user_id = user_id
        self._nickname: str | None = None
    async def _lookup_via_browser(self) -> str | None:
        if not bool(settings.PUBG_NICK_BROWSER_FALLBACK):
            return None
        try:
            from playwright.async_api import async_playwright
        except Exception:
            return None
        timeout = max(6, int(settings.PUBG_NICK_BROWSER_TIMEOUT_SECONDS or 10))
        urls = _browser_urls_from_settings()
        for url in urls:
            try:
                async with async_playwright() as p:
                    browser = await p.chromium.launch(headless=True, args=["--no-sandbox"])
                    context = await browser.new_context(
                        viewport={"width": 390, "height": 844},
                        user_agent=(
                            "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) "
                            "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 "
                            "Mobile/15E148 Safari/604.1"
                        ),
                        is_mobile=True,
                        has_touch=True,
                        device_scale_factor=3,
                    )
                    page = await context.new_page()
                    try:
                        await page.goto(url, wait_until="domcontentloaded", timeout=timeout * 1000)
                        await page.wait_for_timeout(1800)
                        input_selectors = (
                            "input[placeholder='Enter Player ID']",
                            "input[placeholder='Spieler-ID eingeben']",
                            "input[placeholder='Введите ID игрока']",
                            "input[type='text'][maxlength='30']",
                        )
                        target = None
                        for sel in input_selectors:
                            loc = page.locator(sel)
                            if await loc.count() > 0:
                                target = loc.first
                                break
                        if target is None:
                            await context.close()
                            await browser.close()
                            continue
                        await target.scroll_into_view_if_needed()
                        await target.fill(str(self.user_id))
                        response = None
                        for _ in range(2):
                            try:
                                async with page.expect_response(
                                    lambda r: "/interface/getCharac" in r.url and r.request.method == "POST",
                                    timeout=timeout * 1000,
                                ) as resp_info:
                                    await page.keyboard.press("Enter")
                                response = await resp_info.value
                                break
                            except Exception:
                                await page.wait_for_timeout(700)
                        if response is None:
                            await context.close()
                            await browser.close()
                            continue
                        raw = await response.text()
                        data = json.loads(raw)
                        nick = _normalize_nick(unquote(((data.get("info") or {}).get("charac_name") or "")))
                        await context.close()
                        await browser.close()
                        if nick:
                            return nick
                    except Exception:
                        try:
                            await context.close()
                        except Exception:
                            pass
                        try:
                            await browser.close()
                        except Exception:
                            pass
                        continue
            except Exception:
                continue
        return None
    async def fetch_user_info(self) -> dict[str, t.Any]:
        static_nick = _static_nick_from_settings(str(self.user_id))
        if static_nick:
            self._nickname = static_nick
            return {"id": self.user_id, "nickname": self._nickname}
        browser_nick = await self._lookup_via_browser()
        if browser_nick:
            self._nickname = browser_nick
            return {"id": self.user_id, "nickname": self._nickname}
        return {"id": None, "nickname": None}
    @property
    def nick_name(self) -> str | None:
        return _normalize_nick(self._nickname)

async def resolve_pubg_nick_via_jollymax(pubg_id: str, *, timeout_seconds: int = 8) -> str | None:
    digits = "".join(ch for ch in (pubg_id or "") if ch.isdigit())
    if len(digits) < 6:
        return None
    try:
        uid = int(digits)
    except ValueError:
        return None
    parser = MidasbuyParser(uid)
    browser_timeout = max(6, int(settings.PUBG_NICK_BROWSER_TIMEOUT_SECONDS or 10))
    timeout = max(10, int(timeout_seconds), browser_timeout + 10)
    try:
        await asyncio.wait_for(parser.fetch_user_info(), timeout=timeout)
        return parser.nick_name
    except Exception:
        return None
