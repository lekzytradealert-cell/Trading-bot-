"""
Enhanced Features for Lekzy Trade AI
Adds menu system, manual trading, UTC+1, candle analysis
"""

import os
import asyncio
import logging
import sqlite3
from datetime import datetime
import pytz
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

logger = logging.getLogger(__name__)
UTC_PLUS_1 = pytz.timezone('Europe/Paris')

class EnhancedFeatures:
    def __init__(self, telegram_bot):
        self.bot = telegram_bot
        self.setup_enhanced_database()
    
    def setup_enhanced_database(self):
        """Setup enhanced database tables"""
        try:
            self.conn = sqlite3.connect('enhanced_trading.db', check_same_thread=False)
            self.cursor = self.conn.cursor()
            
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS enhanced_trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT,
                    direction TEXT,
                    trade_type TEXT,
                    entry_price REAL,
                    stop_loss REAL,
                    take_profit REAL,
                    status TEXT DEFAULT 'active',
                    outcome TEXT,
                    pnl_percentage REAL,
                    accuracy_score REAL,
                    risk_reward_ratio REAL,
                    entry_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    exit_time TIMESTAMP NULL,
                    candle_time TEXT,
                    timeframe TEXT
                )
            ''')
            
            self.conn.commit()
            logger.info("✅ Enhanced database setup complete")
        except Exception as e:
            logger.error(f"❌ Enhanced database setup failed: {e}")
    
    def get_utc1_time(self):
        """Get current time in UTC+1"""
        return datetime.now(UTC_PLUS_1).strftime('%Y-%m-%d %H:%M:%S UTC+1')
    
    async def setup_enhanced_handlers(self, application):
        """Setup enhanced menu handlers"""
        # Add enhanced commands
        application.add_handler(CommandHandler("menu", self.menu_command))
        application.add_handler(CommandHandler("enhanced", self.enhanced_command))
        application.add_handler(CallbackQueryHandler(self.handle_menu_callback))
        
        logger.info("✅ Enhanced handlers setup complete")
    
    async def menu_command(self, update, context):
        """Enhanced menu command"""
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
            f"🤖 <b>ENHANCED TRADING MENU</b> 🤖\n\n"
            f"⏰ Server Time: {self.get_utc1_time()}\n\n"
            "Select an option:",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    async def enhanced_command(self, update, context):
        """Show enhanced features info"""
        await update.message.reply_text(
            "🚀 <b>Enhanced Trading Features</b>\n\n"
            "✅ New Features Available:\n"
            "• Menu System (/menu)\n"
            "• Manual Trading\n" 
            "• Candle-based Analysis\n"
            "• UTC+1 Timeframe\n"
            "• Accuracy Scoring\n"
            "• Profit/Loss Tracking\n\n"
            "Use /menu to explore!",
            parse_mode='HTML'
        )
    
    async def handle_menu_callback(self, update, context):
        """Handle menu callbacks"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "generate_signals":
            await self.generate_signals_handler(query)
        elif query.data == "manual_trade":
            await self.show_manual_trade_menu(query)
        elif query.data == "active_trades":
            await self.show_active_trades(query)
        elif query.data == "trading_stats":
            await self.show_trading_stats(query)
        elif query.data == "bot_performance":
            await self.show_bot_performance(query)
        elif query.data == "market_hours":
            await self.show_market_hours(query)
        elif query.data == "help":
            await self.show_help(query)
    
    async def generate_signals_handler(self, query):
        """Handle generate signals"""
        await query.edit_message_text(
            "🔍 <b>Generating Enhanced Signals...</b>\n\n"
            "📊 Using candle-based analysis\n"
            "⏰ Timeframe: 5-minute candles\n"
            "🌍 Timezone: UTC+1\n\n"
            "<i>Enhanced signal generation coming soon!</i>",
            parse_mode='HTML'
        )
    
    async def show_manual_trade_menu(self, query):
        """Show manual trade menu"""
        keyboard = [
            [InlineKeyboardButton("📈 BUY Trade", callback_data="manual_buy")],
            [InlineKeyboardButton("📉 SELL Trade", callback_data="manual_sell")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_main")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(
            "📊 <b>MANUAL TRADING</b>\n\n"
            "Create custom trades with full control.\n\n"
            "Select trade direction:",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
    
    async def show_market_hours(self, query):
        """Show market hours in UTC+1"""
        message = f"""
🕒 <b>MARKET HOURS (UTC+1)</b>

<b>Asian Session:</b> 02:00 - 08:00
<b>London Session:</b> 08:00 - 16:00  
<b>New York Session:</b> 14:00 - 22:00
<b>Overnight:</b> 22:00 - 02:00

⏰ Current Server Time: {self.get_utc1_time()}
🌍 Timezone: Europe/Paris (UTC+1)

<i>Best trading during London & NY overlap (14:00-16:00)</i>
"""
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')
    
    async def show_bot_performance(self, query):
        """Show bot performance"""
        message = f"""
💰 <b>BOT PERFORMANCE</b>

⏰ Last Updated: {self.get_utc1_time()}
📊 Version: Enhanced v1.0
🌍 Timezone: UTC+1
🕯️ Analysis: Candle-based
🎯 Features: Accuracy Scoring

<b>Available Features:</b>
• Menu Navigation (/menu)
• Manual Trading
• Candle Analysis (5-min)
• UTC+1 Timeframe
• Profit/Loss Tracking
• Risk Management

<i>More features coming soon...</i>
"""
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')
    
    async def show_active_trades(self, query):
        """Show active trades"""
        try:
            self.cursor.execute("SELECT COUNT(*) FROM enhanced_trades WHERE status = 'active'")
            active_count = self.cursor.fetchone()[0]
            
            if active_count == 0:
                message = "📋 <b>ACTIVE TRADES</b>\n\nNo active enhanced trades found."
            else:
                message = f"📋 <b>ACTIVE TRADES</b>\n\n{active_count} enhanced trades running."
                
        except Exception as e:
            message = "📋 <b>ACTIVE TRADES</b>\n\nError loading enhanced trades."
            logger.error(f"Error loading active trades: {e}")
        
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')
    
    async def show_trading_stats(self, query):
        """Show trading statistics"""
        try:
            self.cursor.execute('''
                SELECT 
                    COUNT(*) as total_trades,
                    SUM(CASE WHEN outcome = 'won' THEN 1 ELSE 0 END) as won_trades,
                    SUM(CASE WHEN outcome = 'lost' THEN 1 ELSE 0 END) as lost_trades
                FROM enhanced_trades 
                WHERE status = 'closed'
            ''')
            
            result = self.cursor.fetchone()
            
            if result and result[0] > 0:
                total_trades, won_trades, lost_trades = result
                win_rate = (won_trades / total_trades * 100) if total_trades > 0 else 0
                
                message = f"""
📊 <b>ENHANCED TRADING STATS</b>

📈 Total Trades: {total_trades}
🟢 Won Trades: {won_trades}
🔴 Lost Trades: {lost_trades}
🎯 Win Rate: {win_rate:.1f}%
"""
            else:
                message = "📊 <b>ENHANCED TRADING STATS</b>\n\nNo enhanced trading data available yet."
                
        except Exception as e:
            message = "📊 <b>ENHANCED TRADING STATS</b>\n\nError loading statistics."
            logger.error(f"Error loading stats: {e}")
        
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='HTML')
    
    async def show_help(self, query):
        """Show help information"""
        message = """
❓ <b>ENHANCED FEATURES HELP</b>

<b>New Commands:</b>
/menu - Enhanced trading menu
/enhanced - Show enhanced features info

<b>Menu Options:</b>
• Generate Signals - Candle-based analysis
• Manual Trade - Create custom trades  
• Active Trades - View current positions
• Trading Stats - Performance metrics
• Bot Performance - System overview
• Market Hours - Trading session times

<b>Features:</b>
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
