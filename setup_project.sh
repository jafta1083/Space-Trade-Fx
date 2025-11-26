#!/bin/bash

# Create main project folder structure
mkdir -p space_trading_fx/{core,trading,config,utils}
mkdir -p tests
mkdir -p logs

# Create Python files
touch space_trading_fx/__init__.py
touch space_trading_fx/main.py

touch space_trading_fx/core/__init__.py
touch space_trading_fx/core/strategy_engine.py

touch space_trading_fx/trading/__init__.py
touch space_trading_fx/trading/trade_executor.py

touch space_trading_fx/config/__init__.py
touch space_trading_fx/config/settings.py

touch space_trading_fx/utils/__init__.py
touch space_trading_fx/utils/logger.py

# Create test file
touch tests/test_strategy_engine.py

# Root-level files
touch requirements.txt
touch README.md
touch .gitignore
touch logs/bot.log

echo "✅ SpaceTradingFX folder structure created successfully!"

# Install dependencies
python3 -m venv venv
. venv/bin/activate
pip install --upgrade pip
pip install flask flask_sqlalchemy flask_login flask-dance sqlalchemy oauthlib requests loguru rsa

# Run Flask dashboard
. venv/bin/activate
python3 SpaceTradingFX/flask_dashboard/main.py
