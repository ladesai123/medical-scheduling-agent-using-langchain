"""
Simple OpenAI API client when the openai package is not available.
"""
import json
import urllib.request
import urllib.parse
import urllib.error


class SimpleOpenAIClient:
    """Simple OpenAI API client using only standard library."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.openai.com/v1"
    
    def create_completion(self, model: str, messages: list, temperature: float = 0.7, max_tokens: int = 500):
        """Create a chat completion using the OpenAI API."""
        url = f"{self.base_url}/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        try:
            # Create request
            request = urllib.request.Request(
                url,
                data=json.dumps(data).encode('utf-8'),
                headers=headers,
                method='POST'
            )
            
            # Make request
            with urllib.request.urlopen(request, timeout=30) as response:
                response_data = json.loads(response.read().decode('utf-8'))
                return response_data
                
        except urllib.error.HTTPError as e:
            error_body = e.read().decode('utf-8') if hasattr(e, 'read') else str(e)
            if e.code == 429:
                raise Exception(f"Rate limit exceeded (429): {error_body}")
            elif e.code == 401:
                raise Exception(f"Authentication failed (401): Check your API key")
            elif e.code == 403:
                raise Exception(f"Forbidden (403): {error_body}")
            else:
                raise Exception(f"OpenAI API error {e.code}: {error_body}")
        except urllib.error.URLError as e:
            raise Exception(f"Network error: {e}")
        except Exception as e:
            raise Exception(f"Request failed: {e}")


class SimpleOpenAIResponse:
    """Simple wrapper to mimic OpenAI response structure."""
    
    def __init__(self, response_data):
        self.choices = []
        if 'choices' in response_data:
            for choice in response_data['choices']:
                self.choices.append(SimpleChoice(choice))


class SimpleChoice:
    """Simple wrapper for OpenAI choice structure."""
    
    def __init__(self, choice_data):
        self.message = SimpleMessage(choice_data.get('message', {}))


class SimpleMessage:
    """Simple wrapper for OpenAI message structure."""
    
    def __init__(self, message_data):
        self.content = message_data.get('content', '')


if __name__ == "__main__":
    # Test the simple client (requires valid API key)
    import os
    
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        try:
            client = SimpleOpenAIClient(api_key)
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, how are you?"}
            ]
            
            response_data = client.create_completion("gpt-3.5-turbo", messages)
            response = SimpleOpenAIResponse(response_data)
            
            print("Response:", response.choices[0].message.content)
            
        except Exception as e:
            print(f"Error testing simple OpenAI client: {e}")
    else:
        print("No API key found for testing")