# SpaceTradingFX

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

## Setup
The application is configured to run in the Replit environment with:
- Python 3.12
- Flask web server on port 5000
- Dependencies managed via uv package manager

## Dependencies
- Flask - Web framework for the dashboard
- pandas - Data manipulation
- loguru - Logging
- schedule - Task scheduling
- python-dotenv - Environment variable management
- pytest - Testing framework
- PySimpleGUI - GUI components

## Running the Application
The Flask dashboard is automatically started via the configured workflow and runs on port 5000. The dashboard displays:
- Account balance
- Active trades with profit/loss
- Market trends and payouts
- Bot logs

## Deployment
The application is configured for autoscale deployment, which is suitable for this stateless web dashboard.

## Recent Changes
- 2025-11-02: Initial Replit setup
  - Installed Python dependencies
  - Configured Flask app to bind to 0.0.0.0:5000
  - Set up workflow for Flask dashboard
  - Configured deployment settings
