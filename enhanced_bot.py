#!/usr/bin/env python3
"""
Enhanced Trading Bot - Main Entry Point
With Menu System, Manual Trading, UTC+1, and Candle Analysis
"""

import os
import asyncio
import logging
import sys
from datetime import datetime
import pytz
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.trading_core import TradingSignalBot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('enhanced_bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class EnhancedTradingBot:
    def __init__(self):
        self.bot = None
        self.utc_plus_one = pytz.timezone('Europe/Paris')
        
    async def initialize(self):
        """Initialize the trading bot"""
        try:
            logger.info("🚀 Initializing Enhanced Trading Bot...")
            
            # Check for required environment variables
            if not os.getenv('TELEGRAM_TOKEN'):
                logger.error("❌ TELEGRAM_TOKEN not found in environment")
                return False
            
            # Initialize core trading bot
            self.bot = TradingSignalBot()
            
            if await self.bot.initialize():
                logger.info("✅ Enhanced Trading Bot initialized successfully!")
                return True
            else:
                logger.error("❌ Failed to initialize trading core")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize bot: {e}")
            return False
    
    async def start_services(self):
        """Start all bot services"""
        try:
            logger.info("🔄 Starting bot services...")
            
            # Start Telegram bot
            await self.bot.start_telegram_bot()
            
            # Start scheduled tasks
            await self.bot.start_scheduler()
            
            # Send startup message
            await self.bot.send_startup_message()
            
            logger.info("✅ All services started successfully!")
            
            # Keep the bot running
            while True:
                await asyncio.sleep(3600)
                
        except Exception as e:
            logger.error(f"❌ Error in services: {e}")
            raise
    
    async def shutdown(self):
        """Graceful shutdown"""
        logger.info("🛑 Shutting down Enhanced Trading Bot...")
        if self.bot:
            await self.bot.shutdown()

async def main():
    """Main function"""
    print("🤖 Starting Enhanced Trading Bot...")
    bot = EnhancedTradingBot()
    
    try:
        if await bot.initialize():
            await bot.start_services()
        else:
            logger.error("❌ Failed to initialize bot")
            
    except KeyboardInterrupt:
        logger.info("⏹️ Bot stopped by user")
    except Exception as e:
        logger.error(f"💥 Bot crashed: {e}")
    finally:
        await bot.shutdown()

if __name__ == "__main__":
    # Run the bot
    asyncio.run(main())
