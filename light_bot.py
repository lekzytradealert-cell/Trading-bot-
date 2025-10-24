import time
import random
from datetime import datetime
import telebot  # pip install pyTelegramBotAPI

# === TELEGRAM CONFIGURATION ===
TELEGRAM_TOKEN = "8358721170:AAGOG7151_fNYEtiNXaXCrd3r01bx3nkCDY"
CHAT_ID = "6307001401"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

def send_trade_signal():
    # --- Asset pools ---
    forex_pairs = ["EURUSD", "USDJPY", "GBPUSD", "AUDUSD", "USDCAD", "NZDUSD"]
    crypto_pairs = ["BTCUSD", "ETHUSD", "BCHUSD", "XRPUSD", "LTCUSD", "DOGEUSD"]
    commodities = ["GOLD", "SILVER", "CRUDEOIL", "NATGAS"]
    stocks = ["AAPL", "TSLA", "AMZN", "MSFT", "GOOGL", "META", "NFLX", "NVDA"]

    all_assets = forex_pairs + crypto_pairs + commodities + stocks

    # --- Performance counters ---
    total_signals = 0
    total_wins = 0
    total_losses = 0

    while True:
        signal_id = f"#LX-{random.randint(1000, 9999)}"
        asset = random.choice(all_assets)
        direction = random.choice(["BUY", "SELL"])
        arrow = "⬆️" if direction == "BUY" else "⬇️"
        confidence = random.randint(70, 95)
        payout = random.randint(75, 90)

        # Step 1: Pre-entry alert
        entry_time = datetime.now().strftime("%H:%M")
        pre_signal = (
            f"🕐 Entry Time: {entry_time} (UTC +1)\n"
            f"Asset: {asset}\n"
            f"Expiration: 1 min [M1]\n\n"
            f"⏰ Entry soon... Wait for confirmation in 30s.\n\n"
            f"{signal_id}"
        )
        bot.send_message(CHAT_ID, pre_signal)
        time.sleep(random.randint(25, 35))

        # Step 2: Random analysis
        analysis_options = [
            "RSI shows potential reversal zone 🔄",
            "EMA crossover indicates strong momentum 💪",
            "Resistance level tested multiple times 📊",
            "MACD divergence detected ⚡️",
            "Strong volume spike before price action 🚀",
            "Support level showing buying pressure 🧱",
            "Candlestick pattern confirms reversal 🕯️",
            "Volatility rising, market preparing for move 🔥",
            "Price rejected key psychological level 💹",
            "Moving averages aligning with trend 📈"
        ]
        analysis = random.choice(analysis_options)

        # Step 3: Final signal
        final_signal = (
            f"📊 *Lekzy FX — RSI Bot v9.7 Pro*\n\n"
            f"{arrow} *{direction} — {asset}*\n"
            f"🎯 Expiration: 1 min [M1]\n"
            f"📈 Confidence: {confidence}%\n"
            f"💰 Payout: {payout}%\n\n"
            f"🔍 Analysis: {analysis}\n\n"
            f"{signal_id}\n"
            f"⚡️ Signal powered by Lekzy FX Premium Intelligence"
        )
        bot.send_message(CHAT_ID, final_signal, parse_mode="Markdown")

        # Step 4: Wait for result
        time.sleep(90)
        win_chance = confidence / 100
        is_win = random.random() < win_chance
        result = "✅ WIN" if is_win else "❌ LOSS"

        win_summaries = [
            "Strong momentum confirmed — trade closed in profit 💰",
            "Signal performed perfectly — smooth entry and exit ✅",
            "Price respected trend — solid win 📈",
            "Resistance break validated the move — great call 🔥",
            "Technical confluence supported the win 🎯",
        ]
        loss_summaries = [
            "Market reversed unexpectedly — trade lost ❌",
            "Volatility spike hit stop — tough loss ⚠️",
            "False breakout occurred — loss recorded 📉",
            "Unexpected candle reversal — not in our favor 😔",
            "News volatility affected the trade — loss ❌",
        ]
        summary = random.choice(win_summaries if is_win else loss_summaries)

        result_message = (
            f"{result} — {asset} ({direction})\n"
            f"🎯 Confidence: {confidence}% | 💰 Payout: {payout}%\n"
            f"{summary}\n\n"
            f"{signal_id}"
        )
        bot.send_message(CHAT_ID, result_message)

        # --- Update performance counters ---
        total_signals += 1
        if is_win:
            total_wins += 1
        else:
            total_losses += 1

        # Step 5: Show session summary every 10 trades
        if total_signals % 10 == 0:
            accuracy = round((total_wins / total_signals) * 100)
            motivation = random.choice([
                "Keep pushing — consistency is key 💪",
                "Great work! Focus on process, not just results ⚡️",
                "Discipline turns losses into lessons 📘",
                "Trading is patience + precision 🎯",
                "Stay focused — markets reward calm minds 🧘‍♂️"
            ])
            session_summary = (
                f"📊 *Session Performance Summary*\n\n"
                f"Total Signals: {total_signals}\n"
                f"✅ Wins: {total_wins}\n"
                f"❌ Losses: {total_losses}\n"
                f"📈 Accuracy: {accuracy}%\n\n"
                f"{motivation}\n\n"
                f"⚡️ Powered by Lekzy FX Premium Intelligence"
            )
            bot.send_message(CHAT_ID, session_summary, parse_mode="Markdown")
            total_signals = 0
            total_wins = 0
            total_losses = 0

        # Step 6: Wait 4–8 minutes before next signal
        time.sleep(random.randint(240, 480))

# === RUN BOT ===
if __name__ == "__main__":
    print("🚀 Lekzy FX Bot is now running...")
    send_trade_signal()
