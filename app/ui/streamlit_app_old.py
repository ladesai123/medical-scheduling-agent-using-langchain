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


def apply_custom_css():
    """Apply custom CSS for health-themed UI."""
    st.markdown("""
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    /* Main app styling */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1200px;
    }
    
    /* Custom header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        color: white;
        text-align: center;
        box-shadow: 0 10px 30px rgba(102, 126, 234, 0.3);
    }
    
    .main-header h1 {
        font-family: 'Inter', sans-serif;
        font-weight: 700;
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header p {
        font-family: 'Inter', sans-serif;
        font-size: 1.2rem;
        opacity: 0.9;
        margin-bottom: 0;
    }
    
    /* Chat container styling */
    .chat-container {
        background: white;
        border-radius: 15px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
        border: 1px solid #e8ecef;
    }
    
    /* Message styling */
    .user-message {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 5px 20px;
        margin: 0.5rem 0;
        margin-left: 2rem;
        font-family: 'Inter', sans-serif;
        box-shadow: 0 3px 10px rgba(102, 126, 234, 0.3);
    }
    
    .assistant-message {
        background: #f8f9fa;
        color: #2c3e50;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 20px 5px;
        margin: 0.5rem 0;
        margin-right: 2rem;
        border-left: 4px solid #2ecc71;
        font-family: 'Inter', sans-serif;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    
    /* Quick action buttons */
    .quick-action-btn {
        background: linear-gradient(135deg, #2ecc71, #27ae60);
        color: white;
        border: none;
        padding: 0.75rem 1.5rem;
        border-radius: 25px;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        cursor: pointer;
        transition: all 0.3s ease;
        margin: 0.25rem;
        box-shadow: 0 3px 10px rgba(46, 204, 113, 0.3);
    }
    
    .quick-action-btn:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(46, 204, 113, 0.4);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* Feature list styling */
    .feature-list {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #2ecc71;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }
    
    /* Stats cards */
    .stat-card {
        background: linear-gradient(135deg, #74b9ff, #0984e3);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        text-align: center;
        box-shadow: 0 3px 10px rgba(116, 185, 255, 0.3);
    }
    
    /* Input styling */
    .stTextInput > div > div > input {
        border-radius: 25px;
        border: 2px solid #e8ecef;
        padding: 0.75rem 1rem;
        font-family: 'Inter', sans-serif;
        transition: all 0.3s ease;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* Success/error messages */
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #c3e6cb;
        margin: 1rem 0;
    }
    
    .error-message {
        background: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #f5c6cb;
        margin: 1rem 0;
    }
    
    /* Hide Streamlit elements */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom button styling */
    .stButton > button {
        border-radius: 25px;
        border: none;
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        font-family: 'Inter', sans-serif;
        font-weight: 500;
        padding: 0.5rem 1.5rem;
        transition: all 0.3s ease;
        box-shadow: 0 3px 10px rgba(102, 126, 234, 0.3);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    </style>
    """, unsafe_allow_html=True)


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
    st.markdown("### AI-Powered Appointment Scheduling System")
    
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