from __future__ import annotations
import asyncio
import json
import html
import logging
import os
import re
import time
from pathlib import Path
from datetime import datetime, timezone
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import Message
from dotenv import load_dotenv
from parser import resolve_pubg_nick_via_jollymax
load_dotenv()

BOT_TOKEN = (os.getenv("BOT_TOKEN") or "").strip()
PUBG_NICK_TIMEOUT_SECONDS = int(os.getenv("PUBG_NICK_TIMEOUT_SECONDS") or "20")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
log = logging.getLogger("pubgmid-bot")
dp = Dispatcher()
CUSTOM_EMOJI_FILE = Path(__file__).with_name("custom.json")

def _load_custom_emoji_map() -> dict[str, str]:
    try:
        raw = json.loads(CUSTOM_EMOJI_FILE.read_text(encoding="utf-8"))
    except Exception:
        return {}
    if not isinstance(raw, dict):
        return {}
    out: dict[str, str] = {}
    for key, value in raw.items():
        k = str(key).strip().lower()
        v = str(value).strip()
        if k:
            out[k] = v
    return out

CUSTOM_EMOJI = _load_custom_emoji_map()

def _emoji(name: str, fallback: str) -> str:
    emoji_id = (CUSTOM_EMOJI.get(name.lower()) or "").strip()
    if emoji_id.isdigit():
        return f'<tg-emoji emoji-id="{emoji_id}">{html.escape(fallback)}</tg-emoji>'
    return html.escape(fallback)
def _extract_pubg_id(text: str) -> str | None:
    digits = "".join(ch for ch in (text or "") if ch.isdigit())
    if len(digits) < 6:
        return None
    return digits
def _api_payload(pubg_id: str, nick: str | None, elapsed: float) -> dict:
    return {
        "ok": bool(nick),
        "pubg_id": pubg_id,
        "nickname": nick,
        "elapsed_ms": int(elapsed * 1000),
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
def _api_pretty_text(payload: dict) -> str:
    raw = json.dumps(payload, ensure_ascii=False, indent=2)
    return f"<pre>{html.escape(raw)}</pre>"

@dp.message(Command("start"))
async def start_cmd(msg: Message) -> None:
    raw = re.sub(r"^/start(@\w+)?", "", (msg.text or "")).strip()
    if raw.startswith("api_"):
        pubg_id = _extract_pubg_id(raw[4:])
        if pubg_id:
            started = time.perf_counter()
            nick = await resolve_pubg_nick_via_jollymax(pubg_id, timeout_seconds=PUBG_NICK_TIMEOUT_SECONDS)
            elapsed = time.perf_counter() - started
            await msg.answer(_api_pretty_text(_api_payload(pubg_id, nick, elapsed)), parse_mode="HTML")
            return
    await msg.answer("Send your PUBG ID and I will check the nickname.\n\nUser mode: <code>/id 1234567890</code>\nAPI mode: <code>/api 1234567890</code>", parse_mode="HTML",)

@dp.message(Command("id"))
async def id_cmd(msg: Message) -> None:
    raw = re.sub(r"^/id(@\w+)?", "", (msg.text or "")).strip()
    pubg_id = _extract_pubg_id(raw)
    if not pubg_id:
        await msg.answer("Invalid format. Example: <code>/id 1234567890</code>", parse_mode="HTML")
        return
    started = time.perf_counter()
    wait = await msg.answer(f"Checking <code>{pubg_id}</code>...", parse_mode="HTML")
    nick = await resolve_pubg_nick_via_jollymax(pubg_id, timeout_seconds=PUBG_NICK_TIMEOUT_SECONDS)
    elapsed = time.perf_counter() - started
    if nick:
        text = (
            f"<blockquote>{_emoji('info', '💎')} Information</blockquote>\n"
            f"{_emoji('success', '✅')} ID: <code>{pubg_id}</code>\n"
            f"{_emoji('nick', '⭐')} Nick: <code>{html.escape(nick)}</code>\n"
            f"<blockquote>{_emoji('time', '⏱')} Parse time: <code>{elapsed:.2f}s</code></blockquote>"
        )
    else:
        text = (
            f"<blockquote>{_emoji('info', '💎')} Information</blockquote>\n"
            f"{_emoji('warning', '⚠️')} ID: <code>{pubg_id}</code>\n"
            "Nickname not found automatically. Please check if you entered your ID correctly.\n"
            f"<blockquote>{_emoji('time', '⏱')} Parse time: <code>{elapsed:.2f}s</code></blockquote>"
        )
    try:
        await wait.edit_text(text, parse_mode="HTML")
    except Exception:
        await msg.answer(text, parse_mode="HTML")

@dp.message(Command("api"))
@dp.message(Command("parse"))
async def api_cmd(msg: Message) -> None:
    raw = re.sub(r"^/(api|parse)(@\w+)?", "", (msg.text or "")).strip()
    pubg_id = _extract_pubg_id(raw)
    if not pubg_id:
        err = {"ok": False, "error": "invalid_pubg_id", "hint": "use /api <PUBG_ID>"}
        await msg.answer(_api_pretty_text(err), parse_mode="HTML")
        return
    started = time.perf_counter()
    wait = await msg.answer(f"Checking API <code>{pubg_id}</code>...", parse_mode="HTML")
    nick = await resolve_pubg_nick_via_jollymax(pubg_id, timeout_seconds=PUBG_NICK_TIMEOUT_SECONDS)
    elapsed = time.perf_counter() - started
    text = _api_pretty_text(_api_payload(pubg_id, nick, elapsed))
    try:
        await wait.edit_text(text, parse_mode="HTML")
    except Exception:
        await msg.answer(text, parse_mode="HTML")

@dp.message()
async def any_text(msg: Message) -> None:
    pubg_id = _extract_pubg_id(msg.text or "")
    if not pubg_id:
        await msg.answer("Send PUBG ID digits only or use /api <PUBG_ID>.", parse_mode="HTML")
        return
    await id_cmd(msg)

async def main() -> None:
    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    me = await bot.get_me()
    log.info("Started as @%s", me.username)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
