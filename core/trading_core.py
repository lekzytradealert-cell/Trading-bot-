import os
import asyncio
import logging
import sqlite3
from datetime import datetime
import pytz
from telegram import Bot
from telegram.ext import Application

logger = logging.getLogger(__name__)

class TradingSignalBot:
    def __init__(self):
        self.bot_token = os.getenv('TELEGRAM_TOKEN')
        if not self.bot_token:
            # Fallback to your current token
            self.bot_token = "8411003379:AAEgw9b3eE943a0G5eMAC9zNKnAJPD6qGJ4"
        
        self.utc_plus_one = pytz.timezone('Europe/Paris')
        self.bot = None
        self.application = None
        
        # Your existing assets
        self.assets = [
            "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD",
            "BTCUSD", "ETHUSD", "XRPUSD", "LTCUSD", "BCHUSD", 
            "GOLD", "SILVER", "OIL", "NATGAS", "SPX500"
        ]
        
    async def initialize(self):
        """Initialize the bot"""
        try:
            logger.info("🔧 Initializing Trading Core...")
            
            # Initialize Telegram bot
            self.bot = Bot(token=self.bot_token)
            self.application = Application.builder().token(self.bot_token).build()
            
            # Setup database
            await self.setup_database()
            
            # Add handlers
            await self.setup_handlers()
            
            logger.info("✅ Trading core initialized")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize trading core: {e}")
            return False
    
    async def setup_database(self):
        """Setup enhanced database"""
        try:
            self.conn = sqlite3.connect('enhanced_trading.db', check_same_thread=False)
            self.cursor = self.conn.cursor()
            
            # Create enhanced tables
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
            
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS bot_stats (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    total_trades INTEGER DEFAULT 0,
                    won_trades INTEGER DEFAULT 0,
                    lost_trades INTEGER DEFAULT 0,
                    total_profit REAL DEFAULT 0,
                    accuracy_rate REAL DEFAULT 0,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            self.conn.commit()
            logger.info("✅ Enhanced database setup complete")
            
        except Exception as e:
            logger.error(f"❌ Database setup failed: {e}")
    
    async def setup_handlers(self):
        """Setup Telegram handlers"""
        try:
            from handlers.menu_handlers import setup_handlers
            setup_handlers(self.application)
            logger.info("✅ Handlers setup complete")
        except Exception as e:
            logger.error(f"❌ Handler setup failed: {e}")
    
    async def start_telegram_bot(self):
        """Start Telegram bot"""
        try:
            logger.info("🤖 Starting Telegram bot...")
            await self.application.initialize()
            await self.application.start()
            await self.application.updater.start_polling()
            logger.info("✅ Telegram bot started")
        except Exception as e:
            logger.error(f"❌ Telegram bot failed: {e}")
            raise
    
    async def start_scheduler(self):
        """Start scheduled tasks"""
        logger.info("⏰ Scheduler placeholder - will be implemented")
        # We'll add the actual scheduling later
    
    async def send_startup_message(self):
        """Send startup message to admin"""
        try:
            # Try to get admin from your existing users database
            admin_id = await self.get_admin_id()
            if admin_id:
                await self.bot.send_message(
                    chat_id=admin_id,
                    text="🚀 Enhanced Trading Bot Started!\n\n"
                         "✅ New Features:\n"
                         "• Menu System\n• Manual Trading\n• Candle Analysis\n"
                         "• UTC+1 Timeframe\n• Accuracy Scoring\n"
                         "Use /menu to explore!"
                )
                logger.info(f"✅ Startup message sent to admin {admin_id}")
        except Exception as e:
            logger.warning(f"⚠️ Could not send startup message: {e}")
    
    async def get_admin_id(self):
        """Get admin ID from existing database"""
        try:
            # Check your existing users database
            if os.path.exists('users.json'):
                import json
                with open('users.json', 'r') as f:
                    users = json.load(f)
                    for user_id, user_data in users.items():
                        if user_data.get('role') == 'admin':
                            return int(user_id)
            
            # Check subs.db
            if os.path.exists('subs.db'):
                conn = sqlite3.connect('subs.db')
                cursor = conn.cursor()
                cursor.execute("SELECT user_id FROM users WHERE role = 'admin' LIMIT 1")
                result = cursor.fetchone()
                conn.close()
                if result:
                    return result[0]
                    
        except Exception as e:
            logger.error(f"❌ Error getting admin ID: {e}")
        
        return None
    
    async def shutdown(self):
        """Shutdown bot"""
        try:
            if self.application:
                await self.application.stop()
                await self.application.shutdown()
            if hasattr(self, 'conn'):
                self.conn.close()
            logger.info("✅ Bot shutdown complete")
        except Exception as e:
            logger.error(f"❌ Error during shutdown: {e}")
