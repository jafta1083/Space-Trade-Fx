# SpaceTradingFX Setup

## Overview
SpaceTradingFX is a Python-based trading bot application with a Flask web dashboard. The application reads trading signals from a file and displays them in a web-based dashboard along with account balance, active trades, and market trends.

## Project Structure
- `SpaceTradingFX/flask_dashboard/` - Flask web application for the dashboard
  - `app.py` - Main Flask application
  - `templates/dashboard.html` - Dashboard HTML template
- `SpaceTradingFX/space_trading_fx/` - Core trading bot logic
  - `core/` - Core functionality (signal reader, strategy engine)
  - `trading/` - Trading execution logic
  - `config/` - Configuration settings
  - `utils/` - Utility functions
- `SpaceTradingFX/data/` - Trading signals data
- `SpaceTradingFX/logs/` - Application logs

## Setup (Bot_setup)
The application can run in local environments or in hosted platforms. For local development:

- Python 3.12+
- Flask web server on port 5000
- Dependencies managed via pip and `pyproject.toml` / `requirements.txt`

### Quick Local Setup

```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r SpaceTradingFX/requirements.txt
```

### Running the Flask Dashboard

```bash
source venv/bin/activate
python SpaceTradingFX/flask_dashboard/main.py
```

The dashboard runs on `http://127.0.0.1:5000` by default.

## Notes
- Replace any Replit-specific credentials with your own when running locally.
- If you plan to deploy, configure `SESSION_SECRET` and `DATABASE_URL` environment variables.

