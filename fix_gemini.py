"""
Emergency fix for Gemini client
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
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("GEMINI_API_KEY not found in environment variables")
    print("Please check your .env file")
    sys.exit(1)

print(f"API Key found: {GEMINI_API_KEY[:10]}...{GEMINI_API_KEY[-4:]}" if len(GEMINI_API_KEY) > 14 else "API Key found")

# Try to use the simple Gemini client
try:
    from app.utils.simple_gemini import SimpleGeminiClient, SimpleGeminiResponse
    
    client = SimpleGeminiClient(GEMINI_API_KEY)
    print("Simple Gemini client initialized successfully")
    
    # Simple CLI chat loop for testing
    def run_cli():
        print("Starting emergency CLI chat mode with Gemini...")
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
                # Get response from Gemini
                response_data = client.create_completion(
                    model="gemini-1.5-flash",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=500
                )
                
                response = SimpleGeminiResponse(response_data)
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
    print("Simple Gemini client not available")
    
    # Fallback CLI with basic responses
    def run_cli():
        print("Starting basic CLI mode (no AI)...")
        print("Type 'exit' to quit.")
        
        while True:
            user_input = input("\nYou: ")
            if user_input.lower() == 'exit':
                print("Goodbye!")
                break
            
            # Basic responses
            if "appointment" in user_input.lower():
                print("\nAssistant: I'd be happy to help you schedule an appointment. However, I'm running in basic mode without AI capabilities. Please use the main application for full functionality.")
            elif "hello" in user_input.lower() or "hi" in user_input.lower():
                print("\nAssistant: Hello! I'm running in basic mode. Please use the main application for full medical scheduling capabilities.")
            else:
                print("\nAssistant: I'm running in basic mode without AI. Please use the main application for medical scheduling assistance.")

if __name__ == "__main__":
    run_cli()