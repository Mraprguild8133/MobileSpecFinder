"""
Telegram bot command and callback handlers
"""
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from telegram.constants import ParseMode
from utils.formatter import MessageFormatter
from utils.search_filters import SearchFilters
import re

logger = logging.getLogger(__name__)

class BotHandlers:
    """Handler class for bot commands and callbacks"""
    
    def __init__(self, config, scraper):
        self.config = config
        self.scraper = scraper
        self.formatter = MessageFormatter()
        self.search_filters = SearchFilters(config)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        if not update.message:
            return
            
        welcome_message = """
🔍 *Mobile Phone Search Bot*

Welcome! I can help you find detailed information about mobile phones from:
• 91mobiles.com
• GSMArena.com

*Available Commands:*
/search <phone name> - Search for mobile phones
/filter - Set search filters (brand, price range)
/help - Show this help message

*Example:*
`/search iPhone 15 Pro`
`/search Samsung Galaxy S24`

Get started by typing /search followed by the phone name!
        """
        
        await update.message.reply_text(
            welcome_message,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        if not update.message:
            return
            
        help_message = """
🔍 *Mobile Phone Search Bot - Help*

*Commands:*
• `/search <phone name>` - Search for mobile phones
• `/filter` - Set advanced search filters
• `/help` - Show this help message

*Search Examples:*
• `/search iPhone 15`
• `/search Samsung Galaxy`
• `/search OnePlus 12 Pro`

*Features:*
✅ Product images and specifications
✅ Price information and offers
✅ Purchase links
✅ Advanced filtering options
✅ Results from multiple sources

*Tips:*
• Be specific with phone names for better results
• Use brand names for filtering
• Check both sources for comprehensive information

Need help? Just type your query after /search!
        """
        
        await update.message.reply_text(
            help_message,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def search_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /search command"""
        if not update.message or not update.effective_user:
            return
            
        if not context.args:
            await update.message.reply_text(
                "❌ Please provide a search query!\n\n"
                "Usage: `/search <phone name>`\n"
                "Example: `/search iPhone 15 Pro`",
                parse_mode=ParseMode.MARKDOWN
            )
            return
        
        query = " ".join(context.args)
        
        # Show typing indicator
        await update.message.reply_chat_action("typing")
        
        try:
            # Get user's active filters
            user_id = update.effective_user.id
            filters = context.user_data.get(f"filters_{user_id}", {}) if context.user_data else {}
            
            # Send searching message
            searching_msg = await update.message.reply_text(
                f"🔍 Searching for '{query}'...\n"
                "This may take a few seconds.",
                parse_mode=ParseMode.MARKDOWN
            )
            
            # Perform search
            products = self.scraper.search_mobiles(query, filters)
            
            # Delete searching message
            await searching_msg.delete()
            
            if not products:
                await update.message.reply_text(
                    f"❌ No results found for '{query}'\n\n"
                    "Try:\n"
                    "• Different keywords\n"
                    "• Brand name + model\n"
                    "• Remove filters with /filter",
                    parse_mode=ParseMode.MARKDOWN
                )
                return
            
            # Store results for pagination
            if context.user_data is not None:
                context.user_data[f"search_results_{user_id}"] = products
                context.user_data[f"current_page_{user_id}"] = 0
            
            # Send first page of results
            await self._send_search_results(update, context, products, 0)
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            await update.message.reply_text(
                "❌ An error occurred while searching. Please try again later.",
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def filter_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /filter command"""
        if not update.message or not update.effective_user:
            return
            
        user_id = update.effective_user.id
        
        # Create filter keyboard
        keyboard = [
            [
                InlineKeyboardButton("📱 Brand Filter", callback_data="filter_brand"),
                InlineKeyboardButton("💰 Price Range", callback_data="filter_price")
            ],
            [
                InlineKeyboardButton("🗑️ Clear Filters", callback_data="filter_clear"),
                InlineKeyboardButton("✅ Show Current", callback_data="filter_show")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            "🔧 *Search Filters*\n\n"
            "Configure your search preferences:",
            reply_markup=reply_markup,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline keyboard callbacks"""
        if not update.callback_query or not update.effective_user:
            return
            
        query = update.callback_query
        await query.answer()
        
        data = query.data
        if not data:
            return
            
        user_id = update.effective_user.id
        
        if data.startswith("filter_"):
            await self._handle_filter_callback(update, context, data)
        elif data.startswith("page_"):
            await self._handle_pagination_callback(update, context, data)
        elif data.startswith("brand_"):
            await self._handle_brand_selection(update, context, data)
        elif data.startswith("price_"):
            await self._handle_price_selection(update, context, data)
    
    async def _handle_filter_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
        """Handle filter-related callbacks"""
        if not update.effective_user or not update.callback_query:
            return
            
        user_id = update.effective_user.id
        query = update.callback_query
        
        if data == "filter_brand":
            keyboard = []
            brands = self.config.SUPPORTED_BRANDS
            
            # Create brand selection keyboard (2 brands per row)
            for i in range(0, len(brands), 2):
                row = []
                row.append(InlineKeyboardButton(brands[i], callback_data=f"brand_{brands[i].lower()}"))
                if i + 1 < len(brands):
                    row.append(InlineKeyboardButton(brands[i + 1], callback_data=f"brand_{brands[i + 1].lower()}"))
                keyboard.append(row)
            
            keyboard.append([InlineKeyboardButton("« Back", callback_data="filter_back")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "📱 *Select Brand(s)*\n\nChoose one or more brands to filter:",
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif data == "filter_price":
            keyboard = [
                [InlineKeyboardButton("💵 Budget (₹0-15K)", callback_data="price_budget")],
                [InlineKeyboardButton("💳 Mid-range (₹15K-35K)", callback_data="price_mid")],
                [InlineKeyboardButton("💎 Premium (₹35K-80K)", callback_data="price_premium")],
                [InlineKeyboardButton("👑 Flagship (₹80K+)", callback_data="price_flagship")],
                [InlineKeyboardButton("« Back", callback_data="filter_back")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                "💰 *Select Price Range*\n\nChoose your budget range:",
                reply_markup=reply_markup,
                parse_mode=ParseMode.MARKDOWN
            )
        
        elif data == "filter_clear":
            if context.user_data is not None:
                context.user_data[f"filters_{user_id}"] = {}
            await query.edit_message_text(
                "✅ All filters cleared!\n\nUse /search to find phones without any filters."
            )
        
        elif data == "filter_show":
            filters = context.user_data.get(f"filters_{user_id}", {}) if context.user_data else {}
            if not filters:
                filter_text = "No active filters"
            else:
                filter_parts = []
                if filters.get('brand'):
                    filter_parts.append(f"Brands: {', '.join(filters['brand'])}")
                if filters.get('price_range'):
                    filter_parts.append(f"Price: {filters['price_range']}")
                filter_text = "\n".join(filter_parts)
            
            await query.edit_message_text(
                f"🔧 *Current Filters*\n\n{filter_text}"
            )
        
        elif data == "filter_back":
            await self.filter_command(update, context)
    
    async def _handle_brand_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
        """Handle brand selection"""
        if not update.effective_user:
            return
            
        user_id = update.effective_user.id
        brand = data.replace("brand_", "").title()
        
        # Get current filters
        filters = context.user_data.get(f"filters_{user_id}", {}) if context.user_data else {}
        if 'brand' not in filters:
            filters['brand'] = []
        
        # Toggle brand selection
        if brand.lower() in [b.lower() for b in filters['brand']]:
            filters['brand'] = [b for b in filters['brand'] if b.lower() != brand.lower()]
        else:
            filters['brand'].append(brand)
        
        if context.user_data is not None:
            context.user_data[f"filters_{user_id}"] = filters
        
        selected_brands = ", ".join(filters['brand']) if filters['brand'] else "None"
        
        await update.callback_query.edit_message_text(
            f"✅ Brand filter updated!\n\n"
            f"Selected brands: {selected_brands}\n\n"
            f"Use /search to find phones with these filters."
        )
    
    async def _handle_price_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
        """Handle price range selection"""
        user_id = update.effective_user.id
        price_range = data.replace("price_", "")
        
        # Get current filters
        filters = context.user_data.get(f"filters_{user_id}", {})
        filters['price_range'] = price_range
        if context.user_data is not None:
            context.user_data[f"filters_{user_id}"] = filters
        
        range_names = {
            'budget': 'Budget (₹0-15K)',
            'mid': 'Mid-range (₹15K-35K)',
            'premium': 'Premium (₹35K-80K)',
            'flagship': 'Flagship (₹80K+)'
        }
        
        await update.callback_query.edit_message_text(
            f"✅ Price filter updated!\n\n"
            f"Selected range: {range_names[price_range]}\n\n"
            f"Use /search to find phones in this price range."
        )
    
    async def _handle_pagination_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, data: str):
        """Handle pagination callbacks"""
        user_id = update.effective_user.id
        page = int(data.replace("page_", ""))
        
        products = context.user_data.get(f"search_results_{user_id}", [])
        if not products:
            await update.callback_query.edit_message_text("❌ No search results found. Please search again.")
            return
        
        context.user_data[f"current_page_{user_id}"] = page
        await self._send_search_results_edit(update, context, products, page)
    
    async def _send_search_results(self, update: Update, context: ContextTypes.DEFAULT_TYPE, products: list, page: int):
        """Send search results with pagination"""
        if not update.message:
            return
            
        total_pages = (len(products) - 1) // self.config.MAX_RESULTS_PER_PAGE + 1
        start_idx = page * self.config.MAX_RESULTS_PER_PAGE
        end_idx = min(start_idx + self.config.MAX_RESULTS_PER_PAGE, len(products))
        
        page_products = products[start_idx:end_idx]
        
        # Send header message
        header_text = f"🔍 *Search Results* (Page {page + 1}/{total_pages})\n" \
                     f"Found {len(products)} products\n\n"
        
        # Create pagination keyboard
        keyboard = []
        if total_pages > 1:
            nav_buttons = []
            if page > 0:
                nav_buttons.append(InlineKeyboardButton("◀️ Previous", callback_data=f"page_{page - 1}"))
            if page < total_pages - 1:
                nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data=f"page_{page + 1}"))
            if nav_buttons:
                keyboard.append(nav_buttons)
        
        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
        
        await update.message.reply_text(header_text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
        
        # Send individual product cards
        for product in page_products:
            await self._send_product_card(update, product)
    
    async def _send_search_results_edit(self, update: Update, context: ContextTypes.DEFAULT_TYPE, products: list, page: int):
        """Edit search results message for pagination"""
        total_pages = (len(products) - 1) // self.config.MAX_RESULTS_PER_PAGE + 1
        start_idx = page * self.config.MAX_RESULTS_PER_PAGE
        end_idx = min(start_idx + self.config.MAX_RESULTS_PER_PAGE, len(products))
        
        # Update header
        header_text = f"🔍 *Search Results* (Page {page + 1}/{total_pages})\n" \
                     f"Found {len(products)} products\n\n"
        
        # Create pagination keyboard
        keyboard = []
        if total_pages > 1:
            nav_buttons = []
            if page > 0:
                nav_buttons.append(InlineKeyboardButton("◀️ Previous", callback_data=f"page_{page - 1}"))
            if page < total_pages - 1:
                nav_buttons.append(InlineKeyboardButton("Next ▶️", callback_data=f"page_{page + 1}"))
            if nav_buttons:
                keyboard.append(nav_buttons)
        
        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
        
        await update.callback_query.edit_message_text(
            header_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
        
        # Send new product cards for this page
        page_products = products[start_idx:end_idx]
        for product in page_products:
            await update.callback_query.message.reply_photo(
                photo=product.get('image_url', ''),
                caption=self.formatter.format_product_card(product),
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def _send_product_card(self, update: Update, product: dict):
        """Send individual product card with image and details"""
        if not update.message:
            return
            
        try:
            caption = self.formatter.format_product_card(product)
            
            if product.get('image_url'):
                await update.message.reply_photo(
                    photo=product['image_url'],
                    caption=caption,
                    parse_mode=ParseMode.MARKDOWN
                )
            else:
                await update.message.reply_text(
                    caption,
                    parse_mode=ParseMode.MARKDOWN
                )
        
        except Exception as e:
            logger.error(f"Error sending product card: {e}")
            # Fallback to text-only message
            await update.message.reply_text(
                self.formatter.format_product_card(product),
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        """Handle errors"""
        logger.error(f"Update {update} caused error {context.error}")
        
        if hasattr(update, 'effective_message') and update.effective_message:
            await update.effective_message.reply_text(
                "❌ An error occurred. Please try again later."
            )
