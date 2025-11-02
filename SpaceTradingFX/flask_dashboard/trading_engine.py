import os
from datetime import datetime
from app import db
from models import Trade, TradingSignal, TradingPreference
from forex_data import get_forex_provider
import logging

logger = logging.getLogger(__name__)


class TradingEngine:
    """Main trading bot engine"""
    
    def __init__(self, user_id):
        self.user_id = user_id
        self.forex_provider = get_forex_provider()
        self.preferences = TradingPreference.query.filter_by(user_id=user_id).first()
        
        if not self.preferences:
            # Create default preferences
            self.preferences = TradingPreference(
                user_id=user_id,
                currency_pairs=['EURUSD', 'GBPUSD', 'USDJPY'],
                timeframe='1H',
                risk_percentage=1.0,
                max_concurrent_trades=3,
                trading_enabled=False
            )
            db.session.add(self.preferences)
            db.session.commit()
    
    def analyze_markets(self):
        """Analyze all configured currency pairs"""
        signals = []
        
        for currency_pair in self.preferences.currency_pairs:
            try:
                signal_data = self.forex_provider.analyze_signal(currency_pair)
                
                # Create signal record
                signal = TradingSignal(
                    currency_pair=currency_pair,
                    signal_type=signal_data['signal'],
                    strength=signal_data['strength'],
                    price=self._get_current_price(currency_pair),
                    indicators=signal_data['indicators'],
                    timeframe=self.preferences.timeframe
                )
                db.session.add(signal)
                signals.append(signal_data)
                
            except Exception as e:
                logger.error(f"Error analyzing {currency_pair}: {e}")
        
        db.session.commit()
        return signals
    
    def _get_current_price(self, currency_pair):
        """Get current price for a currency pair"""
        try:
            data = self.forex_provider.get_forex_intraday(
                currency_pair[:3],
                currency_pair[3:],
                self.preferences.timeframe
            )
            
            if data['success'] and data['data']:
                return data['data'][0]['close']
            else:
                return 1.0  # Default fallback
                
        except Exception:
            return 1.0
    
    def execute_trade(self, currency_pair, signal_type, signal_data):
        """Execute a trade based on signal"""
        
        # Check if trading is enabled
        if not self.preferences.trading_enabled:
            logger.info(f"Trading disabled for user {self.user_id}")
            return None
        
        # Check concurrent trades limit
        active_trades = Trade.query.filter_by(
            user_id=self.user_id,
            status='open'
        ).count()
        
        if active_trades >= self.preferences.max_concurrent_trades:
            logger.info(f"Max concurrent trades reached for user {self.user_id}")
            return None
        
        # Calculate position size based on risk
        lot_size = self._calculate_lot_size()
        entry_price = self._get_current_price(currency_pair)
        
        # Calculate stop loss and take profit
        stop_loss, take_profit = self._calculate_sl_tp(entry_price, signal_type)
        
        # Create trade record
        trade = Trade(
            user_id=self.user_id,
            currency_pair=currency_pair,
            trade_type=signal_type,
            entry_price=entry_price,
            lot_size=lot_size,
            stop_loss=stop_loss,
            take_profit=take_profit,
            status='open',
            signal_data=signal_data
        )
        
        db.session.add(trade)
        db.session.commit()
        
        # In production, send order to MetaTrader here
        # self._send_to_mt5(trade)
        
        logger.info(f"Trade executed: {trade.id} - {currency_pair} {signal_type}")
        return trade
    
    def _calculate_lot_size(self):
        """Calculate lot size based on risk percentage"""
        # Simplified calculation - in production, use account balance
        base_lot = 0.01
        risk_multiplier = self.preferences.risk_percentage / 1.0
        return round(base_lot * risk_multiplier, 2)
    
    def _calculate_sl_tp(self, entry_price, signal_type):
        """Calculate stop loss and take profit"""
        # Simple 1:2 risk-reward ratio
        sl_pips = 20  # 20 pips stop loss
        tp_pips = 40  # 40 pips take profit
        
        pip_value = 0.0001  # For most pairs
        
        if signal_type == 'BUY':
            stop_loss = entry_price - (sl_pips * pip_value)
            take_profit = entry_price + (tp_pips * pip_value)
        else:  # SELL
            stop_loss = entry_price + (sl_pips * pip_value)
            take_profit = entry_price - (tp_pips * pip_value)
        
        return round(stop_loss, 5), round(take_profit, 5)
    
    def update_open_trades(self):
        """Update all open trades with current prices"""
        open_trades = Trade.query.filter_by(
            user_id=self.user_id,
            status='open'
        ).all()
        
        for trade in open_trades:
            current_price = self._get_current_price(trade.currency_pair)
            
            # Calculate profit/loss
            if trade.trade_type == 'BUY':
                price_diff = current_price - trade.entry_price
            else:  # SELL
                price_diff = trade.entry_price - current_price
            
            # Calculate P/L (simplified)
            trade.profit_loss = round(price_diff * trade.lot_size * 100000, 2)
            
            # Check stop loss and take profit
            if self._check_exit_conditions(trade, current_price):
                self._close_trade(trade, current_price)
        
        db.session.commit()
    
    def _check_exit_conditions(self, trade, current_price):
        """Check if trade should be closed"""
        if trade.trade_type == 'BUY':
            if trade.stop_loss and current_price <= trade.stop_loss:
                return True
            if trade.take_profit and current_price >= trade.take_profit:
                return True
        else:  # SELL
            if trade.stop_loss and current_price >= trade.stop_loss:
                return True
            if trade.take_profit and current_price <= trade.take_profit:
                return True
        
        return False
    
    def _close_trade(self, trade, exit_price):
        """Close a trade"""
        trade.exit_price = exit_price
        trade.status = 'closed'
        trade.closed_at = datetime.now()
        
        # Calculate final P/L
        if trade.trade_type == 'BUY':
            price_diff = exit_price - trade.entry_price
        else:
            price_diff = trade.entry_price - exit_price
        
        trade.profit_loss = round(price_diff * trade.lot_size * 100000, 2)
        
        logger.info(f"Trade closed: {trade.id} - P/L: {trade.profit_loss}")
    
    def get_account_summary(self):
        """Get trading account summary"""
        all_trades = Trade.query.filter_by(user_id=self.user_id).all()
        
        total_trades = len(all_trades)
        winning_trades = len([t for t in all_trades if t.profit_loss > 0])
        losing_trades = len([t for t in all_trades if t.profit_loss < 0])
        total_profit = sum([t.profit_loss for t in all_trades if t.status == 'closed'])
        
        active_trades = [t for t in all_trades if t.status == 'open']
        
        return {
            'total_trades': total_trades,
            'winning_trades': winning_trades,
            'losing_trades': losing_trades,
            'win_rate': (winning_trades / total_trades * 100) if total_trades > 0 else 0,
            'total_profit': total_profit,
            'active_trades': len(active_trades),
            'trades': active_trades
        }


