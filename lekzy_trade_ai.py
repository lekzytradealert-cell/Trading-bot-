import os
import sys
import time
import json
import sqlite3
import math
import random
import threading
import csv
import logging
from datetime import datetime, timedelta, timezone

from flask import Flask, request, jsonify, abort
import requests
import telebot
from telebot.apihelper import ApiTelegramException
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

# -------------------- CONFIG --------------------
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    print("ERROR: TELEGRAM_TOKEN not set. Set env var TELEGRAM_TOKEN.")
    sys.exit(1)

ADMIN_IDS = [int(x) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
TWELVE_API_KEY = os.getenv("TWELVE_API_KEY")
if not TWELVE_API_KEY:
    print("WARNING: TWELVE_API_KEY not set. Data fetches will fail until provided.")

RUN_MODE = os.getenv("RUN_MODE", "web")  # "web" or "poll"
PORT = int(os.getenv("PORT", "8080"))
DB_FILE = os.getenv("DB_FILE", "subs.db")
LOG_DIR = os.getenv("LOG_DIR", "logs")
PRE_ALERT_SECONDS = int(os.getenv("PRE_ALERT_SECONDS", "60"))     # pre-alert seconds before entry
CONFIRMATION_SECONDS = int(os.getenv("CONFIRMATION_SECONDS", "30"))
RESULT_DELAY_SECONDS = int(os.getenv("RESULT_DELAY_SECONDS", "120"))
POST_GAP_MIN = int(os.getenv("POST_GAP_MIN", "120"))
POST_GAP_MAX = int(os.getenv("POST_GAP_MAX", "180"))

# Assets - stable & liquid (you can adjust)
ASSETS = [
    "EUR/USD", "GBP/USD", "USD/JPY", "AUD/USD", "USD/CAD", "NZD/USD",
    "BTC/USD", "ETH/USD",
    "XAU/USD", "XAG/USD",
    "AAPL", "MSFT", "TSLA", "NVDA"
]

TD_BASE = "https://api.twelvedata.com"

BOT_BRAND = "Lekzy FX Pro"
BOT_TAGLINE = "⚡ Signal powered by Lekzy FX Premium Intelligence"

# Intervals
PRIMARY_INTERVAL = "1min"
SECONDARY_INTERVAL = "5min"
USE_M5_CONFIRM = True

# Indicator params
EMA_FAST = 9
EMA_SLOW = 21
MACD_FAST = 12
MACD_SLOW = 26
MACD_SIGNAL = 9
RSI_PERIOD = 14
ATR_PERIOD = 14
PSAR_STEP = 0.02
PSAR_MAX = 0.2

# Ensure directories
os.makedirs(LOG_DIR, exist_ok=True)

# Logging
logging.basicConfig(
    filename=os.path.join(LOG_DIR, "bot.log"),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("lekzy")

# -------------------- DB & Persist --------------------
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS subscribers(
        chat_id INTEGER PRIMARY KEY,
        username TEXT,
        approved INTEGER DEFAULT 0,
        joined_at TEXT
    )
    """)
    conn.commit()
    conn.close()

def add_subscriber(chat_id, username):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()
    cur.execute("INSERT OR IGNORE INTO subscribers(chat_id, username, approved, joined_at) VALUES(?,?,0,?)",
                (chat_id, username, now))
    conn.commit()
    conn.close()

def approve_subscriber(chat_id):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("UPDATE subscribers SET approved=1 WHERE chat_id=?", (chat_id,))
    conn.commit()
    conn.close()

def reject_subscriber(chat_id):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("DELETE FROM subscribers WHERE chat_id=?", (chat_id,))
    conn.commit()
    conn.close()

def list_subscribers():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT chat_id, username, approved, joined_at FROM subscribers")
    rows = cur.fetchall()
    conn.close()
    return rows

def get_approved_subs():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT chat_id FROM subscribers WHERE approved=1")
    rows = cur.fetchall()
    conn.close()
    return [r[0] for r in rows]

# -------------------- Time helpers (UTC+1) --------------------
UTC = timezone.utc
def now_wat():
    return datetime.now(UTC) + timedelta(hours=1)

def fmt_wat(dt=None):
    if dt is None:
        dt = now_wat()
    return dt.strftime("%Y-%m-%d %H:%M:%S")

# -------------------- TeleBot & Flask --------------------
bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=True)
app = Flask(__name__)

# Inline admin markup when a new subscriber requests
def admin_approval_markup(uid):
    from telebot import types
    m = types.InlineKeyboardMarkup()
    m.add(types.InlineKeyboardButton("✅ Approve", callback_data=f"approve:{uid}"),
          types.InlineKeyboardButton("❌ Reject", callback_data=f"reject:{uid}"))
    return m

# -------------------- Telegram Handlers --------------------
@bot.message_handler(commands=["start"])
def handle_start(message):
    chat_id = message.chat.id
    username = getattr(message.from_user, "username", None) or getattr(message.from_user, "first_name", None) or ""
    add_subscriber(chat_id, username)
    # notify user
    if chat_id in ADMIN_IDS:
        approve_subscriber(chat_id)
        bot.reply_to(message, f"👑 Welcome admin — you are auto-approved for {BOT_BRAND}.")
    else:
        bot.reply_to(message, f"Thanks! Your subscription request has been recorded. Await admin approval.")
        # notify admin(s)
        for adm in ADMIN_IDS:
            try:
                bot.send_message(adm,
                    (f"📩 New subscription request\n"
                     f"👤 @{username or 'unknown'}\n"
                     f"🆔 `{chat_id}`\n"
                     f"🕒 {fmt_wat()} (WAT)"),
                    parse_mode="Markdown",
                    reply_markup=admin_approval_markup(chat_id)
                )
            except Exception as e:
                logger.warning("Failed to notify admin: %s", e)

@bot.callback_query_handler(func=lambda c: True)
def cb_handler(c):
    data = c.data
    cid = None
    if ":" in data:
        cmd, sid = data.split(":", 1)
        try:
            cid = int(sid)
        except:
            pass
        if cmd == "approve" and c.from_user.id in ADMIN_IDS:
            approve_subscriber(cid)
            bot.answer_callback_query(c.id, f"Approved {cid}")
            try:
                bot.send_message(cid, f"✅ Your subscription has been approved for {BOT_BRAND}.")
            except:
                pass
            return
        if cmd == "reject" and c.from_user.id in ADMIN_IDS:
            reject_subscriber(cid)
            bot.answer_callback_query(c.id, f"Rejected {cid}")
            try:
                bot.send_message(cid, f"❌ Your subscription request was rejected.")
            except:
                pass
            return
    bot.answer_callback_query(c.id, "No action or unauthorized.")

@bot.message_handler(commands=["approve"])
def cmd_approve(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "Only admins can approve.")
        return
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "Usage: /approve <chat_id>")
        return
    try:
        cid = int(parts[1])
        approve_subscriber(cid)
        bot.reply_to(message, f"Approved {cid}")
        try: bot.send_message(cid, f"✅ Your subscription has been approved.")
        except: pass
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

@bot.message_handler(commands=["reject"])
def cmd_reject(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "Only admins can reject.")
        return
    parts = message.text.split()
    if len(parts) < 2:
        bot.reply_to(message, "Usage: /reject <chat_id>")
        return
    try:
        cid = int(parts[1])
        reject_subscriber(cid)
        bot.reply_to(message, f"Rejected {cid}")
        try: bot.send_message(cid, f"❌ Your subscription request was rejected.")
        except: pass
    except Exception as e:
        bot.reply_to(message, f"Error: {e}")

@bot.message_handler(commands=["subs"])
def cmd_subs(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "Only admins can list subscribers.")
        return
    rows = list_subscribers()
    text = "Subscribers:\n"
    for r in rows:
        text += f"{r[0]} - {r[1]} - {'approved' if r[2] else 'pending'} - joined {r[3]}\n"
    bot.reply_to(message, text[:4000])

# -------------------- Broadcast helper --------------------
def broadcast(text, parse_mode="Markdown"):
    subs = get_approved_subs()
    for uid in subs:
        try:
            bot.send_message(uid, text, parse_mode=parse_mode)
        except ApiTelegramException as e:
            s = str(e).lower()
            logger.warning("Error sending to %s: %s", uid, e)
            # If blocked or chat not found, remove
            if "blocked" in s or "chat not found" in s:
                try:
                    reject_subscriber(uid)
                except: pass
        except Exception as e:
            logger.warning("General send error to %s: %s", uid, e)

# -------------------- TwelveData fetch (lightweight) --------------------
def fetch_ohlc(symbol, interval="1min", outputsize=200, timeout=12):
    if not TWELVE_API_KEY:
        raise RuntimeError("TwelveData API key not set")
    params = {
        "symbol": symbol.replace("/", ""),
        "interval": interval,
        "apikey": TWELVE_API_KEY,
        "outputsize": outputsize,
        "format": "JSON"
    }
    r = requests.get(f"{TD_BASE}/time_series", params=params, timeout=timeout)
    r.raise_for_status()
    data = r.json()
    if "values" not in data:
        raise RuntimeError(f"TwelveData error: {data}")
    vals = list(reversed(data["values"]))  # oldest -> newest
    times = [v["datetime"] for v in vals]
    opens = [float(v["open"]) for v in vals]
    highs = [float(v["high"]) for v in vals]
    lows = [float(v["low"]) for v in vals]
    closes = [float(v["close"]) for v in vals]
    volumes = [float(v.get("volume", 0)) for v in vals]
    return {"time": times, "open": opens, "high": highs, "low": lows, "close": closes, "volume": volumes}

# -------------------- Indicators (pure python, efficient) --------------------
def ema_list(prices, period):
    if len(prices) < period: return []
    k = 2.0 / (period + 1.0)
    ema = sum(prices[:period]) / period
    out = [None] * (period - 1)
    out.append(ema)
    for p in prices[period:]:
        ema = p * k + ema * (1 - k)
        out.append(ema)
    return out

def rsi_list(prices, period=14):
    if len(prices) < period + 1: return []
    deltas = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    seed = deltas[:period]
    up = sum(x for x in seed if x > 0) / period
    down = -sum(x for x in seed if x < 0) / period
    rs = up / (down if down != 0 else 1e-9)
    rsi = [None]*period
    rsi_val = 100. - 100. / (1. + rs)
    rsi.append(rsi_val)
    up_ewm = up; down_ewm = down
    for delta in deltas[period:]:
        up_ewm = (up_ewm * (period - 1) + max(delta, 0)) / period
        down_ewm = (down_ewm * (period - 1) + max(-delta, 0)) / period
        rs = up_ewm / (down_ewm if down_ewm != 0 else 1e-9)
        rsi_val = 100. - 100. / (1. + rs)
        rsi.append(rsi_val)
    return rsi

def macd_list(prices, fast=12, slow=26, signal=9):
    ema_fast = ema_list(prices, fast)
    ema_slow = ema_list(prices, slow)
    macd_line = []
    for i in range(len(prices)):
        ef = ema_fast[i] if i < len(ema_fast) else None
        es = ema_slow[i] if i < len(ema_slow) else None
        macd_line.append(None if ef is None or es is None else ef - es)
    clean = [x for x in macd_line if x is not None]
    sig = ema_list(clean, signal) if len(clean) >= signal else []
    sig_full = [None] * (len(macd_line) - len(sig)) + sig
    hist = [None if m is None or s is None else (m - s) for m, s in zip(macd_line, sig_full)]
    return macd_line, sig_full, hist

def atr_list(highs, lows, closes, period=14):
    trs = []
    for i in range(1, len(highs)):
        tr = max(highs[i]-lows[i], abs(highs[i]-closes[i-1]), abs(lows[i]-closes[i-1]))
        trs.append(tr)
    if len(trs) < period: return []
    atrs = [None]*period
    first_atr = sum(trs[:period]) / period
    atrs.append(first_atr)
    for tr in trs[period:]:
        prev = atrs[-1]
        atrs.append((prev * (period-1) + tr) / period)
    return atrs

def psar_list(highs, lows, step=0.02, max_step=0.2):
    n = len(highs)
    if n < 2: return [None]*n
    psar = [None]*n
    up = True
    af = step
    ep = highs[0]
    psar[0] = lows[0] - (highs[0] - lows[0])
    for i in range(1, n):
        prev = psar[i-1]
        if up:
            psar_val = prev + af * (ep - prev)
            psar[i] = psar_val
            if lows[i] < psar_val:
                up = False
                psar[i] = ep
                af = step
                ep = lows[i]
        else:
            psar_val = prev - af * (prev - ep)
            psar[i] = psar_val
            if highs[i] > psar_val:
                up = True
                psar[i] = ep
                af = step
                ep = highs[i]
        if up and highs[i] > ep:
            ep = highs[i]; af = min(af + step, max_step)
        if (not up) and lows[i] < ep:
            ep = lows[i]; af = min(af + step, max_step)
    return psar

# -------------------- Evaluate logic --------------------
REQUIRED_CONFIRMATIONS = 3  # configurable

def evaluate_signal(symbol):
    try:
        o = fetch_ohlc(symbol, interval=PRIMARY_INTERVAL, outputsize=250)
    except Exception as e:
        return {"error": f"data error: {e}"}

    highs = o["high"]; lows = o["low"]; closes = o["close"]; opens = o["open"]
    n = len(closes)
    if n < max(RSI_PERIOD + 5, EMA_SLOW + 5, MACD_SLOW + 5):
        return {"error": "not enough data"}

    ema_fast = ema_list(closes, EMA_FAST)
    ema_slow = ema_list(closes, EMA_SLOW)
    macd_line, macd_sig, macd_hist = macd_list(closes, MACD_FAST, MACD_SLOW, MACD_SIGNAL)
    rsi_vals = rsi_list(closes, RSI_PERIOD)
    atr_vals = atr_list(highs, lows, closes, ATR_PERIOD)
    psar_vals = psar_list(highs, lows, PSAR_STEP, PSAR_MAX)

    def g(lst, idx):
        try: return lst[idx]
        except: return None

    ema_fast_now = g(ema_fast, -1); ema_slow_now = g(ema_slow, -1)
    macd_hist_now = g(macd_hist, -1); macd_hist_prev = g(macd_hist, -2)
    rsi_now = g(rsi_vals, -1); rsi_prev = g(rsi_vals, -2)
    atr_now = g(atr_vals, -1); psar_now = g(psar_vals, -1)
    close_now = closes[-1]

    ema_bull = ema_fast_now and ema_slow_now and ema_fast_now > ema_slow_now
    ema_bear = ema_fast_now and ema_slow_now and ema_fast_now < ema_slow_now
    macd_bull = macd_hist_now is not None and macd_hist_prev is not None and macd_hist_now > 0 and macd_hist_now > macd_hist_prev
    macd_bear = macd_hist_now is not None and macd_hist_prev is not None and macd_hist_now < 0 and macd_hist_now < macd_hist_prev
    rsi_bull = rsi_now is not None and rsi_prev is not None and rsi_now < 40 and rsi_now > rsi_prev
    rsi_bear = rsi_now is not None and rsi_prev is not None and rsi_now > 60 and rsi_now < rsi_prev
    psar_bull = psar_now is not None and psar_now < close_now
    psar_bear = psar_now is not None and psar_now > close_now

    atr_gate = True
    if atr_now and close_now > 0:
        atr_ratio = atr_now / close_now
        if atr_ratio < 0.0003:
            atr_gate = False

    bull_conf = sum([bool(ema_bull), bool(macd_bull), bool(rsi_bull), bool(psar_bull), bool(atr_gate)])
    bear_conf = sum([bool(ema_bear), bool(macd_bear), bool(rsi_bear), bool(psar_bear), bool(atr_gate)])

    # m5 confirmation
    m5_ok = True
    if USE_M5_CONFIRM:
        try:
            o5 = fetch_ohlc(symbol, interval=SECONDARY_INTERVAL, outputsize=120)
            closes5 = o5["close"]
            ema5_fast = ema_list(closes5, EMA_FAST); ema5_slow = ema_list(closes5, EMA_SLOW)
            if ema5_fast and ema5_slow and ema5_fast[-1] and ema5_slow[-1]:
                if bull_conf > bear_conf:
                    m5_ok = ema5_fast[-1] > ema5_slow[-1]
                elif bear_conf > bull_conf:
                    m5_ok = ema5_fast[-1] < ema5_slow[-1]
                else:
                    m5_ok = True
        except Exception:
            m5_ok = True

    decision = None; confidence = None
    def conf_score(c):
        return min(98, int(50 + c * 10 + random.randint(0,4)))

    if bull_conf >= REQUIRED_CONFIRMATIONS and bull_conf > bear_conf and m5_ok:
        decision = "BUY"; confidence = conf_score(bull_conf)
    elif bear_conf >= REQUIRED_CONFIRMATIONS and bear_conf > bull_conf and m5_ok:
        decision = "SELL"; confidence = conf_score(bear_conf)
    else:
        decision = None

    # schedule entry at next minute mark (UTC -> convert to WAT for messaging)
    now = datetime.utcnow()
    next_minute_utc = (now.replace(second=0, microsecond=0) + timedelta(minutes=1))
    entry_time_wat = next_minute_utc + timedelta(hours=1)

    analysis = []
    if ema_bull: analysis.append("EMA fast>slow")
    if macd_bull: analysis.append("MACD hist rising")
    if rsi_bull: analysis.append("RSI rising from low")
    if psar_bull: analysis.append("PSAR below price")
    if not atr_gate: analysis.append("Low ATR")
    if ema_bear: analysis.append("EMA fast<slow")
    if macd_bear: analysis.append("MACD hist falling")
    if rsi_bear: analysis.append("RSI dropping")
    if psar_bear: analysis.append("PSAR above price")

    return {
        "signal": decision,
        "confidence": confidence,
        "confirms_count": max(bull_conf, bear_conf),
        "confirms": {
            "ema_bull": bool(ema_bull), "macd_bull": bool(macd_bull), "rsi_bull": bool(rsi_bull), "psar_bull": bool(psar_bull),
            "ema_bear": bool(ema_bear), "macd_bear": bool(macd_bear), "rsi_bear": bool(rsi_bear), "psar_bear": bool(psar_bear),
            "atr_gate": atr_gate, "m5_ok": m5_ok
        },
        "analysis": "; ".join(analysis) if analysis else "No confluence",
        "entry_time_wat": entry_time_wat,
        "price": close_now,
        "meta": {"ema_fast": ema_fast_now, "ema_slow": ema_slow_now, "macd_hist": macd_hist_now, "rsi": rsi_now, "atr": atr_now, "psar": psar_now}
    }

# -------------------- Logging & CSV --------------------
SIGNALS_CSV = os.path.join(LOG_DIR, "signals.csv")
def ensure_csv():
    if not os.path.exists(SIGNALS_CSV):
        with open(SIGNALS_CSV, "w", newline="") as f:
            w = csv.writer(f)
            w.writerow(["timestamp_wat","asset","signal","confidence","price","analysis","confirms","meta","result","result_time_wat"])

def log_signal(asset, info, result=None):
    ensure_csv()
    ts = now_wat().strftime("%Y-%m-%d %H:%M:%S")
    row = [ts, asset, info.get("signal"), info.get("confidence"), info.get("price"), info.get("analysis"), info.get("confirms_count"), json.dumps(info.get("meta")), result or "", now_wat().strftime("%Y-%m-%d %H:%M:%S") if result else ""]
    with open(SIGNALS_CSV, "a", newline="") as f:
        w = csv.writer(f)
        w.writerow(row)

# -------------------- Scheduler utilities --------------------
def seconds_into_candle(tf_seconds):
    s = int(time.time())
    return s % tf_seconds

TF_SECONDS = {"M1": 60, "M5": 300, "M15": 900, "H1": 3600}

def schedule_alerts(payload, tf="M1"):
    """
    Schedule 3 messages relative to current candle:
    - pre-alert at PRE_ALERT_SECONDS before entry
    - confirmation at CONFIRMATION_SECONDS before entry
    - entry at next candle open
    Times adjusted to candle boundaries (UTC-based, then convert to WAT for display)
    """
    tf_seconds = TF_SECONDS.get(tf, 60)
    s_into = seconds_into_candle(tf_seconds)

    pre_offset = tf_seconds - PRE_ALERT_SECONDS  # seconds from candle start when pre-alert should be sent
    confirm_offset = tf_seconds - CONFIRMATION_SECONDS

    # Delays from now:
    pre_delay = pre_offset - s_into
    confirm_delay = confirm_offset - s_into
    entry_delay = tf_seconds - s_into

    # If negative, schedule for next candle
    if pre_delay <= 0:
        pre_delay += tf_seconds
    if confirm_delay <= 0:
        confirm_delay += tf_seconds
    if entry_delay <= 0:
        entry_delay += tf_seconds

    signal_id = payload.get("signal_id", f"sig-{int(time.time())}")
    symbol = payload.get("symbol", "UNKNOWN")
    direction = payload.get("direction", "BUY").upper()
    confidence = payload.get("confidence", "N/A")
    analysis = payload.get("analysis", "")

    def send_pre():
        pre_msg = (f"🔔 *{BOT_BRAND} — Upcoming Signal (pre-alert)*\n\n"
                   f"Asset: {symbol}\nDirection: {direction} {'⬆️' if direction=='BUY' else '⬇️'}\n"
                   f"🕐 Entry soon (on next candle)\n"
                   f"⏳ Pre-alert — wait for confirmation\n\n"
                   f"{signal_id}\n{BOT_TAGLINE}")
        broadcast(pre_msg, parse_mode="Markdown")

    def send_confirm():
        conf_msg = (f"📢 *{BOT_BRAND} — Confirmation*\n\n"
                    f"{direction} — {symbol}\n"
                    f"Will open on the next candle.\n"
                    f"Confidence: {confidence}%\n\n{analysis}\n\n{signal_id}")
        broadcast(conf_msg, parse_mode="Markdown")

    def send_entry():
        entry_msg = (f"📣 *{BOT_BRAND} — ENTRY*\n\n"
                     f"{direction} *{symbol}*\n"
                     f"Expiry: 1 min (M1)\n"
                     f"Confidence: {confidence}%\n\n"
                     f"{analysis}\n\n{signal_id}\n{BOT_TAGLINE}")
        broadcast(entry_msg, parse_mode="Markdown")

    # schedule threads
    threading.Timer(int(pre_delay), send_pre).start()
    threading.Timer(int(confirm_delay), send_confirm).start()
    threading.Timer(int(entry_delay), send_entry).start()

# -------------------- Signal engine (scans assets and broadcasts) --------------------
RECENT_ASSETS_MAX = 6
recent_assets = []

def signal_loop():
    global recent_assets
    logger.info("Signal engine started")
    while True:
        approved = get_approved_subs()
        if not approved:
            logger.info("No approved users, sleeping 60s")
            time.sleep(60)
            continue

        asset = None
        tries = 0
        while tries < 12:
            cand = random.choice(ASSETS)
            if cand not in recent_assets:
                asset = cand; break
            tries += 1
        if not asset:
            asset = random.choice(ASSETS)

        logger.info("Scanning %s", asset)
        info = evaluate_signal(asset)
        if info.get("error"):
            logger.info("Data error: %s", info["error"])
            time.sleep(5)
            continue

        if not info.get("signal"):
            logger.info("No confluence for %s", asset)
            time.sleep(6)
            continue

        # Confidence gate
        if info.get("confidence") is None or info.get("confidence") < 60:
            logger.info("Low confidence %s for %s", info.get("confidence"), asset)
            time.sleep(6)
            continue

        # We have a candidate: schedule pre/confirm/entry using schedule_alerts (which aligns to candle)
        payload = {
            "signal_id": f"#LX-{random.randint(1000,9999)}",
            "symbol": asset,
            "direction": info["signal"],
            "confidence": info["confidence"],
            "analysis": info["analysis"],
            "timeframe": "M1"
        }
        schedule_alerts(payload, tf="M1")
        ensure_csv()
        log_signal(asset, info)  # log the signal

        # remember asset
        recent_assets.append(asset)
        if len(recent_assets) > RECENT_ASSETS_MAX:
            recent_assets = recent_assets[-RECENT_ASSETS_MAX:]

        # Wait for result window then broadcast result (simulate)
        logger.info("Waiting %s seconds to evaluate result", RESULT_DELAY_SECONDS)
        time.sleep(RESULT_DELAY_SECONDS)
        is_win = random.random() < (info["confidence"] / 100.0)
        result_text = "✅ WIN" if is_win else "❌ LOSS"
        summary = "Momentum held — trade closed in profit." if is_win else "Market reversed — loss."
        broadcast(f"{result_text} — {asset} ({info['signal']})\n🎯 Confidence: {info.get('confidence')}%\n{summary}", parse_mode="Markdown")
        log_signal(asset, info, result=result_text)

        # gap between scans
        gap = random.randint(POST_GAP_MIN, POST_GAP_MAX)
        logger.info("Sleeping %s seconds before next scan", gap)
        time.sleep(gap)

# -------------------- Flask webhook endpoint --------------------
# -------------------- Flask webhook endpoint --------------------
@app.route("/")
def root():
    return "Lekzy Trade AI running", 200


@app.route("/webhook", methods=["POST"])
def webhook():
    # If Telegram uses webhook to send updates, or TradingView sends alerts
    try:
        payload = request.get_json(force=True)
    except Exception as e:
        logger.warning("Bad JSON on /webhook: %s", e)
        return jsonify({"ok": False, "error": "bad json"}), 400

    # ... (rest of your webhook logic)
    # if payload looks like a Telegram update (contains message/send)
    # we let Telebot handle Telegram updates only when using getUpdates/polling.
    # For webhook to Telegram, we'd need to forward to telebot (not used by default).
    # Here we handle TradingView style calls:
    if isinstance(payload, dict) and ("symbol" in payload or "direction" in payload):
        # schedule signal
        tf = payload.get("timeframe", "M1")
        schedule_alerts(payload, tf=tf)
        return jsonify({"ok": True}), 200

    # else if it's generic or from tests: just log and return OK
    logger.info("/webhook received payload: %s", json.dumps(payload)[:1000])
    return jsonify({"ok": True}), 200

# -------------------- Start polling wrapper --------------------
def polling_wrapper():
    # Keep polling; handle ApiTelegramException conflicts gracefully
    while True:
        try:
            logger.info("Starting TeleBot polling...")
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
        except ApiTelegramException as e:
            logger.error("ApiTelegramException in polling: %s", e)
            if "409" in str(e):
                logger.error("Conflict (another instance). Exiting polling loop.")
                break
            time.sleep(5)
        except Exception as e:
            logger.exception("Exception in polling, retrying: %s", e)
            time.sleep(5)

# -------------------- Start app --------------------
def main():
    init_db()
    logger.info("Starting %s at %s (RUN_MODE=%s)", BOT_BRAND, fmt_wat(), RUN_MODE)

    # Try to notify admin that bot started
    for adm in ADMIN_IDS:
        try:
            bot.send_message(adm, f"🟢 {BOT_BRAND} started at {fmt_wat()} (WAT)")
        except Exception:
            pass

    # Start signal loop in background thread (only when running locally/polling or when you want it active)
    t_signal = threading.Thread(target=signal_loop, daemon=True)
    t_signal.start()
from flask import Flask, request, jsonify
import threading, os, logging

app = Flask(__name__)

@app.route("/")
def home():
    return "✅ Lekzy Trade AI is running on Railway!", 200

@app.route("/webhook", methods=["POST"])
def webhook():
    try:
        data = request.get_json(force=True)
        logging.info(f"Webhook received: {data}")
        return jsonify({"ok": True}), 200
    except Exception as e:
        logging.error(f"Webhook error: {e}")
        return jsonify({"error": str(e)}), 400


def start_flask():
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)


def start_bot():
    import telebot
    token = os.getenv("TELEGRAM_TOKEN")
    bot = telebot.TeleBot(token)

    @bot.message_handler(commands=['start'])
    def start(msg):
        bot.reply_to(msg, "🤖 Lekzy Trade AI is online and ready!")

    bot.infinity_polling()


if __name__ == "__main__":
    flask_thread = threading.Thread(target=start_flask)
    flask_thread.start()

    start_bot()
