#!/usr/bin/env python3
"""
Web service for Telegram bot with status page and webhook support
"""
import os
import logging
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify
try:
    from telegram import Update
    from telegram.ext import Application
except ImportError:
    # Fallback if telegram imports fail
    Update = None
    Application = None
from config import Config
from bot.telegram_bot import MobileBot
import asyncio
import threading

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
config = Config()
bot_instance = None
bot_status = {
    'status': 'Starting...',
    'start_time': datetime.now(),
    'total_requests': 0,
    'last_update': None,
    'webhook_url': None,
    'is_webhook': False
}

# HTML template for status page
STATUS_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Telegram Mobile Bot Status</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 800px; margin: 0 auto; padding: 20px; background: #f5f5f5;
        }
        .container { background: white; border-radius: 10px; padding: 30px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        .header { text-align: center; border-bottom: 2px solid #007bff; padding-bottom: 20px; margin-bottom: 30px; }
        .status-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }
        .status-card { padding: 20px; border-radius: 8px; border-left: 4px solid #007bff; background: #f8f9fa; }
        .status-card h3 { margin: 0 0 10px 0; color: #007bff; font-size: 14px; text-transform: uppercase; }
        .status-card p { margin: 0; font-size: 18px; font-weight: 600; }
        .status-online { border-left-color: #28a745; }
        .status-offline { border-left-color: #dc3545; }
        .features { margin-top: 30px; }
        .feature-list { list-style: none; padding: 0; }
        .feature-list li { padding: 10px; background: #e9ecef; margin: 5px 0; border-radius: 5px; }
        .feature-list li::before { content: "✓ "; color: #28a745; font-weight: bold; }
        .refresh-btn { 
            background: #007bff; color: white; border: none; padding: 10px 20px; 
            border-radius: 5px; cursor: pointer; font-size: 16px; margin-top: 20px;
        }
        .refresh-btn:hover { background: #0056b3; }
    </style>
    <script>
        function refreshStatus() {
            location.reload();
        }
        // Auto-refresh every 30 seconds
        setTimeout(function(){ location.reload(); }, 30000);
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📱 Telegram Mobile Bot</h1>
            <p>Mobile Phone Search Bot with Advanced Filtering</p>
        </div>
        
        <div class="status-grid">
            <div class="status-card {{ 'status-online' if status.status == 'Running' else 'status-offline' }}">
                <h3>Bot Status</h3>
                <p>{{ status.status }}</p>
            </div>
            
            <div class="status-card">
                <h3>Uptime</h3>
                <p>{{ uptime }}</p>
            </div>
            
            <div class="status-card">
                <h3>Total Requests</h3>
                <p>{{ status.total_requests }}</p>
            </div>
            
            <div class="status-card">
                <h3>Connection Type</h3>
                <p>{{ 'Webhook' if status.is_webhook else 'Polling' }}</p>
            </div>
            
            <div class="status-card">
                <h3>Last Update</h3>
                <p>{{ status.last_update or 'Never' }}</p>
            </div>
            
            <div class="status-card">
                <h3>Bot Token</h3>
                <p>{{ 'Configured ✓' if bot_token else 'Missing ✗' }}</p>
            </div>
        </div>
        
        <div class="features">
            <h2>🚀 Bot Features</h2>
            <ul class="feature-list">
                <li>Mobile phone search from 91mobiles.com and GSMArena.com</li>
                <li>Comprehensive product details with images and specifications</li>
                <li>Advanced filtering by brand and price range</li>
                <li>Interactive inline keyboards for easy navigation</li>
                <li>Real-time product information and purchase links</li>
                <li>Professional message formatting with full product details</li>
            </ul>
        </div>
        
        <button class="refresh-btn" onclick="refreshStatus()">🔄 Refresh Status</button>
        <p style="text-align: center; color: #6c757d; margin-top: 30px;">
            Last updated: {{ datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC') }}
        </p>
    </div>
</body>
</html>
"""

@app.route('/')
def status_page():
    """Display bot status page"""
    global bot_status
    
    # Calculate uptime
    uptime_delta = datetime.now() - bot_status['start_time']
    hours, remainder = divmod(int(uptime_delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime = f"{hours}h {minutes}m {seconds}s"
    
    return render_template_string(
        STATUS_HTML,
        status=bot_status,
        uptime=uptime,
        bot_token=bool(config.BOT_TOKEN),
        datetime=datetime
    )

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle Telegram webhook updates"""
    global bot_status
    
    try:
        if not bot_instance:
            return jsonify({'error': 'Bot not initialized'}), 500
            
        # Get update from Telegram
        json_data = request.get_json()
        if not json_data:
            return jsonify({'error': 'No JSON data'}), 400
            
        if Update and bot_instance:
            # Create Update object and process it
            update = Update.de_json(json_data, bot_instance.application.bot)
            
            # Update statistics
            bot_status['total_requests'] += 1
            bot_status['last_update'] = datetime.now().strftime('%H:%M:%S')
            
            # Process the update in a separate thread to avoid blocking
            def process_update():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(bot_instance.application.process_update(update))
                loop.close()
            
            threading.Thread(target=process_update, daemon=True).start()
        else:
            bot_status['total_requests'] += 1
            bot_status['last_update'] = datetime.now().strftime('%H:%M:%S')
        
        return jsonify({'status': 'ok'}), 200
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/set_webhook', methods=['POST'])
def set_webhook():
    """Set webhook URL for the bot"""
    global bot_status
    
    try:
        webhook_url = request.json.get('url') if request.json else None
        if not webhook_url:
            # Use default webhook URL
            webhook_url = f"https://{os.getenv('REPL_SLUG', 'telegram-bot')}.{os.getenv('REPL_OWNER', 'user')}.repl.co/webhook"
        
        if bot_instance and hasattr(bot_instance, 'application'):
            try:
                # Set webhook in separate thread
                def set_webhook_async():
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    loop.run_until_complete(bot_instance.application.bot.set_webhook(url=webhook_url))
                    loop.close()
                
                threading.Thread(target=set_webhook_async, daemon=True).start()
                
                bot_status['webhook_url'] = webhook_url
                bot_status['is_webhook'] = True
                bot_status['status'] = 'Running (Webhook)'
                
                return jsonify({
                    'status': 'success',
                    'webhook_url': webhook_url,
                    'message': 'Webhook set successfully'
                }), 200
            except Exception as e:
                logger.error(f"Failed to set webhook: {e}")
                return jsonify({'error': f'Failed to set webhook: {str(e)}'}), 500
        else:
            return jsonify({'error': 'Bot not initialized'}), 500
            
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def api_stats():
    """API endpoint for bot statistics"""
    return jsonify(bot_status)

def start_bot():
    """Start the Telegram bot"""
    global bot_instance, bot_status
    
    try:
        if not config.BOT_TOKEN:
            bot_status['status'] = 'Error: No bot token'
            logger.error("BOT_TOKEN not found")
            return
            
        # Initialize bot
        try:
            bot_instance = MobileBot(config)
            bot_status['status'] = 'Running'
            logger.info("Bot initialized successfully")
            
            # Start polling in a separate thread
            def run_polling():
                try:
                    bot_instance.run()
                except Exception as e:
                    logger.error(f"Bot polling error: {e}")
                    bot_status['status'] = f'Error: {str(e)}'
            
            polling_thread = threading.Thread(target=run_polling, daemon=True)
            polling_thread.start()
        except ImportError as e:
            logger.warning(f"Bot initialization failed due to import error: {e}")
            bot_status['status'] = 'Bot Disabled (Import Error)'
        except Exception as e:
            logger.error(f"Bot initialization failed: {e}")
            bot_status['status'] = f'Error: {str(e)}'
        
    except Exception as e:
        logger.error(f"Error starting bot: {e}")
        bot_status['status'] = f'Error: {str(e)}'

if __name__ == '__main__':
    # Start the bot
    start_bot()
    
    # Start web server
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting web service on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)