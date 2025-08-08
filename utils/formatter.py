"""
Message formatting utilities for the Telegram bot
"""
import re
from typing import Dict, List

class MessageFormatter:
    """Class to format messages for Telegram"""
    
    def __init__(self):
        pass
    
    def format_product_card(self, product: Dict) -> str:
        """Format comprehensive product information as a Telegram message"""
        name = self._escape_markdown(product.get('name', 'Unknown'))
        price = self._escape_markdown(product.get('price', 'Price not available'))
        source = product.get('source', 'Unknown')
        product_url = product.get('product_url', '')
        
        # Format message header
        message = f"📱 *{name}*\n"
        message += f"💰 *Price:* {price}\n"
        message += f"🔗 *Source:* {source}\n\n"
        
        # Add product summary if available
        summary = product.get('summary', '')
        if summary:
            clean_summary = self._escape_markdown(summary[:150])
            message += f"📝 *Overview:*\n{clean_summary}\n\n"
        
        # Add key features if available
        features = product.get('features', [])
        if features:
            message += "*⭐ Key Features:*\n"
            for feature in features[:5]:
                clean_feature = self._escape_markdown(self._clean_spec_text(feature))
                message += f"• {clean_feature}\n"
            message += "\n"
        
        # Add detailed specifications
        detailed_specs = product.get('detailed_specs', [])
        specs = product.get('specs', [])
        
        all_specs = detailed_specs + specs if detailed_specs else specs
        
        if all_specs:
            message += "*📋 Full Specifications:*\n"
            for i, spec in enumerate(all_specs[:10], 1):  # Show more comprehensive specs
                clean_spec = self._escape_markdown(self._clean_spec_text(spec))
                message += f"{i}\. {clean_spec}\n"
            message += "\n"
        
        # Add purchase link
        if product_url:
            message += f"🛒 [👆 View Complete Details & Buy Here]({product_url})\n\n"
        
        # Add additional product information
        message += "*📊 Product Information:*\n"
        message += f"• *Source:* {source}\n"
        
        if source == '91mobiles':
            message += "• *Includes:* Prices, offers, reviews & comparisons\n"
        elif source == 'GSMArena':
            message += "• *Includes:* Technical specs & expert reviews\n"
            
        # Add call to action
        message += "\n💡 _Tap the link above for live pricing and availability_"
        
        return message
    
    def _escape_markdown(self, text: str) -> str:
        """Escape special characters for Markdown formatting"""
        if not text:
            return ""
        
        # Characters that need to be escaped in MarkdownV2
        special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        
        for char in special_chars:
            text = text.replace(char, f'\\{char}')
        
        return text
    
    def _clean_spec_text(self, spec: str) -> str:
        """Clean specification text for better formatting"""
        if not spec:
            return ""
        
        # Remove excessive whitespace
        spec = re.sub(r'\s+', ' ', spec.strip())
        
        # Remove HTML tags if any
        spec = re.sub(r'<[^>]+>', '', spec)
        
        # Limit length
        if len(spec) > 80:
            spec = spec[:77] + "..."
        
        return spec
    
    def format_search_summary(self, query: str, total_results: int, filters: Dict[str, any] = None) -> str:
        """Format search summary message"""
        message = f"🔍 *Search Results for: {self._escape_markdown(query)}*\n"
        message += f"📊 Found {total_results} products\n\n"
        
        if filters and filters is not None:
            message += "*Applied Filters:*\n"
            if filters.get('brand'):
                brands = ', '.join(filters['brand'])
                message += f"📱 Brands: {self._escape_markdown(brands)}\n"
            if filters.get('price_range'):
                price_range = filters['price_range']
                range_names = {
                    'budget': 'Budget (₹0-15K)',
                    'mid': 'Mid-range (₹15K-35K)', 
                    'premium': 'Premium (₹35K-80K)',
                    'flagship': 'Flagship (₹80K+)'
                }
                message += f"💰 Price: {range_names.get(price_range, price_range)}\n"
            message += "\n"
        
        return message
    
    def format_error_message(self, error_type: str, query: str = "") -> str:
        """Format error messages"""
        if error_type == "no_results":
            return f"❌ No results found for '{self._escape_markdown(query)}'\n\n" \
                   "Try:\n" \
                   "• Different keywords\n" \
                   "• Brand name + model\n" \
                   "• Remove filters with /filter"
        
        elif error_type == "search_error":
            return "❌ Search failed. This could be due to:\n" \
                   "• Network issues\n" \
                   "• Website temporarily unavailable\n" \
                   "• Rate limiting\n\n" \
                   "Please try again in a few moments."
        
        elif error_type == "invalid_query":
            return "❌ Please provide a valid search query!\n\n" \
                   "Usage: `/search <phone name>`\n" \
                   "Example: `/search iPhone 15 Pro`"
        
        else:
            return "❌ An unexpected error occurred. Please try again later."
