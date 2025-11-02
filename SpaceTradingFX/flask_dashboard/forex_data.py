import requests
import os
from datetime import datetime, timedelta


class ForexDataProvider:
    """Fetches forex data and technical indicators"""
    
    def __init__(self):
        # Using Alpha Vantage API (free tier)
        self.api_key = os.environ.get('ALPHA_VANTAGE_API_KEY', 'demo')
        self.base_url = 'https://www.alphavantage.co/query'
    
    def get_forex_intraday(self, from_currency='EUR', to_currency='USD', interval='5min'):
        """Get intraday forex data"""
        try:
            params = {
                'function': 'FX_INTRADAY',
                'from_symbol': from_currency,
                'to_symbol': to_currency,
                'interval': interval,
                'apikey': self.api_key,
                'outputsize': 'compact'
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            data = response.json()
            
            if 'Time Series FX (5min)' in data or f'Time Series FX ({interval})' in data:
                time_series_key = list(data.keys())[1]  # Get the time series key
                time_series = data[time_series_key]
                
                # Convert to list of candlesticks
                candlesticks = []
                for timestamp, values in time_series.items():
                    candlesticks.append({
                        'time': timestamp,
                        'open': float(values['1. open']),
                        'high': float(values['2. high']),
                        'low': float(values['3. low']),
                        'close': float(values['4. close'])
                    })
                
                return {'success': True, 'data': candlesticks}
            else:
                return {'success': False, 'error': 'Invalid response from API'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_rsi(self, from_currency='EUR', to_currency='USD', interval='daily', time_period=14):
        """Get RSI indicator"""
        try:
            params = {
                'function': 'RSI',
                'symbol': f'{from_currency}{to_currency}',
                'interval': interval,
                'time_period': time_period,
                'series_type': 'close',
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            data = response.json()
            
            if 'Technical Analysis: RSI' in data:
                rsi_data = data['Technical Analysis: RSI']
                latest_timestamp = list(rsi_data.keys())[0]
                latest_rsi = float(rsi_data[latest_timestamp]['RSI'])
                
                return {'success': True, 'rsi': latest_rsi, 'timestamp': latest_timestamp}
            else:
                return {'success': False, 'error': 'Could not fetch RSI data'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_macd(self, from_currency='EUR', to_currency='USD', interval='daily'):
        """Get MACD indicator"""
        try:
            params = {
                'function': 'MACD',
                'symbol': f'{from_currency}{to_currency}',
                'interval': interval,
                'series_type': 'close',
                'apikey': self.api_key
            }
            
            response = requests.get(self.base_url, params=params, timeout=10)
            data = response.json()
            
            if 'Technical Analysis: MACD' in data:
                macd_data = data['Technical Analysis: MACD']
                latest_timestamp = list(macd_data.keys())[0]
                latest_macd = {
                    'macd': float(macd_data[latest_timestamp]['MACD']),
                    'signal': float(macd_data[latest_timestamp]['MACD_Signal']),
                    'hist': float(macd_data[latest_timestamp]['MACD_Hist']),
                    'timestamp': latest_timestamp
                }
                
                return {'success': True, 'data': latest_macd}
            else:
                return {'success': False, 'error': 'Could not fetch MACD data'}
                
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def analyze_signal(self, currency_pair):
        """Analyze multiple indicators to generate trading signal"""
        from_curr, to_curr = currency_pair[:3], currency_pair[3:]
        
        # Get indicators
        rsi_result = self.get_rsi(from_curr, to_curr)
        macd_result = self.get_macd(from_curr, to_curr)
        
        signal = {
            'currency_pair': currency_pair,
            'timestamp': datetime.now().isoformat(),
            'indicators': {},
            'signal': 'NEUTRAL',
            'strength': 0
        }
        
        if rsi_result['success']:
            rsi = rsi_result['rsi']
            signal['indicators']['rsi'] = rsi
            
            # RSI signals
            if rsi < 30:
                signal['signal'] = 'BUY'
                signal['strength'] += 30
            elif rsi > 70:
                signal['signal'] = 'SELL'
                signal['strength'] += 30
        
        if macd_result['success']:
            macd_data = macd_result['data']
            signal['indicators']['macd'] = macd_data
            
            # MACD crossover signals
            if macd_data['macd'] > macd_data['signal'] and macd_data['hist'] > 0:
                if signal['signal'] == 'BUY' or signal['signal'] == 'NEUTRAL':
                    signal['signal'] = 'BUY'
                    signal['strength'] += 20
            elif macd_data['macd'] < macd_data['signal'] and macd_data['hist'] < 0:
                if signal['signal'] == 'SELL' or signal['signal'] == 'NEUTRAL':
                    signal['signal'] = 'SELL'
                    signal['strength'] += 20
        
        # Normalize strength to 0-100
        signal['strength'] = min(100, signal['strength'])
        
        return signal


# Mock data provider for development/testing
class MockForexDataProvider:
    """Provides mock forex data for testing without API calls"""
    
    def get_forex_intraday(self, from_currency='EUR', to_currency='USD', interval='5min'):
        """Return mock forex data"""
        import random
        
        base_price = 1.0850
        candlesticks = []
        
        for i in range(100):
            timestamp = (datetime.now() - timedelta(minutes=5*i)).strftime('%Y-%m-%d %H:%M:%S')
            price_change = random.uniform(-0.0010, 0.0010)
            
            open_price = base_price + price_change
            close_price = open_price + random.uniform(-0.0005, 0.0005)
            high_price = max(open_price, close_price) + random.uniform(0, 0.0003)
            low_price = min(open_price, close_price) - random.uniform(0, 0.0003)
            
            candlesticks.append({
                'time': timestamp,
                'open': round(open_price, 5),
                'high': round(high_price, 5),
                'low': round(low_price, 5),
                'close': round(close_price, 5)
            })
            
            base_price = close_price
        
        return {'success': True, 'data': candlesticks}
    
    def analyze_signal(self, currency_pair):
        """Generate mock trading signal"""
        import random
        
        signals = ['BUY', 'SELL', 'NEUTRAL']
        signal_type = random.choice(signals)
        
        return {
            'currency_pair': currency_pair,
            'timestamp': datetime.now().isoformat(),
            'indicators': {
                'rsi': random.uniform(30, 70),
                'macd': {
                    'macd': random.uniform(-0.001, 0.001),
                    'signal': random.uniform(-0.001, 0.001),
                    'hist': random.uniform(-0.0005, 0.0005)
                }
            },
            'signal': signal_type,
            'strength': random.uniform(40, 90)
        }


# Use real or mock provider based on API key availability
def get_forex_provider():
    """Get the appropriate forex data provider"""
    api_key = os.environ.get('ALPHA_VANTAGE_API_KEY')
    if api_key and api_key != 'demo':
        return ForexDataProvider()
    else:
        return MockForexDataProvider()
