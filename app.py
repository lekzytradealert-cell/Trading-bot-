from flask import Flask, request
import telebot
import os

# === CONFIG ===
BOT_TOKEN = os.getenv("BOT_TOKEN", "7964628886:AAG8yIo-777pal9Q98Av8dr0EaqlGso5r6M")
bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

# === BASIC COMMAND ===
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "✅ Lekzy Trade AI bot is active and connected successfully!")

# === WEBHOOK ROUTE ===
@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    if update:
        bot.process_new_updates([telebot.types.Update.de_json(update)])
    return "OK", 200  # ✅ Must return plain text + status 200

# === HOME ROUTE ===
@app.route('/')
def home():
    return "Lekzy Trade AI bot is running fine on Render ✅"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
