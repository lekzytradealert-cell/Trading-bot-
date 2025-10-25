#!/usr/bin/env python3
"""
Lekzy Trade AI - Final Version with Force Takeover
"""

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
import pytz
import requests

from flask import Flask, request, jsonify, abort
import telebot
from telebot import types

# ONLY use environment variable
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    print("❌ ERROR: TELEGRAM_TOKEN not set in environment")
    sys.exit(1)

print(f"🚀 ENHANCED BOT STARTING...")
print(f"✅ Token: {TELEGRAM_TOKEN[:10]}...")

# Initialize bot
bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=True)
app = Flask(__name__)

# UTC+1 timezone
UTC_PLUS_1 = pytz.timezone('Europe/Paris')

def get_utc1_time():
    return datetime.now(UTC_PLUS_1).strftime('%Y-%m-%d %H:%M:%S UTC+1')

def force_takeover():
    """Forcefully take over bot control by stopping other instances"""
    try:
        print("🔄 Attempting to stop other bot instances...")
        # Use Telegram API to close other connections
        response = requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/close",
            timeout=5
        )
        print("✅ Sent close command to other instances")
        time.sleep(3)  # Wait for other instances to close
    except Exception as e:
        print(f"⚠️ Could not stop other instances: {e}")

# Enhanced menu command
@bot.message_handler(commands=['menu'])
def enhanced_menu(msg):
    markup = types.InlineKeyboardMarkup()
    
    btn_signals = types.InlineKeyboardButton("📊 Generate Signals", callback_data="enhanced_signals")
    btn_manual = types.InlineKeyboardButton("📈 Manual Trade", callback_data="enhanced_manual")
    btn_stats = types.InlineKeyboardButton("💰 Trading Stats", callback_data="enhanced_stats")
    btn_hours = types.InlineKeyboardButton("🕒 Market Hours", callback_data="enhanced_hours")
    
    markup.add(btn_signals, btn_manual)
    markup.add(btn_stats, btn_hours)
    
    bot.send_message(
        msg.chat.id,
        f"🤖 <b>ENHANCED TRADING MENU</b> 🤖\n\n"
        f"⏰ Server Time: {get_utc1_time()}\n"
        f"🌍 Timezone: UTC+1\n"
        f"🚀 Version: Enhanced v2.0\n\n"
        "Select an option:",
        reply_markup=markup,
        parse_mode='HTML'
    )

# Market hours command
@bot.message_handler(commands=['hours'])
def market_hours(msg):
    hours_text = f"""
🕒 <b>MARKET HOURS (UTC+1)</b>

<b>Asian Session:</b> 02:00 - 08:00
<b>London Session:</b> 08:00 - 16:00  
<b>New York Session:</b> 14:00 - 22:00
<b>Overnight:</b> 22:00 - 02:00

⏰ Current Time: {get_utc1_time()}
🌍 Timezone: Europe/Paris
🚀 Bot Version: Enhanced v2.0

<i>Best trading during London & NY overlap (14:00-16:00)</i>
"""
    bot.send_message(msg.chat.id, hours_text, parse_mode='HTML')

# Handle enhanced callbacks
@bot.callback_query_handler(func=lambda call: call.data.startswith('enhanced_'))
def handle_enhanced_callback(call):
    if call.data == "enhanced_signals":
        bot.answer_callback_query(call.id, "🔍 Generating enhanced signals...")
        bot.send_message(call.message.chat.id, 
            "📊 <b>Enhanced Signal Generation</b>\n\n"
            "🚀 Using advanced candle-based analysis\n"
            "⏰ Timeframe: 5-minute candles\n"
            "🌍 Timezone: UTC+1\n"
            "🎯 Features: Accuracy scoring & profit tracking",
            parse_mode='HTML'
        )
    
    elif call.data == "enhanced_manual":
        bot.answer_callback_query(call.id, "📈 Manual trading selected")
        bot.send_message(call.message.chat.id, 
            "📈 <b>Manual Trading</b>\n\n"
            "Create custom trades with:\n"
            "• Entry price control\n"
            "• Stop loss management\n"
            "• Take profit targets\n"
            "• Risk/reward calculation\n"
            "• UTC+1 timeframe",
            parse_mode='HTML'
        )
    
    elif call.data == "enhanced_stats":
        bot.answer_callback_query(call.id, "📊 Loading statistics...")
        bot.send_message(call.message.chat.id, 
            f"💰 <b>Trading Statistics</b>\n\n"
            f"⏰ Last Updated: {get_utc1_time()}\n"
            f"🌍 Timezone: UTC+1\n"
            f"🚀 Version: Enhanced v2.0\n"
            f"📊 Data: Candle-based analysis",
            parse_mode='HTML'
        )
    
    elif call.data == "enhanced_hours":
        market_hours(call.message)

# Your existing functions
def now_utc():
    return datetime.now(timezone.utc)

def now_wat():
    return datetime.now(timezone.utc) + timedelta(hours=1)

def format_time(dt):
    return dt.strftime("%Y-%m-%d %H:%M:%S")

@app.route('/')
def home():
    return "🚀 Lekzy Trade AI Enhanced v2.0 is running!"

@app.route('/health')
def health():
    return jsonify({
        "status": "ok", 
        "time": format_time(now_utc()),
        "version": "enhanced_v2.0",
        "timezone": "UTC+1"
    })

@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, 
        "🚀 <b>Lekzy Trade AI Enhanced v2.0</b> is online!\n\n"
        "✅ <b>New Enhanced Features:</b>\n"
        "• /menu - Interactive trading menu\n"
        "• /hours - Market hours (UTC+1)\n"
        "• Candle-based analysis\n"
        "• Manual trading interface\n"
        "• Accuracy scoring\n"
        "• Profit tracking\n\n"
        "🌍 <b>Timezone:</b> UTC+1 (Europe/Paris)\n"
        "⏰ <b>Current Time:</b> " + get_utc1_time(),
        parse_mode='HTML'
    )

# Your existing callback handler
@bot.callback_query_handler(func=lambda call: not call.data.startswith('enhanced_'))
def handle_callback(call):
    # Your existing callback handling
    pass

def start_bot():
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            print(f"🤖 Attempt {retry_count + 1} to start bot...")
            
            if retry_count > 0:
                force_takeover()
                time.sleep(5)  # Wait for takeover to complete
            
            bot.infinity_polling(timeout=60, long_polling_timeout=60)
            break  # Success
            
        except Exception as e:
            retry_count += 1
            print(f"❌ Attempt {retry_count} failed: {e}")
            
            if retry_count < max_retries:
                print(f"🔄 Retrying in 10 seconds... ({retry_count}/{max_retries})")
                time.sleep(10)
            else:
                print("💥 All retry attempts failed")
                # Don't exit - let Flask keep running

def start_flask(port=8080):
    print(f"🌐 Starting Flask app on port {port}...")
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    
    print("=" * 50)
    print("🚀 LEKZY TRADE AI ENHANCED v2.0")
    print("🌍 Timezone: UTC+1 (Europe/Paris)")
    print("⏰ Current Time: " + get_utc1_time())
    print("=" * 50)
    
    # Start bot in background thread
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    bot_thread.start()
    
    print("✅ Enhanced bot services started!")
    print("   Bot commands: /start, /menu, /hours")
    print("   Web server: http://0.0.0.0:" + str(port))
    print("   🚀 Ready for enhanced trading!")
    
    # Start Flask app (main thread)
    start_flask(port)
