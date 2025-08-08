#!/usr/bin/env python3
"""
Standalone web service for Telegram bot status monitoring
"""
import os
import logging
import json
from datetime import datetime
from flask import Flask, render_template_string, request, jsonify

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Bot status tracking
bot_status = {
    'status': 'Unknown',
    'start_time': datetime.now(),
    'total_requests': 0,
    'last_update': None,
    'webhook_url': None,
    'is_webhook': False,
    'bot_token_present': bool(os.getenv('TELEGRAM_BOT_TOKEN'))
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
        .webhook-section { margin-top: 20px; padding: 20px; background: #fff3cd; border-radius: 8px; }
        .webhook-url { background: #f8f9fa; padding: 10px; border-radius: 4px; font-family: monospace; word-break: break-all; }
        .btn-secondary { background: #6c757d; margin-left: 10px; }
        .btn-secondary:hover { background: #545b62; }
    </style>
    <script>
        function refreshStatus() {
            location.reload();
        }
        function setWebhook() {
            const url = document.getElementById('webhook-url').value || generateWebhookUrl();
            fetch('/set_webhook', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({url: url})
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message || 'Webhook operation completed');
                refreshStatus();
            })
            .catch(error => {
                alert('Error: ' + error);
            });
        }
        function generateWebhookUrl() {
            return `https://${window.location.host}:5000/webhook`;
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
                <p>{{ 'Configured ✓' if status.bot_token_present else 'Missing ✗' }}</p>
            </div>
        </div>
        
        <div class="webhook-section">
            <h3>🔗 Webhook Configuration</h3>
            <p>Set up webhook for better performance and reliability:</p>
            <input type="text" id="webhook-url" placeholder="Enter webhook URL (optional)" class="webhook-url" style="width: 100%; margin: 10px 0;">
            <br>
            <button class="refresh-btn" onclick="setWebhook()">Set Webhook</button>
            <button class="refresh-btn btn-secondary" onclick="document.getElementById('webhook-url').value = generateWebhookUrl()">Use Default URL</button>
            <p style="font-size: 12px; color: #6c757d; margin-top: 10px;">
                Default: https://{{ request.host }}:5000/webhook
            </p>
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
    
    # Try to read status from main bot if available
    try:
        # Check if main bot is running by looking for its process
        import subprocess
        result = subprocess.run(['pgrep', '-f', 'main.py'], capture_output=True, text=True)
        if result.returncode == 0:
            bot_status['status'] = 'Running'
        else:
            bot_status['status'] = 'Stopped'
    except:
        bot_status['status'] = 'Unknown'
    
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
    """Handle Telegram webhook updates"""
    global bot_status
    
    try:
        # Just log the webhook request for now
        json_data = request.get_json()
        if not json_data:
            return jsonify({'error': 'No JSON data'}), 400
            
        # Update statistics
        bot_status['total_requests'] += 1
        bot_status['last_update'] = datetime.now().strftime('%H:%M:%S')
        
        logger.info(f"Webhook received: {json_data.get('message', {}).get('text', 'No text')}")
        
        # For now, just acknowledge the webhook
        # In production, this would forward to the actual bot
        return jsonify({'status': 'ok'}), 200
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/set_webhook', methods=['POST'])
def set_webhook():
    """Set webhook URL for the bot"""
    global bot_status
    
    try:
        data = request.get_json() or {}
        webhook_url = data.get('url') or f"https://{request.host}:5000/webhook"
        
        # For now, just simulate setting webhook
        bot_status['webhook_url'] = webhook_url
        bot_status['is_webhook'] = True
        
        logger.info(f"Webhook URL set to: {webhook_url}")
        
        return jsonify({
            'status': 'success',
            'webhook_url': webhook_url,
            'message': f'Webhook configured for {webhook_url}'
        }), 200
            
    except Exception as e:
        logger.error(f"Error setting webhook: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/stats')
def api_stats():
    """API endpoint for bot statistics"""
    return jsonify(bot_status)

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'service': 'telegram-bot-status'
    }), 200

if __name__ == '__main__':
    # Start web server
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"Starting status web service on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)