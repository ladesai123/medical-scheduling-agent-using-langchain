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


def get_gemini_api_key():
    """Get Gemini API key from environment."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY not found in environment variables. "
            "Please set it in your .env file or system environment."
        )
    return api_key


def get_preferred_provider():
    """Get the preferred AI provider from environment (gemini or openai)."""
    # Load environment first to ensure we have the latest values
    load_environment()
    provider = os.getenv("AI_PROVIDER", "gemini").lower()
    if provider not in ["gemini", "openai"]:
        logger.warning(f"Unknown AI_PROVIDER '{provider}', defaulting to 'gemini'")
        return "gemini"
    return provider


def get_llm():
    """Initialize and return the language model."""
    try:
        # Load environment first
        load_environment()
        
        # Get preferred provider
        provider = get_preferred_provider()
        logger.info(f"Using AI provider: {provider}")
        
        # Try to use LangChain agent first
        try:
            from app.agents.langchain_agent import LangChainMedicalAgent
            
            if provider == "gemini":
                try:
                    api_key = get_gemini_api_key()
                    # Create LangChain agent with Gemini
                    agent = LangChainMedicalAgent(api_key=api_key, provider="gemini")
                    logger.info("LangChain Medical Agent initialized successfully with Gemini")
                    return agent
                except Exception as e:
                    logger.warning(f"Gemini LangChain agent failed: {e}")
                    # Try OpenAI as fallback
                    try:
                        api_key = get_openai_api_key()
                        agent = LangChainMedicalAgent(api_key=api_key, provider="openai")
                        logger.info("LangChain Medical Agent initialized successfully with OpenAI fallback")
                        return agent
                    except Exception as e2:
                        logger.warning(f"OpenAI fallback also failed: {e2}")
            else:  # provider == "openai"
                try:
                    api_key = get_openai_api_key()
                    agent = LangChainMedicalAgent(api_key=api_key, provider="openai")
                    logger.info("LangChain Medical Agent initialized successfully with OpenAI")
                    return agent
                except Exception as e:
                    logger.warning(f"OpenAI LangChain agent failed: {e}")
                    # Try Gemini as fallback
                    try:
                        api_key = get_gemini_api_key()
                        agent = LangChainMedicalAgent(api_key=api_key, provider="gemini")
                        logger.info("LangChain Medical Agent initialized successfully with Gemini fallback")
                        return agent
                    except Exception as e2:
                        logger.warning(f"Gemini fallback also failed: {e2}")
            
        except Exception as e:
            logger.warning(f"LangChain agent failed: {e}")
        
        # Fall back to enhanced mock agent
        try:
            from app.agents.mock_langchain_agent import MockLangChainAgent
            agent = MockLangChainAgent()
            logger.info("MockLangChain Medical Agent initialized successfully")
            return agent
        except Exception as e:
            logger.warning(f"Mock LangChain agent failed: {e}")
        
        # Fall back to direct API clients
        if provider == "gemini":
            try:
                # Try google-generativeai package first
                try:
                    import google.generativeai as genai
                    api_key = get_gemini_api_key()
                    genai.configure(api_key=api_key)
                    model = genai.GenerativeModel('gemini-1.5-flash')
                    logger.info("Google GenerativeAI client initialized successfully")
                    return MockLLMWithGemini(model)
                except ImportError:
                    # Try our simple Gemini client
                    from app.utils.simple_gemini import SimpleGeminiClient
                    api_key = get_gemini_api_key()
                    client = SimpleGeminiClient(api_key)
                    logger.info("Simple Gemini client initialized successfully")
                    return MockLLMWithSimpleGemini(client)
            except Exception as e:
                logger.warning(f"Could not initialize Gemini client: {e}")
                # Try OpenAI as fallback
                try:
                    from openai import OpenAI
                    api_key = get_openai_api_key()
                    client = OpenAI(api_key=api_key)
                    logger.info("OpenAI client initialized successfully as fallback")
                    return MockLLMWithOpenAI(client)
                except Exception as e2:
                    logger.warning(f"OpenAI fallback failed: {e2}")
        else:  # provider == "openai"
            try:
                from openai import OpenAI
                api_key = get_openai_api_key()
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
            except Exception as e:
                logger.warning(f"Could not initialize OpenAI client: {e}")
                # Try Gemini as fallback
                try:
                    from app.utils.simple_gemini import SimpleGeminiClient
                    api_key = get_gemini_api_key()
                    client = SimpleGeminiClient(api_key)
                    logger.info("Simple Gemini client initialized successfully as fallback")
                    return MockLLMWithSimpleGemini(client)
                except Exception as e2:
                    logger.warning(f"Gemini fallback failed: {e2}")
        
        # Final fallback to mock LLM
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
        self.api_failed = True  # Mock LLM represents a failed API state
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


class MockLLMWithSimpleGemini:
    """Enhanced mock LLM that uses our simple Gemini client."""
    
    def __init__(self, simple_gemini_client):
        self.client = simple_gemini_client
        self.model_name = "gemini-1.5-flash"
        self.api_failed = False  # Track if API has failed
        self.fallback_llm = None
        logger.info("MockLLMWithSimpleGemini initialized with simple Gemini client")
    
    def generate_response(self, prompt: str) -> str:
        """Generate a response using our simple Gemini client."""
        # If API has already failed, use fallback directly
        if self.api_failed:
            if self.fallback_llm is None:
                self.fallback_llm = MockLLM()
            return self.fallback_llm.generate_response(prompt)
        
        try:
            from app.utils.simple_gemini import SimpleGeminiResponse
            
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
                max_tokens=500,
                max_retries=3  # Add retry logic for rate limiting
            )
            
            response = SimpleGeminiResponse(response_data)
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Error calling simple Gemini client: {e}")
            # Mark API as failed to avoid repeated attempts
            self.api_failed = True
            # Initialize fallback if not already done
            if self.fallback_llm is None:
                self.fallback_llm = MockLLM()
                logger.info("Switching to MockLLM due to API failure")
            return self.fallback_llm.generate_response(prompt)


class MockLLMWithGemini:
    """Enhanced mock LLM that uses Google GenerativeAI when available."""
    
    def __init__(self, gemini_model):
        self.model = gemini_model
        self.model_name = "gemini-1.5-flash"
        self.api_failed = False  # Track if API has failed
        self.fallback_llm = None
        logger.info("MockLLMWithGemini initialized with Google GenerativeAI model")
    
    def generate_response(self, prompt: str) -> str:
        """Generate a response using Google Gemini."""
        # If API has already failed, use fallback directly
        if self.api_failed:
            if self.fallback_llm is None:
                self.fallback_llm = MockLLM()
            return self.fallback_llm.generate_response(prompt)
        
        try:
            system_instruction = """You are a helpful medical appointment scheduling assistant. 
            You help patients schedule appointments, collect necessary information, and answer questions about the medical practice.
            Be professional, friendly, and efficient. Always ask for necessary information step by step.
            
            Key points:
            - New patients need 60-minute appointments
            - Returning patients need 30-minute appointments  
            - Collect name, preferred date/time, doctor preference, insurance information
            - Be helpful with scheduling conflicts and alternatives"""
            
            # Create a new model with system instruction
            import google.generativeai as genai
            model_with_system = genai.GenerativeModel(
                'gemini-1.5-flash',
                system_instruction=system_instruction
            )
            
            response = model_with_system.generate_content(prompt)
            return response.text
            
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            # Mark API as failed to avoid repeated attempts
            self.api_failed = True
            # Initialize fallback if not already done
            if self.fallback_llm is None:
                self.fallback_llm = MockLLM()
                logger.info("Switching to MockLLM due to API failure")
            return self.fallback_llm.generate_response(prompt)


class MockLLMWithSimpleOpenAI:
    """Enhanced mock LLM that uses our simple OpenAI client."""
    
    def __init__(self, simple_openai_client):
        self.client = simple_openai_client
        self.model_name = "gpt-3.5-turbo"
        self.api_failed = False  # Track if API has failed
        self.fallback_llm = None
        logger.info("MockLLMWithSimpleOpenAI initialized with simple OpenAI client")
    
    def generate_response(self, prompt: str) -> str:
        """Generate a response using our simple OpenAI client."""
        # If API has already failed, use fallback directly
        if self.api_failed:
            if self.fallback_llm is None:
                self.fallback_llm = MockLLM()
            return self.fallback_llm.generate_response(prompt)
        
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
            # Mark API as failed to avoid repeated attempts
            self.api_failed = True
            # Initialize fallback if not already done
            if self.fallback_llm is None:
                self.fallback_llm = MockLLM()
                logger.info("Switching to MockLLM due to API failure")
            return self.fallback_llm.generate_response(prompt)


class MockLLMWithOpenAI:
    """Enhanced mock LLM that uses OpenAI when available."""
    
    def __init__(self, openai_client):
        self.client = openai_client
        self.model_name = "gpt-3.5-turbo"
        self.api_failed = False  # Track if API has failed
        self.fallback_llm = None
        logger.info("MockLLMWithOpenAI initialized with OpenAI client")
    
    def generate_response(self, prompt: str) -> str:
        """Generate a response using OpenAI."""
        # If API has already failed, use fallback directly
        if self.api_failed:
            if self.fallback_llm is None:
                self.fallback_llm = MockLLM()
            return self.fallback_llm.generate_response(prompt)
        
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
            # Mark API as failed to avoid repeated attempts
            self.api_failed = True
            # Initialize fallback if not already done
            if self.fallback_llm is None:
                self.fallback_llm = MockLLM()
                logger.info("Switching to MockLLM due to API failure")
            return self.fallback_llm.generate_response(prompt)


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