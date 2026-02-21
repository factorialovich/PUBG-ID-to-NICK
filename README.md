![AIDE+ Pro](https://socialify.git.ci/factorialovich/PUBG-ID-to-NICK/image?description=1&font=KoHo&forks=1&issues=1&logo=https%3A%2F%2Fraw.githubusercontent.com%2Ffactorialovich%2FPUBG-ID-to-NICK%2Fmain%2Fassets%2Ficon.png&name=1&owner=1&pattern=Circuit+Board&pulls=1&stargazers=1&theme=Auto)

> [!IMPORTANT]
> Parsing does not try to disrupt the work in any way Midasbuy, provided for development purposes only.

# PUBG ID to NICK Parser

Telegram bot for retrieving a PUBG Mobile player nickname using their Player ID.

---

## Features

- `/id <PUBG_ID>` — human-readable response
- `/api <PUBG_ID>` or `/parse <PUBG_ID>` — structured JSON response
- Deep-link support via `/start api_<PUBG_ID>`
- Automatic browser fallback via Playwright (Midasbuy) when direct lookup fails

## Testing bot:
- https://t.me/pubgmidtonickbot

---

## Requirements

- Python 3.10+
- Linux server / VPS
- Telegram Bot Token

---

## Environment Variables

### Required

| Variable | Description |
|--------|------|
| `BOT_TOKEN` | Telegram bot token |

### Core Settings

| Variable | Default | Description |
|-------|------|------|
| `PUBG_NICK_TIMEOUT_SECONDS` | 20 | Total nickname resolve timeout |
| `PUBG_NICK_BROWSER_FALLBACK` | true | Enable Playwright fallback |
| `PUBG_NICK_BROWSER_TIMEOUT_SECONDS` | 6 | Browser step timeout |
| `PUBG_NICK_BROWSER_URL` | — | Primary Midasbuy URL |
| `PUBG_NICK_BROWSER_URLS` | — | Comma-separated fallback URLs |
| `PUBG_NICK_STATIC_MAP` | — | Static mappings (`123456789:Nick`) |

### Optional Lookup (reserved)

- `PUBG_NICK_LOOKUP_URL_TEMPLATE`
- `PUBG_NICK_LOOKUP_URLS`
- `PUBG_NICK_LOOKUP_METHOD`
- `PUBG_NICK_LOOKUP_API_KEY`
- `PUBG_NICK_LOOKUP_APPID`
- `PUBG_NICK_LOOKUP_TIMEOUT_SECONDS`
- `PUBG_NICK_LOOKUP_USER_AGENT`

---

## Bot Commands

| Command | Description |
|------|------|
| `/start` | Help message |
| `/id 1234567890` | Human-readable result |
| `/api 1234567890` | JSON response |
| `/parse 1234567890` | Alias for `/api` |

---

## API Response

### Success

```json
{
  "ok": true,
  "pubg_id": "1234567890",
  "nickname": "PlayerName",
  "elapsed_ms": 1240,
  "timestamp_utc": "2026-01-01T10:10:20.000000+00:00"
}
```

### Error

```json
{
  "ok": false,
  "error": "invalid_pubg_id",
  "hint": "use /api <PUBG_ID>"
}
```
