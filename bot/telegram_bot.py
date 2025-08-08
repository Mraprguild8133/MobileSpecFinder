"""
Main Telegram bot class
"""
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from bot.handlers import BotHandlers
from scrapers.mobile_scraper import MobileScraper

logger = logging.getLogger(__name__)

class MobileBot:
    """Main Telegram bot class"""
    
    def __init__(self, config):
        self.config = config
        self.scraper = MobileScraper(config)
        self.handlers = BotHandlers(config, self.scraper)
        
        # Initialize bot application
        self.application = Application.builder().token(config.BOT_TOKEN).build()
        
        # Add handlers
        self._add_handlers()
    
    def _add_handlers(self):
        """Add command and callback handlers"""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.handlers.start_command))
        self.application.add_handler(CommandHandler("help", self.handlers.help_command))
        self.application.add_handler(CommandHandler("search", self.handlers.search_command))
        self.application.add_handler(CommandHandler("filter", self.handlers.filter_command))
        
        # Callback query handler for inline keyboards
        self.application.add_handler(CallbackQueryHandler(self.handlers.handle_callback))
        
        # Error handler
        async def error_wrapper(update: object, context: ContextTypes.DEFAULT_TYPE):
            await self.handlers.error_handler(update, context)
        self.application.add_error_handler(error_wrapper)
    
    def run(self):
        """Start the bot"""
        logger.info("Bot is starting...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)
