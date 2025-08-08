# 📱 Telegram Mobile Phone Search Bot

A comprehensive Telegram bot that scrapes detailed mobile phone information from popular websites like **91mobiles.com** and **GSMArena.com**. Get complete product details including specifications, images, pricing, and purchase links directly through Telegram chat.

## 🚀 Features

### 🔍 **Advanced Search Capabilities**
- Search mobile phones from multiple sources (91mobiles.com & GSMArena.com)
- Comprehensive product information with images and specifications
- Real-time pricing and availability data
- Direct purchase links for easy shopping

### 🎯 **Smart Filtering System**
- **Brand Filtering**: Filter by popular brands (Samsung, Apple, Xiaomi, OnePlus, etc.)
- **Price Range Filtering**: Budget, Mid-range, Premium, and Flagship categories
- **Interactive Interface**: Easy-to-use inline keyboards for navigation

### 📋 **Detailed Product Information**
- **Product Overview**: Summary and key selling points
- **Key Features**: Highlighted product capabilities
- **Full Specifications**: Complete technical details (up to 10 specs)
- **High-Quality Images**: Product photos with each listing
- **Purchase Links**: Direct links to buy from original sources

### 🌐 **Web Dashboard & Monitoring**
- **Live Status Page**: Real-time bot monitoring at `http://localhost:5000`
- **Webhook Support**: Professional webhook configuration
- **Statistics Tracking**: Request counts, uptime, and performance metrics
- **Health Monitoring**: Auto-refresh dashboard every 30 seconds

## 🛠 Bot Commands

| Command | Description | Example |
|---------|-------------|---------|
| `/start` | Welcome message and instructions | `/start` |
| `/search <phone>` | Search for mobile phones | `/search iPhone 15 Pro` |
| `/filter` | Set brand and price filters | `/filter` |
| `/help` | Show help information | `/help` |

## 📦 Installation & Setup

### Prerequisites
- Python 3.11+
- Telegram Bot Token (from @BotFather)
- Internet connection for web scraping

### 1. Clone and Install Dependencies
```bash
# Install using uv (recommended)
uv sync

# Or using pip
pip install -r requirements_export.txt
```

