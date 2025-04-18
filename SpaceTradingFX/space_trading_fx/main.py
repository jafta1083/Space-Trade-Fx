# from space_trading_fx.core.strategy_engine import run_strategy
from space_trading_fx.core.signal_reader import read_signals

# from config.settings import EMAIL
# from utils.logger import log

# run_strategy()



# print(f"Using bot with email: {EMAIL}")
# log("Bot started")




signals = read_signals()

for signal in signals:
    print(f"{signal['action']} signal for {signal['symbol']} at {signal['price']}")
    