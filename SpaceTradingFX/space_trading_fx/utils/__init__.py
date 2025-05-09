import json
import sys
import logger
from SpaceTradingFX.space_trading_fx.utils.logger import log
from utils.status import *
from loguru import logger as loguru_logger

# Configure the logger when the module is loaded
log_file = "space_trading_fx.log"
loguru_logger.remove()
loguru_logger.add(sys.stderr, format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}", level="DEBUG", colorize=True)
loguru_logger.add(log_file, format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}", level="DEBUG", rotation="1 MB", retention="10 days", compression="zip")

# Function to get user profile
def perfil(api_endpoint, user_id, api_key, retries=3, timeout=10):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    params = {
        "user_id": user_id
    }

    for attempt in range(retries):
        try:
            response = logger.get(api_endpoint, headers=headers, params=params, timeout=timeout)

            if response.status_code() == 200:
                profile_data = response.json()
                log(f"Profile data retrieved for user {user_id}.", level="INFO")
                return profile_data
            else:
                log(f"Failed to retrieve profile for user {user_id}. Status code: {response.status_code()}", level="ERROR")
                return None

        except logger.exceptions.Timeout:
            log(f"Request timed out for user {user_id}, attempt {attempt + 1}.", level="WARNING")

        except logger.exceptions.RequestException as e:
            log(f"Request failed for user {user_id}: {str(e)}", level="ERROR")

    log(f"Max retries reached for user {user_id}, profile retrieval failed.", level="ERROR")
    return None

# Optional: Only runs when you directly call this file
if __name__ == "__main__":
    profile = perfil(
        api_endpoint="https://space-trading-fx.com/logs/profile",
        user_id="username",
        api_key="abc123-jafta-key"
    )
    if profile:
        print(json.dumps(profile, indent=2))
    else:
        print("Failed to fetch user profile.")
