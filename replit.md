# Overview

This is a comprehensive Telegram bot that scrapes detailed mobile phone information from popular websites like 91mobiles.com and GSMArena.com. The bot provides complete product details including full specifications, key features, product summaries, images, pricing information, and direct purchase links through an intuitive Telegram chat interface.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Bot Framework
- **Telegram Bot API**: Built using python-telegram-bot library for handling Telegram interactions
- **Command-based Interface**: Implements standard Telegram bot commands (/start, /search, /filter, /help)
- **Callback Query Handling**: Uses inline keyboards for interactive filtering options
- **Error Handling**: Centralized error handling for graceful failure management

## Web Scraping Architecture
- **Multi-source Scraping**: Supports scraping from multiple websites (91mobiles, GSMArena)
- **Resilient URL Handling**: Multiple URL format attempts for robust website access
- **Comprehensive Data Extraction**: Extracts product summaries, detailed specs, features, and images
- **Rate Limiting**: Implements configurable request delays and limits to avoid being blocked
- **Session Management**: Uses persistent HTTP sessions with custom User-Agent headers
- **Advanced Content Extraction**: Utilizes BeautifulSoup and trafilatura for robust HTML parsing
- **Fallback Mechanisms**: Multiple CSS selectors and extraction methods for reliability

## Search and Filtering System
- **Flexible Search**: Text-based search with URL encoding for special characters
- **Brand Filtering**: Supports filtering by predefined mobile phone brands (Samsung, Apple, etc.)
- **Price Range Filtering**: Categorized price ranges (budget, mid-range, premium, flagship)
- **Result Limiting**: Configurable limits for results per page and total results

## Message Formatting
- **Comprehensive Product Cards**: Full product details including overview, features, and complete specifications
- **Enhanced Information Display**: Shows product summaries, key features, and detailed technical specifications
- **Professional Formatting**: Uses Telegram Markdown V2 with structured layout for easy reading
- **Rich Content**: Includes numbered specifications, feature highlights, and clear call-to-action buttons
- **Text Sanitization**: Escapes special characters to prevent formatting issues

## Configuration Management
- **Environment Variables**: All sensitive and configurable settings loaded from environment
- **Modular Configuration**: Centralized config class with logical groupings
- **Default Values**: Fallback values for all configuration options

# External Dependencies

## Core Libraries
- **python-telegram-bot**: Telegram Bot API wrapper for Python
- **requests**: HTTP library for web scraping
- **beautifulsoup4**: HTML/XML parsing library
- **trafilatura**: Content extraction library for web scraping

## Target Websites
- **91mobiles.com**: Primary source for mobile phone information and pricing
- **GSMArena.com**: Secondary source for detailed technical specifications

## Environment Requirements
- **TELEGRAM_BOT_TOKEN**: Required Telegram bot token from BotFather
- **REQUEST_DELAY**: Rate limiting configuration (default: 2.0 seconds)
- **MAX_REQUESTS_PER_MINUTE**: Request throttling (default: 20)
- **SCRAPING_TIMEOUT**: HTTP request timeout (default: 30 seconds)
- **USER_AGENT**: Custom User-Agent string for web requests

## Runtime Dependencies
- **Python 3.7+**: Modern Python version for async/await support
- **Internet Connection**: Required for both Telegram API and web scraping
- **Memory Management**: Session-based requests for efficient connection pooling