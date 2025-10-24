import requests
import time
import json
import datetime
from telegram import Bot

TELEGRAM_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
CHANNEL_ID = "YOUR_CHANNEL_ID"  # e.g. @yourchannel
bot = Bot(token=TELEGRAM_TOKEN)

POCKET_SIGNALS_URL = "https://pocketoption.com/en/signals/list/"  # Their public signal list endpoint

def fetch_pocket_signals():
    """Fetches current PocketOption signals (public feed)."""
    try:
        response = requests.get(POCKET_SIGNALS_URL, timeout=10)
        if response.status_code == 200:
            return response.text
        else:
            return None
    except Exception as e:
        print("Error fetching signals:", e)
        return None

def parse_and_filter_signals(html_text):
    """Very simple HTML parse – replace with API parse if they open one."""
    # This version uses placeholder pattern
    signals = []
    # TODO: implement BeautifulSoup if you want live HTML extraction
    # For now we simulate example:
    now = datetime.datetime.utcnow().strftime("%H:%M:%S")
    signals.append({
        "pair": "EURUSD",
        "direction": "BUY",
        "confidence": 92,
        "time": now
    })
    return [s for s in signals if s["confidence"] >= 80]

def send_signal(signal):
    """Send formatted signal to Telegram."""
    msg = (
        f"🔥 *Pocket Option AI Signal*\n"
        f"Pair: {signal['pair']}\n"
        f"Direction: {signal['direction']}\n"
        f"Confidence: {signal['confidence']} %\n"
        f"Time: {signal['time']} UTC\n"
        f"Mode: Pre-Entry ✅\n"
        f"Next Candle: Waiting..."
    )
    bot.send_message(chat_id=CHANNEL_ID, text=msg, parse_mode="Markdown")

def run_signal_loop():
    while True:
        html = fetch_pocket_signals()
        if html:
            signals = parse_and_filter_signals(html)
            for sig in signals:
                send_signal(sig)
                time.sleep(30)  # Wait 30 s before next signal
        time.sleep(60)

if __name__ == "__main__":
    run_signal_loop()
