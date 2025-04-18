import json
import logger
from utils.status import status_code

class __init__Logger:
   
    def __init__(self, endpoint):
       self.endpoint = endpoint
       self.headers  = {"CONTENT_TYPE" : "application/json" }
       
    def perfil(api_endpoint,user_id, api_key , retries=3, timeout=10):
        
        
        headers = {
            "AUTHORIZATION": f"{api_key}",
            "CONTENT_TYPE": "application/json",
            }
               
        user_id_key = {
            "user_id": {user_id}
        }
        
        
        for attempt in range(retries):
            try:
                response = __init__Logger.get(api_endpoint, headers=headers, user_id_key=user_id_key, timeout=timeout)
                
                if response.status_code == 200:
                    profile_data = response.json()
                    
                    logger.log(f"Profile data retrieved for user {user_id}.", level="INFO")
                    return profile_data
                
                else:
                    logger.log(f"Failed to retrieve profile data for user {user_id}.  Status code: {response.status_code}", level="ERROR")
                    return None
                
            except __init__Logger.exceptions.Timeout:
                logger.log(f"Request time out for user {user_id}, attempt {attempt + 1}.", level="WARNING")    
                
            except __init__Logger.exceptions.RequestException as e:
                logger.log(f"Request failed for user {user_id}: {str(e)}", level="ERROR")
                
        logger.log(f"Max retries reached for user {user_id}, profile retrieval failed.", level="ERROR")               
        return None
    
    
    
    
    user_profile = perfil(api_endpoint="https://space-trading-fx.com/logs/profile",
                          user_id= "username",
                          api_key= "abc123-jafta-key")
                          
          