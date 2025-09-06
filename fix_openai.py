"""
Emergency fix for OpenAI client
"""

import os
import sys

# Add our app directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'app'))

# Load environment variables using our simple loader
try:
    from app.utils.simple_dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # Fallback: manually load .env if our module isn't available
    env_file = ".env"
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()

# Get the API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("OPENAI_API_KEY not found in environment variables")
    print("Please check your .env file")
    sys.exit(1)

print(f"API Key found: {OPENAI_API_KEY[:10]}..." if len(OPENAI_API_KEY) > 10 else "API Key found")

# Try to use the simple OpenAI client
try:
    from app.utils.simple_openai import SimpleOpenAIClient, SimpleOpenAIResponse
    
    client = SimpleOpenAIClient(OPENAI_API_KEY)
    print("Simple OpenAI client initialized successfully")
    
    # Simple CLI chat loop for testing
    def run_cli():
        print("Starting emergency CLI chat mode...")
        print("Type 'exit' to quit.")
        
        # Simple message history
        messages = [
            {"role": "system", "content": "You are a medical scheduling assistant. Help users schedule appointments."}
        ]
        
        while True:
            # Get user input
            user_input = input("\nYou: ")
            if user_input.lower() == 'exit':
                print("Goodbye!")
                break
            
            # Add to messages
            messages.append({"role": "user", "content": user_input})
            
            try:
                # Get response from OpenAI
                response_data = client.create_completion(
                    model="gpt-3.5-turbo",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=500
                )
                
                response = SimpleOpenAIResponse(response_data)
                assistant_message = response.choices[0].message.content
                print(f"\nAssistant: {assistant_message}")
                
                # Add to messages
                messages.append({"role": "assistant", "content": assistant_message})
                
            except Exception as e:
                print(f"Error: {e}")
                print("Falling back to basic response...")
                print("I'm having trouble connecting to the AI service. Please try again later.")

except ImportError as e:
    print(f"Import error: {e}")
    print("Simple OpenAI client not available")
    
    # Fallback CLI with basic responses
    def run_cli():
        print("Starting basic CLI mode (AI not available)...")
        print("Type 'exit' to quit.")
        
        while True:
            user_input = input("\nYou: ")
            if user_input.lower() == 'exit':
                print("Goodbye!")
                break
            
            # Basic responses
            if "appointment" in user_input.lower():
                print("\nAssistant: I'd be happy to help you schedule an appointment. What type of doctor do you need to see?")
            elif "hello" in user_input.lower() or "hi" in user_input.lower():
                print("\nAssistant: Hello! I'm here to help with medical appointment scheduling. How can I assist you?")
            else:
                print("\nAssistant: I can help you schedule medical appointments. Please let me know what you need.")

if __name__ == "__main__":
    run_cli()