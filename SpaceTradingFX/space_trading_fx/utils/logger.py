import json
import logging
import sys
from datetime import datetime
from loguru import logger as loguru_logger
import requests

class CustomLogger:
    def __init__(self, endpoint="https://space-trading-fx.com/log"):
        self.endpoint = endpoint
        self.headers = {
            "Content-Type": "application/json"
        }

        # Configure Loguru logger
        loguru_logger.remove()
        loguru_logger.add(
            sys.stderr,
            format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
            level="DEBUG",
            colorize=True,
        )
        loguru_logger.add(
            "space_trading_fx.log",
            format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
            level="DEBUG",
            rotation="1 MB",
            retention="10 days",
            compression="zip",
        )

    def log(self, message, level="INFO"):
        timestamp = self.get_current_timestamp()
        log_data = {
            "message": message,
            "level": level,
            "timestamp": timestamp,
        }
        loguru_logger.log(level, f"{message} @ {timestamp}")
        self.send_log_to_site(log_data)

    def send_log_to_site(self, log_data):
        try:
            response = requests.post(self.endpoint, headers=self.headers, data=json.dumps(log_data), timeout=5)
            if response.status_code == 200:
                print(f"✅ Log successfully sent to site: {log_data}")
            else:
                print(f"❌ Failed to send log: {response.status_code}")
        except Exception as e:
            print(f"❌ Error sending log: {str(e)}")

    def get_current_timestamp(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# 👇 Main function for testing or standalone run
def main():
    logger = CustomLogger()
    logger.log("API connected successfully.", level="INFO")
    logger.log("User logged in successfully.", level="INFO")
    logger.log("API failed due to timeout.", level="ERROR")

# 👇 Will only run if file is executed directly
if __name__ == "__main__":
    main()