# MetaTrader 5 integration (placeholder for future implementation)
class MT5Connector:
    """Connector for MetaTrader 5 terminal"""
    
    def __init__(self, account, password, server):
        self.account = account
        self.password = password
        self.server = server
        self.connected = False
    
    def connect(self):
        """Connect to MT5 terminal"""
        # In production, use MetaTrader5 library
        # import MetaTrader5 as mt5
        # self.connected = mt5.initialize()
        # mt5.login(self.account, self.password, self.server)
        logger.info(f"MT5 connection placeholder - would connect to {self.server}")
        return True
    
    def send_order(self, trade):
        """Send order to MT5"""
        # In production:
        # request = {
        #     "action": mt5.TRADE_ACTION_DEAL,
        #     "symbol": trade.currency_pair,
        #     "volume": trade.lot_size,
        #     "type": mt5.ORDER_TYPE_BUY if trade.trade_type == 'BUY' else mt5.ORDER_TYPE_SELL,
        #     "price": trade.entry_price,
        #     "sl": trade.stop_loss,
        #     "tp": trade.take_profit,
        #     "magic": 234000,
        #     "comment": f"SpaceTradingFX-{trade.id}",
        # }
        # result = mt5.order_send(request)
        logger.info(f"MT5 order placeholder - would send: {trade.currency_pair} {trade.trade_type}")
        return {"ticket": "123456"}
    
    def close_order(self, ticket):
        """Close an open order"""
        logger.info(f"MT5 close placeholder - would close ticket: {ticket}")
        return True
