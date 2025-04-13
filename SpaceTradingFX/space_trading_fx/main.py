from core.strategy_engine import run_strategy
from config.settings import EMAIL
from utils.logger import log

run_strategy()



print(f"Using bot with email: {EMAIL}")
log("Bot started")

