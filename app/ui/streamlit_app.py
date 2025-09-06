"""
Improved Streamlit UI for the Medical Scheduling Agent
Health-themed, user-friendly interface
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
    from app.agents.langchain_agent import LangChainMedicalAgent
    from app.agents.mock_langchain_agent import MockLangChainAgent
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
        max-height: 500px;
        overflow-y: auto;
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
        page_title="HealthCare+ Medical Scheduling",
        page_icon="🏥",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Apply custom CSS
    apply_custom_css()
    
    # Custom header
    st.markdown("""
    <div class="main-header">
        <h1>🏥 HealthCare+ Medical Scheduling</h1>
        <p>Your AI-Powered Healthcare Appointment Assistant</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'agent' not in st.session_state:
        try:
            llm = get_llm()
            
            # Check if we got a LangChain agent directly
            if isinstance(llm, (LangChainMedicalAgent, MockLangChainAgent)):
                st.session_state.agent = llm
                agent_type = "Enhanced LangChain" if isinstance(llm, LangChainMedicalAgent) else "Enhanced Mock LangChain"
                st.success(f"✅ {agent_type} AI Medical Assistant initialized successfully!", icon="🤖")
            else:
                st.session_state.agent = SchedulerAgent(llm=llm)
                st.success("✅ AI Medical Assistant initialized successfully!", icon="🤖")
        except Exception as e:
            st.error(f"❌ Error initializing agent: {e}")
            st.error("Falling back to rule-based agent...")
            try:
                from app.agents.scheduler_agent import SchedulerAgent
                st.session_state.agent = SchedulerAgent(llm=None)
                st.warning("⚠️ Using fallback rule-based assistant", icon="⚠️")
            except Exception as e2:
                st.error(f"❌ Critical error: {e2}")
                st.stop()
    
    if 'messages' not in st.session_state:
        st.session_state.messages = []
        st.session_state.messages.append({
            "role": "assistant", 
            "content": "👋 Hello! I'm your AI Medical Scheduling Assistant. I'm here to help you:\n\n• **Schedule new appointments** with our specialists\n• **Cancel or reschedule** existing appointments\n• **Check appointment availability** and doctor schedules\n• **Verify insurance** and update patient information\n\nHow can I assist you today? You can start by telling me what you need help with! 😊"
        })
    
    # Create two columns for main layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Chat interface
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)
        st.markdown("### 💬 Chat with Your Medical Assistant")
        
        # Display chat messages
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f'<div class="user-message">👤 You: {message["content"]}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="assistant-message">🤖 Assistant: {message["content"]}</div>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Quick action buttons
        st.markdown("### 🚀 Quick Actions")
        col1_1, col1_2, col1_3, col1_4 = st.columns(4)
        
        with col1_1:
            if st.button("📅 Schedule Appointment", key="schedule_btn", help="Start scheduling a new appointment"):
                quick_msg = "I would like to schedule a new appointment"
                st.session_state.messages.append({"role": "user", "content": quick_msg})
                with st.spinner("Processing your request..."):
                    response = st.session_state.agent.generate_response(quick_msg)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
        
        with col1_2:
            if st.button("🔄 Reschedule", key="reschedule_btn", help="Reschedule an existing appointment"):
                quick_msg = "I want to reschedule my appointment"
                st.session_state.messages.append({"role": "user", "content": quick_msg})
                with st.spinner("Looking up your appointments..."):
                    response = st.session_state.agent.generate_response(quick_msg)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
        
        with col1_3:
            if st.button("❌ Cancel Appointment", key="cancel_btn", help="Cancel an existing appointment"):
                quick_msg = "I want to cancel my appointment"
                st.session_state.messages.append({"role": "user", "content": quick_msg})
                with st.spinner("Looking up your appointments..."):
                    response = st.session_state.agent.generate_response(quick_msg)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
        
        with col1_4:
            if st.button("📋 Check Appointments", key="check_btn", help="View your existing appointments"):
                quick_msg = "I want to check my existing appointments"
                st.session_state.messages.append({"role": "user", "content": quick_msg})
                with st.spinner("Retrieving your appointments..."):
                    response = st.session_state.agent.generate_response(quick_msg)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
        
        # Chat input
        st.markdown("### ✏️ Type Your Message")
        user_input = st.text_input(
            "Type your message here...", 
            key="user_input",
            placeholder="e.g., 'I need to see a cardiologist tomorrow morning' or 'My name is John Smith'",
            help="Ask me anything about scheduling, canceling, or rescheduling appointments!"
        )
        
        col_send, col_clear = st.columns([1, 1])
        with col_send:
            if st.button("📤 Send Message", key="send_btn", type="primary") or user_input:
                if user_input:
                    st.session_state.messages.append({"role": "user", "content": user_input})
                    with st.spinner("🤖 AI Assistant is thinking..."):
                        response = st.session_state.agent.generate_response(user_input)
                        st.session_state.messages.append({"role": "assistant", "content": response})
                    st.rerun()
        
        with col_clear:
            if st.button("🗑️ Clear Chat", key="clear_btn", help="Start a new conversation"):
                st.session_state.messages = []
                st.session_state.agent.conversation_state = {}  # Reset agent state
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": "👋 Hello! I'm your AI Medical Scheduling Assistant. How can I help you today?"
                })
                st.rerun()
    
    with col2:
        # Sidebar content
        st.markdown("### 📊 System Status")
        
        # Show current data stats
        try:
            agent = st.session_state.agent
            patients = agent.load_data("patients.json")
            doctors = agent.load_data("doctors.json")
            appointments = agent.load_data("appointments.json")
            
            # Active appointments
            active_appointments = [apt for apt in appointments if apt.get("status") == "scheduled"]
            cancelled_appointments = [apt for apt in appointments if apt.get("status") == "cancelled"]
            
            st.markdown(f"""
            <div class="stat-card">
                <h4>👥 Patients</h4>
                <h2>{len(patients)}</h2>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="stat-card">
                <h4>👨‍⚕️ Doctors</h4>
                <h2>{len(doctors)}</h2>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="stat-card">
                <h4>📅 Active Appointments</h4>
                <h2>{len(active_appointments)}</h2>
            </div>
            """, unsafe_allow_html=True)
            
            if cancelled_appointments:
                st.markdown(f"""
                <div class="stat-card" style="background: linear-gradient(135deg, #e17055, #d63031);">
                    <h4>❌ Cancelled</h4>
                    <h2>{len(cancelled_appointments)}</h2>
                </div>
                """, unsafe_allow_html=True)
        except:
            st.error("Data not available")
        
        st.markdown("### 🏥 Available Specialties")
        try:
            doctors = st.session_state.agent.load_data("doctors.json")
            specialties = set([doc.get("specialty", "General") for doc in doctors])
            for specialty in sorted(specialties):
                st.markdown(f"""
                <div class="feature-list">
                    <strong>• {specialty}</strong>
                </div>
                """, unsafe_allow_html=True)
        except:
            st.write("Loading specialties...")
        
        st.markdown("### 💡 Sample Commands")
        sample_commands = [
            "I need to schedule an appointment",
            "My name is Sarah Johnson", 
            "I need to see a dermatologist",
            "How about tomorrow afternoon?",
            "Cancel my appointment",
            "Reschedule my appointment to Friday"
        ]
        
        for i, cmd in enumerate(sample_commands):
            if st.button(f"💭 \"{cmd}\"", key=f"sample_{i}", help="Click to use this sample command"):
                st.session_state.messages.append({"role": "user", "content": cmd})
                with st.spinner("Processing..."):
                    response = st.session_state.agent.generate_response(cmd)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                st.rerun()
        
        # Emergency contact info
        st.markdown("### 🚨 Emergency Contact")
        st.markdown("""
        <div style="background: #ffe6e6; padding: 1rem; border-radius: 10px; border-left: 4px solid #e74c3c;">
            <strong>For medical emergencies:</strong><br>
            📞 Call 911<br><br>
            <strong>Clinic Hours:</strong><br>
            🕐 Mon-Fri: 8:00 AM - 6:00 PM<br>
            🕐 Sat: 9:00 AM - 2:00 PM<br>
            🕐 Sun: Closed<br><br>
            <strong>Non-emergency:</strong><br>
            📞 (555) 123-4567
        </div>
        """, unsafe_allow_html=True)
        
        # Data management
        st.markdown("### ⚙️ Admin")
        if st.button("🔄 Generate Sample Data", help="Generate additional sample patients and doctors"):
            try:
                initialize_data()
                st.success("Sample data generated!")
                st.rerun()
            except Exception as e:
                st.error(f"Error generating data: {e}")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; font-size: 0.9rem; padding: 1rem;">
        <strong>HealthCare+ Medical Scheduling</strong> - Powered by AI | Built with ❤️ and Streamlit<br>
        <em>Your health, our priority. Scheduling made simple.</em><br>
        Last updated: {date}
    </div>
    """.format(date=datetime.now().strftime("%Y-%m-%d %H:%M")), unsafe_allow_html=True)


if __name__ == "__main__":
    main()