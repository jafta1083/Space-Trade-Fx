import sys
from pathlib import Path
import pytest

# Make SpaceTradingFX/flask_dashboard importable
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "SpaceTradingFX"))

from flask_dashboard.app import app, db
from flask_dashboard.models import TradingPreference


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    with app.test_client() as client:
        with app.app_context():
            # create tables
            db.create_all()
        yield client
        # teardown
        with app.app_context():
            db.session.remove()
            db.drop_all()


def login(client, email='test@example.com'):
    return client.post('/login', data={'email': email}, follow_redirects=True)


def test_preferences_save_direction_preferences(client):
    # Log in (the login route will create the user)
    rv = login(client)
    assert rv.status_code == 200

    # Access preferences page
    rv = client.get('/preferences')
    assert rv.status_code == 200

    # Post updated preferences including direction per pair
    data = {
        'currency_pairs': ['EURUSD', 'GBPUSD'],
        'timeframe': '1H',
        'risk_percentage': '1.5',
        'max_concurrent_trades': '2',
        'trading_enabled': 'on',
        'direction_EURUSD': 'BUY',
        'direction_GBPUSD': 'SELL'
    }

    rv = client.post('/preferences', data=data, follow_redirects=True)
    assert rv.status_code == 200

    # The login route creates id by replacing @ and . with _
    expected_user_id = 'test_example_com'

    # Verify preferences persisted
    with app.app_context():
        pref = TradingPreference.query.filter_by(user_id=expected_user_id).first()
        assert pref is not None
        assert set(pref.currency_pairs) == set(['EURUSD', 'GBPUSD'])
        assert pref.timeframe == '1H'
        assert abs(pref.risk_percentage - 1.5) < 1e-6
        assert pref.max_concurrent_trades == 2
        assert pref.trading_enabled is True
        assert pref.direction_preferences.get('EURUSD') == 'BUY'
        assert pref.direction_preferences.get('GBPUSD') == 'SELL'
