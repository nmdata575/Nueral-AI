# jan_ai_integration.py
import requests
import json
from typing import Dict, Any

class JanAI:
    def __init__(self, api_key: str, base_url: str = "https://0.0.0.0:1337"):
        """
        Initialize the Jan AI client
        
        Args:
            api_key (str): Your Jan AI API key
            base_url (str): Base URL for the Jan AI API
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
    
    def chat(self, messages: list, model: str = "gpt-4", temperature: float = 0.7) -> Dict[str, Any]:
        """
        Send a message to Jan AI chat
        
        Args:
            messages (list): List of message objects with 'role' and 'content'
            model (str): The model to use
            temperature (float): Sampling temperature
            
        Returns:
            Dict containing the response
        """
        url = f"{self.base_url}/chat/completions"
        
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e)}

# Example usage:
if __name__ == "__main__":
    # This file can be used as a module
    pass