### 2. Configure Bot Token
1. Create a bot via [@BotFather](https://t.me/botfather) on Telegram
2. Get your bot token
3. Set it as an environment variable:
```bash
export TELEGRAM_BOT_TOKEN="your_bot_token_here"
```

### 3. Run the Bot
```bash
# Start the main bot
python main.py

# Or start with web dashboard
python status_server.py  # Web dashboard on port 5000
```

## 🐳 Docker Deployment

### Quick Start with Docker Compose
```bash
# Set your bot token in environment
export TELEGRAM_BOT_TOKEN="your_token_here"

# Start services
docker-compose up -d
```

### Manual Docker Build
```bash
# Build image
docker build -t telegram-mobile-bot .

# Run container
docker run -d \
  -e TELEGRAM_BOT_TOKEN="your_token" \
  -p 5000:5000 \
  telegram-mobile-bot
```

## 🌐 Web Dashboard

Access the web dashboard at: `http://localhost:5000`

### Features:
- **Real-time Status**: Bot health and uptime monitoring
- **Statistics**: Request counts and performance metrics
- **Webhook Configuration**: Easy webhook setup interface
- **Connection Management**: Switch between polling and webhook modes

### Webhook Setup:
1. Visit the web dashboard
2. Click "Set Webhook" 
3. Use default URL or enter custom webhook URL
4. Bot will switch to webhook mode for better performance

## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Bot token from BotFather | Required |
| `REQUEST_DELAY` | Delay between web requests (seconds) | `2.0` |
| `MAX_REQUESTS_PER_MINUTE` | Rate limiting | `20` |
| `SCRAPING_TIMEOUT` | HTTP request timeout | `30` |
| `MAX_RESULTS_PER_PAGE` | Results per search page | `5` |
| `MAX_TOTAL_RESULTS` | Maximum total results | `20` |
| `PORT` | Web service port | `5000` |

### Supported Brands
- Samsung, Apple, Xiaomi, OnePlus, Google
- Oppo, Vivo, Realme, Motorola, Nokia
- Huawei, Honor, Nothing

### Price Ranges
- **Budget**: ₹0 - ₹15,000
- **Mid-range**: ₹15,000 - ₹35,000  
- **Premium**: ₹35,000 - ₹80,000
- **Flagship**: ₹80,000+

## 🏗 Project Structure

```
telegram-mobile-bot/
├── bot/
│   ├── handlers.py          # Command and callback handlers
│   └── telegram_bot.py      # Main bot class
├── scrapers/
│   └── mobile_scraper.py    # Web scraping logic
├── utils/
│   ├── formatter.py         # Message formatting
│   └── search_filters.py    # Search filtering logic
├── config.py                # Configuration management
├── main.py                  # Bot entry point
├── status_server.py         # Web dashboard server
├── web_service.py          # Advanced web service
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose setup
├── requirements_export.txt # Python dependencies
└── README.md              # This file
```

## 🔍 Usage Examples

### Basic Search
```
/search iPhone 15
```
Returns detailed information about iPhone 15 models with images, specs, and purchase links.

### Search with Filters
1. Set filters: `/filter`
2. Choose brand: Samsung
3. Choose price: Premium
4. Search: `/search Galaxy S24`

### Interactive Features
- Use inline keyboards to navigate results
- Page through multiple search results
- Access detailed specifications for each phone
- Direct links to purchase from original websites

## 🛡 Features & Benefits

### ✅ **Comprehensive Data**
- Scrapes from multiple authoritative sources
- Real-time pricing and availability
- Complete technical specifications
- High-quality product images

### ✅ **User-Friendly Interface**
- Simple command structure
- Interactive inline keyboards
- Professional message formatting
- Auto-refresh capabilities

### ✅ **Reliable Performance**
- Rate limiting to avoid being blocked
- Fallback mechanisms for website changes
- Error handling and graceful failures
- Session-based HTTP requests

### ✅ **Production Ready**
- Docker containerization
- Health checks and monitoring
- Webhook support for scalability
- Professional logging and error tracking

## 🔧 Technical Details

### Web Scraping
- **Multiple URL Formats**: Tries different URL patterns for reliability
- **Advanced Selectors**: Multiple CSS selectors for robust data extraction
- **Content Extraction**: Uses BeautifulSoup and trafilatura libraries
- **Rate Limiting**: Configurable delays and request limits

### Telegram Integration  
- **python-telegram-bot**: Modern async Telegram bot framework
- **Callback Queries**: Interactive inline keyboard handling
- **Error Handling**: Comprehensive error management
- **Message Formatting**: Professional Markdown V2 formatting

### Data Sources
- **91mobiles.com**: Primary source for pricing and offers
- **GSMArena.com**: Secondary source for technical specifications

## 🚀 Deployment Options

### 1. **Development Mode**
```bash
python main.py  # Bot only
python status_server.py  # With web dashboard
```

### 2. **Production with Docker**
```bash
docker-compose up -d
```

### 3. **Cloud Deployment**
- Deploy on any cloud platform (AWS, Google Cloud, Azure)
- Use webhook mode for better performance
- Configure environment variables for your platform

## 📈 Monitoring & Maintenance

### Web Dashboard Metrics
- Bot uptime and status
- Total requests processed
- Last activity timestamp
- Connection type (polling vs webhook)
- Error tracking and logs

### Health Checks
- Automatic health monitoring
- Service restart capabilities
- Real-time status updates
- Performance metrics

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is open source and available under the [MIT License](LICENSE).

## 🆘 Support

- **Issues**: Report bugs and request features via GitHub Issues
- **Documentation**: Check this README for setup and usage
- **Web Dashboard**: Monitor bot status at `http://localhost:5000`

## 🔄 Recent Updates

- ✅ Enhanced product information display with summaries and features
- ✅ Improved 91mobiles scraping with multiple URL formats
- ✅ Added comprehensive web dashboard with webhook support
- ✅ Docker containerization for easy deployment
- ✅ Professional message formatting with numbered specifications

---

**Made with ❤️ for mobile phone enthusiasts**

*Get the latest mobile phone information instantly through Telegram!*