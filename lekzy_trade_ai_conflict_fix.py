#!/usr/bin/env python3
"""
Lekzy Trade AI - Conflict Fix Version
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

from flask import Flask, request, jsonify, abort
import requests
import telebot
from telebot import types

# ONLY use environment variable
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
if not TELEGRAM_TOKEN:
    print("❌ ERROR: TELEGRAM_TOKEN not set in environment")
    sys.exit(1)

print(f"✅ Using token: {TELEGRAM_TOKEN[:10]}...")

# Initialize bot with conflict handling
bot = telebot.TeleBot(TELEGRAM_TOKEN, threaded=True)
app = Flask(__name__)

# UTC+1 timezone
UTC_PLUS_1 = pytz.timezone('Europe/Paris')

def get_utc1_time():
    return datetime.now(UTC_PLUS_1).strftime('%Y-%m-%d %H:%M:%S UTC+1')

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
        f"🌍 Timezone: UTC+1\n\n"
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

<i>Best trading during London & NY overlap (14:00-16:00)</i>
"""
    bot.send_message(msg.chat.id, hours_text, parse_mode='HTML')

# Handle enhanced callbacks
@bot.callback_query_handler(func=lambda call: call.data.startswith('enhanced_'))
def handle_enhanced_callback(call):
    if call.data == "enhanced_signals":
        bot.answer_callback_query(call.id, "🔍 Generating enhanced signals...")
        bot.send_message(call.message.chat.id, "📊 <b>Enhanced Signal Generation</b>\n\nUsing candle-based analysis with UTC+1 timeframe.", parse_mode='HTML')
    
    elif call.data == "enhanced_manual":
        bot.answer_callback_query(call.id, "📈 Manual trading selected")
        bot.send_message(call.message.chat.id, "📈 <b>Manual Trading</b>\n\nCreate custom trades with full risk management.", parse_mode='HTML')
    
    elif call.data == "enhanced_stats":
        bot.answer_callback_query(call.id, "📊 Loading statistics...")
        bot.send_message(call.message.chat.id, f"💰 <b>Trading Statistics</b>\n\n⏰ Last Updated: {get_utc1_time()}\n🌍 Timezone: UTC+1", parse_mode='HTML')
    
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
    return "Lekzy Trade AI Enhanced is running!"

@app.route('/health')
def health():
    return jsonify({"status": "ok", "time": format_time(now_utc())})

def admin_approval_markup(uid):
    markup = types.InlineKeyboardMarkup()
    btn_approve = types.InlineKeyboardButton("✅ Approve", callback_data=f"approve_{uid}")
    btn_reject = types.InlineKeyboardButton("❌ Reject", callback_data=f"reject_{uid}")
    markup.add(btn_approve, btn_reject)
    return markup

@bot.message_handler(commands=['start'])
def start(msg):
    bot.reply_to(msg, 
        "🚀 Lekzy Trade AI Enhanced is online!\n\n"
        "New enhanced commands:\n"
        "• /menu - Enhanced trading menu\n"
        "• /hours - Market hours (UTC+1)\n\n"
        "All original features still available!"
    )

# Your existing callback handler
@bot.callback_query_handler(func=lambda call: not call.data.startswith('enhanced_'))
def handle_callback(call):
    # Your existing callback handling
    pass

def start_bot():
    try:
        print("🤖 Starting Telegram bot with conflict handling...")
        # Add small delay and retry logic for conflicts
        time.sleep(5)
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
    except Exception as e:
        print(f"❌ Bot failed: {e}")
        print("💡 This might be a conflict with another running instance")
        print("💡 Waiting 30 seconds and retrying...")
        time.sleep(30)
        start_bot()  # Retry

def start_flask(port=8080):
    print(f"🌐 Starting Flask app on port {port}...")
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    
    print("🔄 Starting services with conflict handling...")
    
    # Start bot in background thread
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    bot_thread.start()
    
    print("✅ Both services started!")
    print("   Bot commands: /start, /menu, /hours")
    print("   Web server: http://0.0.0.0:" + str(port))
    
    # Start Flask app (main thread)
    start_flask(port)
