from flask import render_template, request, redirect, url_for, flash, jsonify, session
from flask_login import current_user, login_required, login_user, logout_user
from app import app, db
from models import User, License, TradingPreference, Trade, TradingSignal
from license_manager import (
    create_user_license, 
    check_license_valid, 
    require_license,
    LICENSE_TYPES
)
from trading_engine import TradingEngine
from forex_data import get_forex_provider
from datetime import datetime
import os


# Make session permanent
@app.before_request
def make_session_permanent():
    session.permanent = True


# Home/Landing page
@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('landing.html')


# Simple login for development (without Replit Auth)
@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email')
        mentor_id = request.form.get('mentor_id', '')
        
        if not email:
            flash('Email is required', 'error')
            return render_template('login.html')
        
        # Find or create user
        user = User.query.filter_by(email=email).first()
        
        if not user:
            # Create new user
            user = User(
                id=email.replace('@', '_').replace('.', '_'),
                email=email,
                first_name=mentor_id if mentor_id else 'User'
            )
            db.session.add(user)
            db.session.commit()
            flash(f'Welcome! New account created for {email}', 'success')
        else:
            flash(f'Welcome back, {email}!', 'success')
        
        # Log in the user
        login_user(user, remember=True)
        return redirect(url_for('dashboard'))
    
    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'info')
    return redirect(url_for('index'))


# Main dashboard
@app.route('/dashboard')
@login_required
def dashboard():
    # Check if user has valid license
    is_valid, license_info = check_license_valid(current_user.id)
    
    # Get trading engine
    engine = TradingEngine(current_user.id)
    account_summary = engine.get_account_summary()
    
    # Get trading preferences
    preferences = TradingPreference.query.filter_by(user_id=current_user.id).first()
    
    # Get recent signals
    recent_signals = TradingSignal.query.order_by(
        TradingSignal.created_at.desc()
    ).limit(5).all()
    
    return render_template(
        'dashboard.html',
        user=current_user,
        has_license=is_valid,
        license=license_info if is_valid else None,
        account_summary=account_summary,
        preferences=preferences,
        recent_signals=recent_signals
    )


# License management
@app.route('/licenses')
@login_required
def view_licenses():
    user_licenses = License.query.filter_by(user_id=current_user.id).order_by(
        License.created_at.desc()
    ).all()
    
    return render_template(
        'licenses.html',
        licenses=user_licenses,
        license_types=LICENSE_TYPES
    )


