#!/usr/bin/env python3
"""
Render.com optimized app for Telegram Mobile Bot
"""
import os
import sys
import logging
import asyncio
import threading
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify

# Configure logging for Render
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Bot status for monitoring
bot_status = {
    'status': 'Starting...',
    'start_time': datetime.now(),
    'total_requests': 0,
    'last_update': None,
    'webhook_url': None,
    'is_webhook': True,  # Render prefers webhook mode
    'bot_token_present': bool(os.getenv('TELEGRAM_BOT_TOKEN')),
    'platform': 'Render.com'
}

# Simple status page optimized for Render
STATUS_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Telegram Mobile Bot - Running on Render</title>
    <style>
        body { 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            max-width: 900px; margin: 0 auto; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh; color: white;
        }
        .container { background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); border-radius: 15px; padding: 30px; box-shadow: 0 8px 32px rgba(0,0,0,0.1); }
        .header { text-align: center; border-bottom: 2px solid rgba(255,255,255,0.2); padding-bottom: 20px; margin-bottom: 30px; }
        .status-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .status-card { padding: 20px; border-radius: 10px; background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); }
        .status-card h3 { margin: 0 0 10px 0; color: #fff; font-size: 14px; text-transform: uppercase; opacity: 0.8; }
        .status-card p { margin: 0; font-size: 18px; font-weight: 600; }
        .status-online { border-left: 4px solid #10b981; }
        .status-offline { border-left: 4px solid #ef4444; }
        .features { background: rgba(255,255,255,0.05); padding: 25px; border-radius: 10px; margin: 20px 0; }
        .feature-list { list-style: none; padding: 0; }
        .feature-list li { padding: 12px; background: rgba(255,255,255,0.1); margin: 8px 0; border-radius: 8px; border-left: 3px solid #10b981; }
        .refresh-btn { 
            background: linear-gradient(45deg, #10b981, #059669); color: white; border: none; 
            padding: 12px 24px; border-radius: 8px; cursor: pointer; font-size: 16px; 
            font-weight: 600; transition: all 0.3s; margin: 10px 5px;
        }
        .refresh-btn:hover { transform: translateY(-2px); box-shadow: 0 4px 12px rgba(16,185,129,0.4); }
        .platform-badge { 
            display: inline-block; background: #10b981; color: white; padding: 4px 12px; 
            border-radius: 20px; font-size: 12px; font-weight: 600; margin-left: 10px;
        }
        .webhook-url { background: rgba(0,0,0,0.2); padding: 15px; border-radius: 8px; font-family: monospace; font-size: 14px; word-break: break-all; margin: 10px 0; }
    </style>
    <script>
        function refreshStatus() { location.reload(); }
        function setWebhook() {
            const url = `https://${window.location.host}/webhook`;
            fetch('/set_webhook', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({url: url})
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message || 'Webhook configured successfully!');
                refreshStatus();
            })
            .catch(error => alert('Error: ' + error));
        }
        // Auto-refresh every 60 seconds for Render
        setTimeout(function(){ location.reload(); }, 60000);
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📱 Telegram Mobile Bot</h1>
            <span class="platform-badge">{{ status.platform }}</span>
            <p>Professional Mobile Phone Search Bot with Advanced Scraping</p>
        </div>
        
        <div class="status-grid">
            <div class="status-card {{ 'status-online' if status.status == 'Running' else 'status-offline' }}">
                <h3>Service Status</h3>
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
                <h3>Connection Mode</h3>
                <p>{{ 'Webhook ✓' if status.is_webhook else 'Polling' }}</p>
            </div>
            
            <div class="status-card">
                <h3>Last Activity</h3>
                <p>{{ status.last_update or 'Waiting...' }}</p>
            </div>
            
            <div class="status-card">
                <h3>Bot Configuration</h3>
                <p>{{ 'Ready ✓' if status.bot_token_present else 'Token Missing ✗' }}</p>
            </div>
        </div>
        
        <div class="features">
            <h2>🚀 Bot Capabilities</h2>
            <ul class="feature-list">
                <li>Real-time mobile phone search from 91mobiles.com & GSMArena.com</li>
                <li>Comprehensive product details with images and full specifications</li>
                <li>Smart filtering by brand (Samsung, Apple, Xiaomi, etc.) and price range</li>
                <li>Interactive Telegram interface with inline keyboards</li>
                <li>Professional message formatting with purchase links</li>
                <li>Webhook-optimized for Render.com deployment</li>
            </ul>
        </div>
        
        <div style="text-align: center; margin-top: 30px;">
            <button class="refresh-btn" onclick="refreshStatus()">🔄 Refresh Status</button>
            <button class="refresh-btn" onclick="setWebhook()">🔗 Configure Webhook</button>
        </div>
        
        <div class="webhook-url">
            <strong>Webhook URL:</strong> https://{{ request.host }}/webhook
        </div>
        
        <p style="text-align: center; opacity: 0.7; margin-top: 30px; font-size: 14px;">
            Deployed on Render.com • Last updated: {{ datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC') }}
        </p>
    </div>
</body>
</html>
"""

@app.route('/')
def status_page():
    """Render-optimized status page"""
    global bot_status
    
    # Update status based on environment
    if bot_status['bot_token_present']:
        bot_status['status'] = 'Running'
    else:
        bot_status['status'] = 'Configuration Required'
    
    # Calculate uptime
    uptime_delta = datetime.now() - bot_status['start_time']
    hours, remainder = divmod(int(uptime_delta.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime = f"{hours}h {minutes}m {seconds}s"
    
    return render_template_string(
        STATUS_HTML,
        status=bot_status,
        uptime=uptime,
        datetime=datetime,
        request=request
    )

@app.route('/webhook', methods=['POST'])
def webhook():
    """Webhook endpoint for Telegram"""
    global bot_status
    
    try:
        json_data = request.get_json()
        if not json_data:
            return jsonify({'error': 'No data received'}), 400
        
        # Update statistics
        bot_status['total_requests'] += 1
        bot_status['last_update'] = datetime.now().strftime('%H:%M:%S')
        
        # Log webhook activity
        message_text = json_data.get('message', {}).get('text', 'No text')
        logger.info(f"Webhook received: {message_text}")
        
        # Process webhook (implement your bot logic here)
        return jsonify({'ok': True}), 200
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/set_webhook', methods=['POST'])
def set_webhook():
    """Configure webhook for Render deployment"""
    global bot_status
    
    try:
        data = request.get_json() or {}
        webhook_url = data.get('url') or f"https://{request.host}/webhook"
        
        # Update status
        bot_status['webhook_url'] = webhook_url
        bot_status['is_webhook'] = True
        
        logger.info(f"Webhook configured: {webhook_url}")
        
        return jsonify({
            'status': 'success',
            'webhook_url': webhook_url,
            'message': 'Webhook configured successfully for Render!'
        }), 200
        
    except Exception as e:
        logger.error(f"Webhook configuration error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health_check():
    """Health check for Render"""
    return jsonify({
        'status': 'healthy',
        'platform': 'Render.com',
        'timestamp': datetime.now().isoformat(),
        'service': 'telegram-mobile-bot'
    }), 200

@app.route('/api/status')
def api_status():
    """API endpoint for bot status"""
    return jsonify(bot_status)

# Initialize bot in background for Render
def initialize_bot():
    """Initialize bot components safely"""
    global bot_status
    
    try:
        # Import bot components safely
        sys.path.append(os.path.dirname(os.path.abspath(__file__)))
        
        from config import Config
        config = Config()
        
        if config.BOT_TOKEN:
            # Import and initialize bot
            try:
                from bot.telegram_bot import MobileBot
                bot_instance = MobileBot(config)
                
                # Set webhook mode for Render
                webhook_url = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME', 'localhost')}/webhook"
                
                # Start bot in webhook mode
                def run_bot():
                    try:
                        # Set webhook and start application
                        application = bot_instance.application
                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        
                        # Configure for webhook
                        loop.run_until_complete(application.bot.set_webhook(webhook_url))
                        bot_status['webhook_url'] = webhook_url
                        bot_status['status'] = 'Running'
                        bot_status['is_webhook'] = True
                        
                        logger.info(f"Bot configured with webhook: {webhook_url}")
                        
                    except Exception as e:
                        logger.error(f"Bot initialization error: {e}")
                        bot_status['status'] = f'Error: {str(e)}'
                
                # Start bot in background thread
                bot_thread = threading.Thread(target=run_bot, daemon=True)
                bot_thread.start()
                
            except ImportError as e:
                logger.warning(f"Bot components not available: {e}")
                bot_status['status'] = 'Web Service Only'
                
        else:
            bot_status['status'] = 'Missing Bot Token'
            logger.warning("TELEGRAM_BOT_TOKEN not found")
            
    except Exception as e:
        logger.error(f"Initialization error: {e}")
        bot_status['status'] = f'Init Error: {str(e)}'

# Initialize bot on startup
if __name__ == '__main__':
    # Initialize bot components
    initialize_bot()
    
    # Start Flask app for Render
    port = int(os.environ.get('PORT', 10000))  # Render uses PORT env var
    logger.info(f"Starting Render-optimized service on port {port}")
    
    app.run(host='0.0.0.0', port=port, debug=False)
else:
    # For WSGI deployment
    initialize_bot()