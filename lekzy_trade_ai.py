import os
import telebot
from flask import Flask, request
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
if not BOT_TOKEN:
    print("❌ BOT_TOKEN not set. Please add it as an environment variable.")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# --- Telegram Handlers ---
@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "🚀 Lekzy Trading Bot is online and ready!")

@bot.message_handler(func=lambda message: True)
def echo_all(message):
    bot.reply_to(message, f"📩 You said: {message.text}")

# --- Flask route for Telegram webhook ---
@app.route("/webhook", methods=["POST"])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        update = request.get_data().decode('utf-8')
        bot.process_new_updates([telebot.types.Update.de_json(update)])
        return "OK", 200
    else:
        return "Unsupported Media Type", 415

# --- Run app ---
if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    print(f"🚀 Starting Flask server on port {port}")
    app.run(host="0.0.0.0", port=port)
