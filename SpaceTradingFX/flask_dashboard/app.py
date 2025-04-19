from flask import Flask, render_template,request
import logging
import os

app = Flask(__name__)

@app.route('/')
def home():
    
    # Make sure 'logs' folder exists
    os.makedirs("logs", exist_ok=True)

    # Configure Werkzeug logger to write to logs/server.log
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler('logs/server.log')
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
    werkzeug_logger.addHandler(file_handler)
    
    
    # Read logs from file (you already have this part)
    log_path = os.path.join(os.path.dirname(__file__), "..","logs","bot.log")
    if os.path.exists(log_path):
        with open(log_path, 'r') as file:
            logs = file.readlines()
    else:
        logs = ["No logs yet."]
    
    # Mock data for other variables
    balance = 10000  # Example balance
    active_trades = [
        {"currency_pair": "EUR/USD", "type": "Buy", "profit": 150},
        {"currency_pair": "GBP/USD", "type": "Sell", "profit": -50}
    ]
    market_trends = [
        {"pair": "EUR/USD", "timeframe": "1H", "payout": "1.5%"},
        {"pair": "GBP/USD", "timeframe": "15M", "payout": "2.3%"}
    ]
    
    # Return the template with variables
    return render_template('dashboard.html', logs=logs, balance=balance, active_trades=active_trades, market_trends=market_trends)

if __name__ == '__main__':
    app.run(debug=True)
