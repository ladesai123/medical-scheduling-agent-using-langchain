"""
Configuration module for the medical scheduling agent.
Handles environment variables and initializes the language model.
"""
import os
import logging

logger = logging.getLogger(__name__)


def load_environment():
    """Load environment variables from .env file if available."""
    try:
        # Try to import python-dotenv if available
        from dotenv import load_dotenv
        load_dotenv()
        logger.info("Environment variables loaded from .env file")
    except ImportError:
        # Use our simple dotenv loader as fallback
        try:
            from app.utils.simple_dotenv import load_dotenv
            if load_dotenv():
                logger.info("Environment variables loaded using simple dotenv loader")
            else:
                logger.warning("Using system environment variables only")
        except Exception as e:
            logger.warning(f"Could not load .env file: {e}")
    except Exception as e:
        logger.warning(f"Could not load .env file: {e}")


def get_openai_api_key():
    """Get OpenAI API key from environment."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY not found in environment variables. "
            "Please set it in your .env file or system environment."
        )
    return api_key


def get_llm():
    """Initialize and return the language model."""
    try:
        # Load environment first
        load_environment()
        
        # Try to use OpenAI if available
        try:
            from openai import OpenAI
            api_key = get_openai_api_key()
            
            # Create OpenAI client with proper initialization
            client = OpenAI(api_key=api_key)
            logger.info("OpenAI client initialized successfully")
            return MockLLMWithOpenAI(client)
            
        except ImportError:
            # Try our simple OpenAI client
            try:
                from app.utils.simple_openai import SimpleOpenAIClient
                api_key = get_openai_api_key()
                client = SimpleOpenAIClient(api_key)
                logger.info("Simple OpenAI client initialized successfully")
                return MockLLMWithSimpleOpenAI(client)
            except Exception as e:
                logger.warning(f"Could not initialize simple OpenAI client: {e}")
                logger.info("Falling back to mock LLM")
                return MockLLM()
        except Exception as e:
            logger.error(f"Error initializing OpenAI client: {e}")
            logger.info("Falling back to mock LLM")
            return MockLLM()
            
    except Exception as e:
        logger.error(f"Error in get_llm: {e}")
        logger.info("Using mock LLM as fallback")
        return MockLLM()


class MockLLM:
    """Mock LLM for testing when OpenAI is not available."""
    
    def __init__(self):
        self.model_name = "mock-llm"
        logger.info("MockLLM initialized")
    
    def generate_response(self, prompt: str) -> str:
        """Generate a mock response based on the prompt."""
        prompt_lower = prompt.lower()
        
        if "hello" in prompt_lower or "hi" in prompt_lower:
            return "Hello! I'm your medical scheduling assistant. How can I help you today?"
        
        elif "appointment" in prompt_lower:
            if "schedule" in prompt_lower or "book" in prompt_lower:
                return ("I'd be happy to help you schedule an appointment. "
                       "Could you please provide me with your name and preferred date/time?")
            elif "cancel" in prompt_lower:
                return "I can help you cancel your appointment. Could you please provide your name and appointment details?"
        
        elif "doctor" in prompt_lower:
            return ("We have several doctors available. Could you tell me what type of specialist "
                   "you're looking for or if you have a preference?")
        
        elif "insurance" in prompt_lower:
            return "I'll need to collect your insurance information. What insurance provider do you have?"
        
        elif "new patient" in prompt_lower:
            return ("As a new patient, I'll need to collect some additional information from you. "
                   "New patient appointments are typically 60 minutes long.")
        
        elif "returning patient" in prompt_lower or "existing patient" in prompt_lower:
            return "Welcome back! Returning patient appointments are typically 30 minutes. When would you like to schedule?"
        
        else:
            return ("I'm here to help with medical appointment scheduling. "
                   "You can ask me to schedule an appointment, check availability, "
                   "or provide information about our services.")


class MockLLMWithSimpleOpenAI:
    """Enhanced mock LLM that uses our simple OpenAI client."""
    
    def __init__(self, simple_openai_client):
        self.client = simple_openai_client
        self.model_name = "gpt-3.5-turbo"
        logger.info("MockLLMWithSimpleOpenAI initialized with simple OpenAI client")
    
    def generate_response(self, prompt: str) -> str:
        """Generate a response using our simple OpenAI client."""
        try:
            from app.utils.simple_openai import SimpleOpenAIResponse
            
            system_message = """You are a helpful medical appointment scheduling assistant. 
            You help patients schedule appointments, collect necessary information, and answer questions about the medical practice.
            Be professional, friendly, and efficient. Always ask for necessary information step by step.
            
            Key points:
            - New patients need 60-minute appointments
            - Returning patients need 30-minute appointments  
            - Collect name, preferred date/time, doctor preference, insurance information
            - Be helpful with scheduling conflicts and alternatives"""
            
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ]
            
            response_data = self.client.create_completion(
                model=self.model_name,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            response = SimpleOpenAIResponse(response_data)
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error calling simple OpenAI client: {e}")
            # Fallback to mock responses
            fallback_llm = MockLLM()
            return fallback_llm.generate_response(prompt)


class MockLLMWithOpenAI:
    """Enhanced mock LLM that uses OpenAI when available."""
    
    def __init__(self, openai_client):
        self.client = openai_client
        self.model_name = "gpt-3.5-turbo"
        logger.info("MockLLMWithOpenAI initialized with OpenAI client")
    
    def generate_response(self, prompt: str) -> str:
        """Generate a response using OpenAI."""
        try:
            system_message = """You are a helpful medical appointment scheduling assistant. 
            You help patients schedule appointments, collect necessary information, and answer questions about the medical practice.
            Be professional, friendly, and efficient. Always ask for necessary information step by step.
            
            Key points:
            - New patients need 60-minute appointments
            - Returning patients need 30-minute appointments  
            - Collect name, preferred date/time, doctor preference, insurance information
            - Be helpful with scheduling conflicts and alternatives"""
            
            messages = [
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt}
            ]
            
            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error calling OpenAI API: {e}")
            # Fallback to mock responses
            fallback_llm = MockLLM()
            return fallback_llm.generate_response(prompt)


# Configuration constants
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-3.5-turbo")
DEBUG_MODE = os.getenv("DEBUG_MODE", "False").lower() == "true"

if __name__ == "__main__":
    # Test the configuration
    print("Testing configuration...")
    try:
        llm = get_llm()
        response = llm.generate_response("Hello, I need to schedule an appointment.")
        print(f"LLM Response: {response}")
    except Exception as e:
        print(f"Error: {e}")