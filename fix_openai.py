"""
Emergency fix for OpenAI client
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY not found in environment variables")

# Initialize a minimal OpenAI client
from openai import OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

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
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",  # Using a simpler model for testing
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            # Extract and print response
            assistant_message = response.choices[0].message.content
            print(f"\nAssistant: {assistant_message}")
            
            # Add to messages
            messages.append({"role": "assistant", "content": assistant_message})
            
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    run_cli()