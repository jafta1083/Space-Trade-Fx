# Space Trading FX

A Flask-based forex trading platform with license management and an automated trading bot.

## Project Structure

```
SpaceTradingFX/
├── space_trading_fx/          # Core trading bot package
│   ├── core/                  # Strategy engine and signal reading
│   ├── trading/               # Trade execution logic
│   ├── config/                # Configuration (settings)
│   ├── utils/                 # Logging and utilities
│   └── main.py                # Bot entry point
├── flask_dashboard/           # Web dashboard for license & trading management
│   ├── app.py                 # Flask app factory
│   ├── main.py                # Dashboard entry point (runs on port 5000)
│   ├── routes.py              # API routes and views
│   ├── models.py              # Database models
│   ├── license_manager.py      # License validation logic
│   ├── trading_engine.py       # Trading logic integration
│   ├── forex_data.py           # Forex data provider
│   └── templates/             # HTML templates
├── tests/                     # Unit tests
├── data/                      # Trading signals (signals.txt)
└── requirements.txt           # Python dependencies
```

## Setup

### 1. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
# OR from project root:
pip install -e .
```

### 3. Environment Variables

Create a `.env` file in the project root:

```
SESSION_SECRET=your-secret-key-here
DATABASE_URL=postgresql://user:password@localhost/trading_db
# Or use SQLite (default): sqlite:///trading.db
```

## Running the Application

### Flask Dashboard (Web UI)

```bash
cd flask_dashboard
python main.py
```

The dashboard runs on `http://localhost:5000`

### Trading Bot

```bash
cd space_trading_fx
python main.py
```

The bot reads trading signals from `data/signals.txt`

## Key Components

### Core Package (`space_trading_fx/`)

- **strategy_engine.py** - Main strategy execution logic
- **signal_reader.py** - Reads trading signals from file
- **trade_executor.py** - Executes trades based on signals
- **logger.py** - Centralized logging with remote log transmission

### Flask Dashboard

- **License Management** - Create, validate, and activate licenses
- **Trading Preferences** - Configure currency pairs, risk levels, etc.
- **Account Summary** - View balance, open trades, P&L
- **Manual Trading** - Execute trades via web interface
- **Market Analysis** - Analyze forex market signals

## Testing

Run tests with pytest:

```bash
pytest tests/ -v
```

## Features

- ✅ User authentication and session management
- ✅ License-based access control
- ✅ Automated trading bot with signal reading
- ✅ Real-time forex data integration
- ✅ Trade execution and P&L tracking
- ✅ Web dashboard for manual control
- ✅ Logging with remote transmission
- ✅ Database persistence (PostgreSQL or SQLite)

## Dependencies

See `requirements.txt` or `pyproject.toml` for the full list:

- Flask & Flask extensions (login, SQLAlchemy, dance)
- Loguru (advanced logging)
- Pandas (data analysis)
- Schedule (task scheduling)
- Requests (HTTP client)
- Pytest (testing)
- PSycopg2 (PostgreSQL driver)

## Security Notes

- Set `SESSION_SECRET` environment variable in production
- Do not commit `.env` files with real credentials
- Use strong, unique license keys for production
- Store API keys and secrets in environment variables only

## Development

### Adding Tests

Place unit tests in `tests/` directory with `test_` prefix:

```python
# tests/test_my_feature.py
def test_example():
    assert 1 + 1 == 2
```

### Code Style

- Follow PEP 8
- Use absolute imports within the `space_trading_fx` package
- Add docstrings to functions and classes

## Troubleshooting

**Import errors when running the bot:**
- Ensure `space_trading_fx` is in PYTHONPATH
- Run from the project root directory
- Check that venv is activated

**Database errors:**
- Set `DATABASE_URL` environment variable
- Run migrations if applicable
- Check database credentials

**Missing dependencies:**
- Reinstall: `pip install -r requirements.txt`
- Check Python version: requires Python >= 3.12

## License

See LICENSE file for details.
