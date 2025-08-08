#!/usr/bin/env python3
"""
Main entry point for the Telegram Mobile Phone Scraper Bot
"""
import os
import logging
from bot.telegram_bot import MobileBot
from config import Config

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Main function to start the bot"""
    try:
        # Initialize configuration
        config = Config()
        
        # Check if bot token is available
        if not config.BOT_TOKEN:
            logger.error("BOT_TOKEN not found in environment variables")
            return
        
        # Initialize and start the bot
        bot = MobileBot(config)
        logger.info("Starting Telegram Mobile Bot...")
        bot.run()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Error starting bot: {e}")

if __name__ == '__main__':
    main()
