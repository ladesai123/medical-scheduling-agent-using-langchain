"""
Simple Google Gemini API client when the google-generativeai package is not available.
"""
import json
import urllib.request
import urllib.parse
import urllib.error
import time
import random
import logging

logger = logging.getLogger(__name__)


class SimpleGeminiClient:
    """Simple Gemini API client using only standard library."""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
    
    def create_completion(self, model: str = "gemini-1.5-flash", messages: list = None, temperature: float = 0.7, max_tokens: int = 500, max_retries: int = 3):
        """Create a chat completion using the Gemini API with retry logic."""
        if messages is None:
            messages = []
            
        # Convert OpenAI-style messages to Gemini format
        # Gemini uses "contents" with "parts" instead of "messages"
        contents = []
        system_instruction = None
        
        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")
            
            if role == "system":
                # System messages become systemInstruction in Gemini
                system_instruction = content
            elif role == "user":
                contents.append({
                    "role": "user",
                    "parts": [{"text": content}]
                })
            elif role == "assistant":
                contents.append({
                    "role": "model",
                    "parts": [{"text": content}]
                })
        
        # Prepare the URL - use generateContent endpoint
        model_name = model if model.startswith("gemini-") else "gemini-1.5-flash"
        url = f"{self.base_url}/models/{model_name}:generateContent?key={self.api_key}"
        
        headers = {
            "Content-Type": "application/json"
        }
        
        # Prepare request data in Gemini format
        data = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
                "maxOutputTokens": max_tokens,
                "topP": 0.8,
                "topK": 10
            }
        }
        
        # Add system instruction if available
        if system_instruction:
            data["systemInstruction"] = {
                "parts": [{"text": system_instruction}]
            }
        
        
        # Make the API request with retry logic
        for attempt in range(max_retries + 1):
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
                    
                    # Convert Gemini response to OpenAI-like format for compatibility
                    openai_format = self._convert_to_openai_format(response_data)
                    logger.info(f"Gemini API call successful on attempt {attempt + 1}")
                    return openai_format
                    
            except urllib.error.HTTPError as e:
                error_body = e.read().decode('utf-8') if hasattr(e, 'read') else str(e)
                
                if e.code == 429:  # Rate limit exceeded
                    if attempt < max_retries:
                        # Exponential backoff with jitter
                        delay = (2 ** attempt) + random.uniform(0, 1)
                        logger.warning(f"Rate limit exceeded (attempt {attempt + 1}/{max_retries + 1}). Retrying in {delay:.2f} seconds...")
                        time.sleep(delay)
                        continue
                    else:
                        logger.error(f"Rate limit exceeded after {max_retries + 1} attempts")
                        raise Exception(f"Rate limit exceeded (429) - max retries reached: {error_body}")
                elif e.code == 401:
                    raise Exception(f"Authentication failed (401): Check your API key")
                elif e.code == 403:
                    raise Exception(f"Forbidden (403): {error_body}")
                else:
                    if attempt < max_retries and e.code >= 500:  # Server errors - retry
                        delay = (2 ** attempt) + random.uniform(0, 1)
                        logger.warning(f"Server error {e.code} (attempt {attempt + 1}/{max_retries + 1}). Retrying in {delay:.2f} seconds...")
                        time.sleep(delay)
                        continue
                    else:
                        raise Exception(f"Gemini API error {e.code}: {error_body}")
            except urllib.error.URLError as e:
                if attempt < max_retries:
                    delay = (2 ** attempt) + random.uniform(0, 1)
                    logger.warning(f"Network error (attempt {attempt + 1}/{max_retries + 1}). Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
                    continue
                else:
                    raise Exception(f"Network error after {max_retries + 1} attempts: {e}")
            except Exception as e:
                if attempt < max_retries:
                    delay = (2 ** attempt) + random.uniform(0, 1)
                    logger.warning(f"Request failed (attempt {attempt + 1}/{max_retries + 1}). Retrying in {delay:.2f} seconds...")
                    time.sleep(delay)
                    continue
                else:
                    raise Exception(f"Request failed after {max_retries + 1} attempts: {e}")
        
        # This should never be reached, but just in case
        raise Exception("Unexpected error in retry logic")
    
    def _convert_to_openai_format(self, gemini_response):
        """Convert Gemini API response to OpenAI-compatible format."""
        try:
            # Extract text from Gemini response
            candidates = gemini_response.get("candidates", [])
            if not candidates:
                raise Exception("No candidates in Gemini response")
            
            candidate = candidates[0]
            content = candidate.get("content", {})
            parts = content.get("parts", [])
            
            if not parts:
                raise Exception("No parts in Gemini response content")
            
            text = parts[0].get("text", "")
            
            # Create OpenAI-compatible response structure
            openai_response = {
                "id": f"gemini-{hash(str(gemini_response)) % 10000000}",
                "object": "chat.completion",
                "created": 1234567890,  # Placeholder timestamp
                "model": "gemini-1.5-flash",
                "choices": [
                    {
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": text
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": {
                    "prompt_tokens": 0,  # Gemini doesn't provide token counts in the same way
                    "completion_tokens": 0,
                    "total_tokens": 0
                }
            }
            
            return openai_response
            
        except Exception as e:
            raise Exception(f"Error converting Gemini response: {e}")


class SimpleGeminiResponse:
    """Simple wrapper to mimic OpenAI response structure."""
    
    def __init__(self, response_data):
        self.choices = [SimpleChoice(choice) for choice in response_data.get("choices", [])]
        self.id = response_data.get("id", "")
        self.object = response_data.get("object", "chat.completion")
        self.created = response_data.get("created", 0)
        self.model = response_data.get("model", "gemini-1.5-flash")


class SimpleChoice:
    """Simple wrapper for Gemini choice structure."""
    
    def __init__(self, choice_data):
        self.index = choice_data.get("index", 0)
        self.message = SimpleMessage(choice_data.get("message", {}))
        self.finish_reason = choice_data.get("finish_reason", "stop")


class SimpleMessage:
    """Simple wrapper for Gemini message structure."""
    
    def __init__(self, message_data):
        self.role = message_data.get("role", "assistant")
        self.content = message_data.get("content", "")


if __name__ == "__main__":
    # Test the simple client (requires valid API key)
    import os
    
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        try:
            client = SimpleGeminiClient(api_key)
            messages = [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, how are you?"}
            ]
            
            response_data = client.create_completion("gemini-1.5-flash", messages)
            response = SimpleGeminiResponse(response_data)
            
            print("Response:", response.choices[0].message.content)
            
        except Exception as e:
            print(f"Error testing simple Gemini client: {e}")
    else:
        print("No API key found for testing")