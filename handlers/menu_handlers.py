from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, CommandHandler, CallbackQueryHandler, MessageHandler, filters
import logging
import sqlite3
from datetime import datetime
import pytz

logger = logging.getLogger(__name__)
UTC_PLUS_1 = pytz.timezone('Europe/Paris')

def get_utc1_time():
    return datetime.now(UTC_PLUS_1).strftime('%Y-%m-%d %H:%M:%S UTC+1')

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user = update.effective_user
    
    keyboard = [
        [InlineKeyboardButton("📊 Generate Signals", callback_data="generate_signals")],
        [InlineKeyboardButton("📈 Manual Trade", callback_data="manual_trade")],
        [InlineKeyboardButton("📋 Active Trades", callback_data="active_trades")],
        [InlineKeyboardButton("📊 Trading Stats", callback_data="trading_stats")],
        [InlineKeyboardButton("💰 Bot Performance", callback_data="bot_performance")],
        [InlineKeyboardButton("🕒 Market Hours", callback_data="market_hours")],
        [InlineKeyboardButton("❓ Help", callback_data="help")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"🤖 <b>ENHANCED TRADING BOT</b> 🤖\n\n"
        f"👋 Welcome {user.first_name}!\n"
        f"⏰ Server Time: {get_utc1_time()}\n\n"
        "Select an option from the menu below:",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

async def menu_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /menu command"""
    await start_command(update, context)

async def handle_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle menu callbacks"""
    query = update.callback_query
    await query.answer()
    
    if query.data == "generate_signals":
        await generate_signals_handler(query)
    elif query.data == "manual_trade":
        await show_manual_trade_menu(query)
    elif query.data == "active_trades":
        await show_active_trades(query)
    elif query.data == "trading_stats":
        await show_trading_stats(query)
    elif query.data == "bot_performance":
        await show_bot_performance(query)
    elif query.data == "market_hours":
        await show_market_hours(query)
    elif query.data == "help":
        await show_help(query)
    elif query.data == "back_main":
        await start_command(update, context)
    else:
        await query.edit_message_text("⚙️ Feature coming soon...")

async def generate_signals_handler(query):
    """Handle generate signals"""
    await query.edit_message_text(
        "🔍 <b>Generating Trading Signals...</b>\n\n"
        "📊 Analyzing markets with candle-based analysis...\n"
        "⏰ Timeframe: 5-minute candles\n"
        "🌍 Timezone: UTC+1\n\n"
        "<i>This feature will be fully implemented in the next update.</i>",
        parse_mode='HTML'
    )

async def show_manual_trade_menu(query):
    """Show manual trade menu"""
    keyboard = [
        [InlineKeyboardButton("📈 BUY Trade", callback_data="manual_buy")],
        [InlineKeyboardButton("📉 SELL Trade", callback_data="manual_sell")],
        [InlineKeyboardButton("🔙 Back to Main", callback_data="back_main")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(
        "📊 <b>MANUAL TRADING</b>\n\n"
        "Create custom trades with full control:\n"
        "• Set entry price\n• Stop loss\n• Take profit\n• Risk management\n\n"
        "Select trade direction:",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )

async def show_active_trades(query):
    """Show active trades"""
    try:
        conn = sqlite3.connect('enhanced_trading.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM enhanced_trades WHERE status = 'active'")
        active_count = cursor.fetchone()[0]
        conn.close()
        
        if active_count == 0:
            message = "📋 <b>ACTIVE TRADES</b>\n\nNo active trades found."
        else:
            message = f"📋 <b>ACTIVE TRADES</b>\n\n{active_count} active trades running."
        
    except Exception as e:
        message = "📋 <b>ACTIVE TRADES</b>\n\nError loading trades."
        logger.error(f"Error loading active trades: {e}")
    
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def show_trading_stats(query):
    """Show trading statistics"""
    try:
        conn = sqlite3.connect('enhanced_trading.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT 
                COUNT(*) as total_trades,
                SUM(CASE WHEN outcome = 'won' THEN 1 ELSE 0 END) as won_trades,
                SUM(CASE WHEN outcome = 'lost' THEN 1 ELSE 0 END) as lost_trades,
                SUM(pnl_percentage) as total_pnl
            FROM enhanced_trades 
            WHERE status = 'closed'
        ''')
        
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0] > 0:
            total_trades, won_trades, lost_trades, total_pnl = result
            win_rate = (won_trades / total_trades * 100) if total_trades > 0 else 0
            
            message = f"""
📊 <b>TRADING STATISTICS</b>

📈 Total Trades: {total_trades}
🟢 Won Trades: {won_trades}
🔴 Lost Trades: {lost_trades}
🎯 Win Rate: {win_rate:.1f}%
💰 Total PnL: {total_pnl or 0:+.2f}%
"""
        else:
            message = "📊 <b>TRADING STATISTICS</b>\n\nNo trading data available yet."
            
    except Exception as e:
        message = "📊 <b>TRADING STATISTICS</b>\n\nError loading statistics."
        logger.error(f"Error loading stats: {e}")
    
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def show_bot_performance(query):
    """Show bot performance"""
    message = f"""
💰 <b>BOT PERFORMANCE</b>

⏰ Last Updated: {get_utc1_time()}
📊 Version: Enhanced v1.0
🌍 Timezone: UTC+1
🕯️ Analysis: Candle-based
🎯 Features: Accuracy Scoring

<b>Available Features:</b>
• Menu Navigation
• Manual Trading
• Candle Analysis (5-min)
• UTC+1 Timeframe
• Profit/Loss Tracking
• Risk Management

<i>Advanced features coming in next update...</i>
"""
    
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def show_market_hours(query):
    """Show market hours in UTC+1"""
    message = """
🕒 <b>MARKET HOURS (UTC+1)</b>

<b>Asian Session:</b> 02:00 - 08:00
<b>London Session:</b> 08:00 - 16:00  
<b>New York Session:</b> 14:00 - 22:00
<b>Overnight:</b> 22:00 - 02:00

⏰ All times in Europe/Paris (UTC+1)
🌍 Current Server Time: {get_utc1_time()}

<i>Best trading during London & NY overlap (14:00-16:00)</i>
"""
    
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

async def show_help(query):
    """Show help information"""
    message = """
❓ <b>HELP & COMMANDS</b>

<b>Main Commands:</b>
/start or /menu - Show main menu

<b>Menu Options:</b>
• 📊 Generate Signals - Automated trading signals
• 📈 Manual Trade - Create custom trades  
• 📋 Active Trades - View current positions
• 📊 Trading Stats - Performance metrics
• 💰 Bot Performance - System overview
• 🕒 Market Hours - Trading session times

<b>New Features:</b>
• Candle-based analysis
• UTC+1 timeframe
• Accuracy scoring
• Profit/loss tracking
• Risk management

<b>Timezone:</b> Europe/Paris (UTC+1)
"""
    
    keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')

def setup_handlers(application):
    """Setup all handlers"""
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("menu", menu_command))
    application.add_handler(CallbackQueryHandler(handle_menu_callback))
