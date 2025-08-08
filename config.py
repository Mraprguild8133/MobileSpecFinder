"""
Configuration settings for the Telegram Mobile Bot
"""
import os

class Config:
    """Configuration class for bot settings"""
    
    def __init__(self):
        # Telegram Bot Token
        self.BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
        
        # Rate limiting settings
        self.REQUEST_DELAY = float(os.getenv('REQUEST_DELAY', '2.0'))
        self.MAX_REQUESTS_PER_MINUTE = int(os.getenv('MAX_REQUESTS_PER_MINUTE', '20'))
        
        # Scraping settings
        self.TIMEOUT = int(os.getenv('SCRAPING_TIMEOUT', '30'))
        self.USER_AGENT = os.getenv('USER_AGENT', 
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        
        # Search settings
        self.MAX_RESULTS_PER_PAGE = int(os.getenv('MAX_RESULTS_PER_PAGE', '5'))
        self.MAX_TOTAL_RESULTS = int(os.getenv('MAX_TOTAL_RESULTS', '20'))
        
        # Supported brands for filtering
        self.SUPPORTED_BRANDS = [
            'Samsung', 'Apple', 'Xiaomi', 'OnePlus', 'Google', 'Oppo', 'Vivo',
            'Realme', 'Motorola', 'Nokia', 'Huawei', 'Honor', 'Nothing'
        ]
        
        # Price ranges for filtering (in INR)
        self.PRICE_RANGES = {
            'budget': (0, 15000),
            'mid': (15000, 35000),
            'premium': (35000, 80000),
            'flagship': (80000, 200000)
        }