@app.route('/buy-license', methods=['GET', 'POST'])
@login_required
def buy_license():
    if request.method == 'POST':
        license_type = request.form.get('license_type')
        license_key = request.form.get('license_key')
        
        if license_key:
            # User entering existing license key
            from license_manager import validate_license_key
            is_valid, result = validate_license_key(license_key)
            
            if is_valid:
                # Create license record for user
                new_license = License(
                    user_id=current_user.id,
                    license_key=license_key,
                    license_type=result['license_type'],
                    status='active',
                    issued_at=datetime.fromisoformat(result['issued']),
                    expires_at=datetime.fromisoformat(result['expires']),
                    max_active_trades=result['max_trades'],
                    features=result['features']
                )
                db.session.add(new_license)
                db.session.commit()
                
                flash('License key activated successfully!', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash(f'Invalid license key: {result}', 'error')
        
        elif license_type and license_type in LICENSE_TYPES:
            # Generate new license (demo mode - in production, integrate Stripe)
            new_license = create_user_license(current_user.id, license_type)
            
            flash(f'{license_type.title()} license created! Your key: {new_license.license_key[:50]}...', 'success')
            return redirect(url_for('view_licenses'))
        else:
            flash('Please select a license type or enter a valid key', 'error')
    
    return render_template('buy_license.html', license_types=LICENSE_TYPES)


# Trading preferences
@app.route('/preferences', methods=['GET', 'POST'])
@login_required
@require_license
def trading_preferences():
    preferences = TradingPreference.query.filter_by(user_id=current_user.id).first()
    
    if not preferences:
        preferences = TradingPreference(user_id=current_user.id)
        db.session.add(preferences)
        db.session.commit()
    
    if request.method == 'POST':
        # Update preferences
        currency_pairs = request.form.getlist('currency_pairs')
        preferences.currency_pairs = currency_pairs
        preferences.timeframe = request.form.get('timeframe', '1H')
        preferences.risk_percentage = float(request.form.get('risk_percentage', 1.0))
        preferences.max_concurrent_trades = int(request.form.get('max_concurrent_trades', 3))
        preferences.trading_enabled = request.form.get('trading_enabled') == 'on'
        
        db.session.commit()
        flash('Trading preferences updated!', 'success')
        return redirect(url_for('dashboard'))
    
    # Available currency pairs
    available_pairs = ['EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 'USDCAD', 'USDCHF', 'NZDUSD']
    
    return render_template(
        'preferences.html',
        preferences=preferences,
        available_pairs=available_pairs
    )


# Trading actions
@app.route('/analyze-markets')
@login_required
@require_license
def analyze_markets():
    engine = TradingEngine(current_user.id)
    signals = engine.analyze_markets()
    
    flash(f'Analyzed {len(signals)} currency pairs', 'success')
    return redirect(url_for('dashboard'))


@app.route('/manual-trade', methods=['POST'])
@login_required
@require_license
def manual_trade():
    currency_pair = request.form.get('currency_pair')
    trade_type = request.form.get('trade_type')  # BUY or SELL
    
    if not currency_pair or not trade_type:
        flash('Currency pair and trade type are required', 'error')
        return redirect(url_for('dashboard'))
    
    engine = TradingEngine(current_user.id)
    
    # Get current market analysis
    forex_provider = get_forex_provider()
    signal_data = forex_provider.analyze_signal(currency_pair)
    
    # Execute trade
    trade = engine.execute_trade(currency_pair, trade_type, signal_data)
    
    if trade:
        flash(f'Trade opened: {currency_pair} {trade_type}', 'success')
    else:
        flash('Could not execute trade. Check your settings.', 'error')
    
    return redirect(url_for('dashboard'))


@app.route('/close-trade/<int:trade_id>', methods=['POST'])
@login_required
@require_license
def close_trade(trade_id):
    trade = Trade.query.get_or_404(trade_id)
    
    # Verify ownership
    if trade.user_id != current_user.id:
        flash('Unauthorized', 'error')
        return redirect(url_for('dashboard'))
    
    if trade.status != 'open':
        flash('Trade is already closed', 'error')
        return redirect(url_for('dashboard'))
    
    # Close trade
    engine = TradingEngine(current_user.id)
    current_price = engine._get_current_price(trade.currency_pair)
    engine._close_trade(trade, current_price)
    db.session.commit()
    
    flash(f'Trade closed. P/L: ${trade.profit_loss:.2f}', 'success')
    return redirect(url_for('dashboard'))


# API endpoints for AJAX
@app.route('/api/account-summary')
@login_required
def api_account_summary():
    engine = TradingEngine(current_user.id)
    summary = engine.get_account_summary()
    
    # Convert trades to dict
    trades_data = [{
        'id': t.id,
        'currency_pair': t.currency_pair,
        'trade_type': t.trade_type,
        'entry_price': t.entry_price,
        'lot_size': t.lot_size,
        'profit_loss': t.profit_loss,
        'opened_at': t.opened_at.isoformat()
    } for t in summary['trades']]
    
    summary['trades'] = trades_data
    return jsonify(summary)


@app.route('/api/forex-data/<currency_pair>')
@login_required
def api_forex_data(currency_pair):
    forex_provider = get_forex_provider()
    data = forex_provider.get_forex_intraday(currency_pair[:3], currency_pair[3:])
    return jsonify(data)


@app.route('/api/market-signal/<currency_pair>')
@login_required
def api_market_signal(currency_pair):
    forex_provider = get_forex_provider()
    signal = forex_provider.analyze_signal(currency_pair)
    return jsonify(signal)


# Error handlers
@app.errorhandler(404)
def not_found(e):
    return render_template('error.html', error='Page not found'), 404


@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error='Server error'), 500
