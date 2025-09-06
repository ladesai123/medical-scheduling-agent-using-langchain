"""
Streamlit UI for the Medical Scheduling Agent
"""
import streamlit as st
import sys
import os
import json
from datetime import datetime

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from app.config import get_llm
    from app.agents.scheduler_agent import SchedulerAgent
    from app.utils.data_generator import generate_patient, generate_doctor
except ImportError as e:
    st.error(f"Import error: {e}")
    st.error("Please make sure all required modules are available.")
    st.stop()


def initialize_data():
    """Initialize data files if they don't exist."""
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "app", "data")
    os.makedirs(data_dir, exist_ok=True)
    
    # Generate patients if file doesn't exist
    patients_file = os.path.join(data_dir, "patients.json")
    if not os.path.exists(patients_file):
        patients = []
        for i in range(20):  # Generate 20 patients for demo
            patient = generate_patient(f"P{i+1:04d}")
            patients.append(patient)
        
        with open(patients_file, "w") as f:
            json.dump(patients, f, indent=2)
        st.success(f"Generated {len(patients)} sample patients")
    
    # Generate doctors if file doesn't exist
    doctors_file = os.path.join(data_dir, "doctors.json")
    if not os.path.exists(doctors_file):
        doctors = []
        for i in range(5):  # Generate 5 doctors for demo
            doctor = generate_doctor(f"D{i+1:03d}")
            doctors.append(doctor)
        
        with open(doctors_file, "w") as f:
            json.dump(doctors, f, indent=2)
        st.success(f"Generated {len(doctors)} sample doctors")
    
    # Create empty appointments file if it doesn't exist
    appointments_file = os.path.join(data_dir, "appointments.json")
    if not os.path.exists(appointments_file):
        with open(appointments_file, "w") as f:
            json.dump([], f, indent=2)


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="Medical Scheduling Agent",
        page_icon="🏥",
        layout="wide"
    )
    
    st.title("🏥 Medical Scheduling Agent")
    st.subtitle("AI-Powered Appointment Scheduling System")
    
    # Initialize session state
    if 'agent' not in st.session_state:
        try:
            with st.spinner("Initializing AI agent..."):
                llm = get_llm()
                st.session_state.agent = SchedulerAgent(llm=llm)
                initialize_data()
                st.success("AI agent initialized successfully!")
        except Exception as e:
            st.error(f"Error initializing agent: {e}")
            st.session_state.agent = SchedulerAgent(llm=None)
            st.warning("Using fallback mode (rule-based responses)")
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
        # Add initial greeting
        st.session_state.messages.append({
            "role": "assistant",
            "content": "Hello! Welcome to our medical scheduling system. I'm here to help you schedule an appointment. How can I assist you today?"
        })
    
    # Sidebar with information
    with st.sidebar:
        st.header("📋 System Information")
        
        if st.button("🔄 Reset Conversation"):
            st.session_state.messages = []
            st.session_state.messages.append({
                "role": "assistant", 
                "content": "Hello! Welcome to our medical scheduling system. I'm here to help you schedule an appointment. How can I assist you today?"
            })
            st.rerun()
        
        st.subheader("Features")
        st.write("✅ Schedule new appointments")
        st.write("✅ Patient lookup")
        st.write("✅ Doctor availability")
        st.write("✅ Insurance verification")
        st.write("✅ Appointment confirmation")
        
        st.subheader("Sample Commands")
        st.write("• 'I need to schedule an appointment'")
        st.write("• 'My name is John Smith'")
        st.write("• 'I need to see a cardiologist'")
        st.write("• 'How about tomorrow morning?'")
        
        # Data management
        st.subheader("📊 Data Management")
        if st.button("Generate Sample Data"):
            try:
                initialize_data()
                st.success("Sample data generated!")
            except Exception as e:
                st.error(f"Error generating data: {e}")
        
        # Show current data stats
        try:
            agent = st.session_state.agent
            patients = agent.load_data("patients.json")
            doctors = agent.load_data("doctors.json")
            appointments = agent.load_data("appointments.json")
            
            st.write(f"👥 Patients: {len(patients)}")
            st.write(f"👨‍⚕️ Doctors: {len(doctors)}")
            st.write(f"📅 Appointments: {len(appointments)}")
        except:
            st.write("Data not available")
    
    # Main chat interface
    st.header("💬 Chat with the Scheduling Agent")
    
    # Display conversation history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Add user message to conversation
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.write(prompt)
        
        # Generate and display assistant response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                try:
                    response = st.session_state.agent.generate_response(prompt)
                    st.write(response)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                except Exception as e:
                    error_msg = f"I apologize, but I encountered an error: {str(e)}"
                    st.write(error_msg)
                    st.session_state.messages.append({"role": "assistant", "content": error_msg})
    
    # Quick action buttons
    st.header("🚀 Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("Schedule Appointment"):
            quick_msg = "I would like to schedule an appointment"
            st.session_state.messages.append({"role": "user", "content": quick_msg})
            response = st.session_state.agent.generate_response(quick_msg)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col2:
        if st.button("Check Availability"):
            quick_msg = "What doctors are available?"
            st.session_state.messages.append({"role": "user", "content": quick_msg})
            response = st.session_state.agent.generate_response(quick_msg)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col3:
        if st.button("Emergency Help"):
            quick_msg = "I need urgent medical attention"
            st.session_state.messages.append({"role": "user", "content": quick_msg})
            response = st.session_state.agent.generate_response(quick_msg)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    with col4:
        if st.button("Get Help"):
            quick_msg = "How does this system work?"
            st.session_state.messages.append({"role": "user", "content": quick_msg})
            response = st.session_state.agent.generate_response(quick_msg)
            st.session_state.messages.append({"role": "assistant", "content": response})
            st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("**Medical Scheduling Agent** - Powered by AI | Built with Streamlit")
    st.markdown(f"*Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")


if __name__ == "__main__":
    main()