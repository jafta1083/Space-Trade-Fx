import json
import logging
import sys
from datetime import datetime
from loguru import logger   
from loguru._logger import Logger
from utils import __init__Logger
from utils.status import status_code


class Custom_Logger(Logger):
    def __init__(self, *args, **kwargs):
        super("Connect").__init__(*args, **kwargs)
        self._logger = logger   # type: ignore
        self._logger.remove()  # type: ignore
        self._logger.add(
            sys.stderr,
            format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
            level="DEBUG",
            colorize=True,
        )
        self._logger.add(
            "space_trading_fx.log",
            format="{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}",
            level="DEBUG",
            rotation="1 MB",
            retention="10 days",
            compression="zip",
        )
        
        
   
        
        
    def log(self, message, level= "INFO"):
        log_data = {
            "message": message,
            "Level": level,
            "timestamp" : self.get_current_timestamp(),
            }
        
        self.send_log_to_site(log_data)
            
    def send_log_to_site(self, log_data):
        try: 
            response = __init__Logger.post(self.endpoint,headers =  self.headers, data) = json.dumps(log_data)
            if response.status_code == 200:
                print("Log successfully sent to site: {log_data}")
                
            else:
                print(f"Failed to send log:{response.status_code}")
        
        except Exception as e:
            print(f"Error to sending log: {str(e)}")
            
    def get_current_timestamp(self):
        
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
               
            
logger = Custom_Logger(endpoint = "https://space-trading-fx.com/log")


logger.log("API conected successfully.", level= "INFO")
logger.log("User logged in successfully.", level= "INFO")
logger.log("API failed due to timeout.",level="ERROR")                
logger.info("logging Information.",level= "INFO")