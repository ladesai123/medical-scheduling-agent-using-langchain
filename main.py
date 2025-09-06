"""
Medical Scheduling Agent

This is the main entry point for the application.
"""

import os
import json
import sys
from typing import List, Dict, Any
import logging

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s,%(msecs)d [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger(__name__)

# Import utility functions
def setup_data():
    """Set up initial data for the application."""
    try:
        # Import here to avoid circular imports
        from app.utils.data_generator import generate_patient, generate_doctor
        
        # Create data directory if it doesn't exist
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app", "data")
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
        
        # Generate patients
        patients_file = os.path.join(data_dir, "patients.json")
        if not os.path.exists(patients_file):
            patients = []
            for i in range(50):  # Generate 50 patients
                patient = generate_patient(f"P{i+1:04d}")
                patients.append(patient)
            
            with open(patients_file, "w") as f:
                json.dump(patients, f, indent=2)
            print(f"Generated 50 synthetic patients and saved to {patients_file}")
        else:
            print(f"Patients file {patients_file} already exists, skipping generation")
        
        # Generate doctors and their schedules
        doctors_file = os.path.join(data_dir, "doctors.json")
        if not os.path.exists(doctors_file):
            doctors = []
            for i in range(10):  # Generate 10 doctors
                doctor = generate_doctor(f"D{i+1:03d}")
                doctors.append(doctor)
            
            with open(doctors_file, "w") as f:
                json.dump(doctors, f, indent=2)
            print(f"Generated 10 synthetic doctors and saved to {doctors_file}")
        else:
            print(f"Doctors file {doctors_file} already exists, skipping generation")
        
        # Create empty appointments file if it doesn't exist
        appointments_file = os.path.join(data_dir, "appointments.json")
        if not os.path.exists(appointments_file):
            with open(appointments_file, "w") as f:
                json.dump([], f, indent=2)
            print(f"Created empty appointments file at {appointments_file}")
        else:
            print(f"Appointments file {appointments_file} already exists, skipping creation")

    except Exception as e:
        logger.error(f"Error setting up data: {e}")
        raise


def run_cli():
    """Run the application in CLI mode."""
    try:
        print("Starting Medical Scheduling Agent in CLI mode...")
        print("Type 'exit', 'quit', 'q', or 'bye' to quit.")
        print("=" * 50)
        
        # Import here to avoid circular imports
        from app.config import get_llm
        from app.agents.scheduler_agent import SchedulerAgent
        
        # Initialize agent
        llm = get_llm()
        agent = SchedulerAgent(llm=llm)
        
        # Display initial greeting
        print("\nAgent: Hello! Welcome to our medical scheduling system. I'm here to help you schedule an appointment. How can I assist you today?")
        
        conversation_count = 0
        max_conversations = 50  # Prevent infinite loops
        
        # Simple CLI interaction loop
        while conversation_count < max_conversations:
            try:
                user_input = input("\nYou: ").strip()
                
                # Handle empty input
                if not user_input:
                    print("Please enter a message or type 'exit' to quit.")
                    continue
                
                # Check for exit commands
                if user_input.lower() in ["exit", "quit", "q", "bye", "goodbye"]:
                    print("\nAgent: Thank you for using our medical scheduling system. Goodbye!")
                    break
                
                # Generate response
                response = agent.generate_response(user_input)
                print(f"\nAgent: {response}")
                
                conversation_count += 1
                
            except (EOFError, KeyboardInterrupt):
                print("\n\nAgent: Thank you for using our medical scheduling system. Goodbye!")
                break
            except Exception as e:
                logger.error(f"Error processing input: {e}")
                print(f"\nAgent: I apologize, but I encountered an error. Please try again or type 'exit' to quit.")
                
        if conversation_count >= max_conversations:
            print(f"\nAgent: We've reached the maximum number of exchanges ({max_conversations}). Thank you for using our service!")
            
    except Exception as e:
        logger.error(f"Error in CLI mode: {e}")
        print(f"Error starting CLI mode: {e}")
        print("Please check your configuration and try again.")
        raise


def run_streamlit():
    """Run the Streamlit UI."""
    try:
        import subprocess
        import sys
        
        # Get the directory where main.py is located
        base_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Build the path to the streamlit app
        streamlit_app_path = os.path.join(base_dir, "app", "ui", "streamlit_app.py")
        
        if not os.path.exists(streamlit_app_path):
            print(f"Error: Streamlit app not found at {streamlit_app_path}")
            sys.exit(1)
        
        # Run the Streamlit app as a subprocess
        subprocess.run([sys.executable, "-m", "streamlit", "run", streamlit_app_path])
        
    except Exception as e:
        logger.error(f"Error running Streamlit: {e}")
        raise


def main():
    """Main entry point for the application."""
    if len(sys.argv) < 2:
        print("Usage: python main.py [cli|streamlit|setup]")
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command == "setup":
        setup_data()
    elif command == "cli":
        run_cli()
    elif command == "streamlit":
        run_streamlit()
    else:
        print(f"Unknown command: {command}")
        print("Usage: python main.py [cli|streamlit|setup]")
        sys.exit(1)


if __name__ == "__main__":
    main()