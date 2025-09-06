"""
LangChain-powered Medical Scheduling Agent
Uses LangChain tools and agents for enhanced conversation and functionality.
"""

import json
import os
import logging
from datetime import datetime, timedelta, date
from typing import Dict, List, Any, Optional

# Try to import email_validator, but make it optional
try:
    from email_validator import validate_email, EmailNotValidError
    EMAIL_VALIDATOR_AVAILABLE = True
except ImportError:
    EMAIL_VALIDATOR_AVAILABLE = False
    # Create dummy functions as fallbacks
    def validate_email(email):
        # Basic validation - just check for @ symbol
        if '@' in email and '.' in email:
            class MockValid:
                def __init__(self, email):
                    self.email = email
            return MockValid(email)
        else:
            raise Exception("Invalid email format")
    
    class EmailNotValidError(Exception):
        pass

# Try to import LangChain components, but make them optional
try:
    from langchain.agents import AgentExecutor, create_openai_tools_agent
    from langchain.tools import tool
    from langchain_openai import ChatOpenAI
    from langchain.prompts import ChatPromptTemplate
    from langchain_core.messages import HumanMessage, SystemMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    # Create dummy functions/classes as fallbacks
    def tool(func):
        return func
    
    class ChatPromptTemplate:
        @staticmethod
        def from_messages(messages):
            return None
    
    class AgentExecutor:
        def __init__(self, *args, **kwargs):
            pass
        
        def invoke(self, inputs):
            return {"output": "LangChain not available - using fallback mode"}
    
    def create_openai_tools_agent(*args, **kwargs):
        return None

# Try to import utility managers, but make them optional
try:
    from app.utils.calendar_manager import CalendarManager
    from app.utils.notification_manager import NotificationManager
    UTILS_AVAILABLE = True
except ImportError:
    UTILS_AVAILABLE = False
    # Create dummy managers as fallbacks
    class CalendarManager:
        def __init__(self, data_dir):
            self.data_dir = data_dir
    
    class NotificationManager:
        def __init__(self, data_dir):
            self.data_dir = data_dir

logger = logging.getLogger(__name__)


class LangChainMedicalAgent:
    """LangChain-powered Medical Scheduling Agent with advanced tools."""
    
    def __init__(self, llm=None, api_key=None, provider="gemini"):
        """Initialize the LangChain agent with tools."""
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
        self.conversation_state = {}
        self.provider = provider
        
        # Check if LangChain is available
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("LangChain is not available. Please install langchain packages or use the mock agent.")
        
        # Initialize managers
        self.calendar_manager = CalendarManager(self.data_dir)
        self.notification_manager = NotificationManager(self.data_dir)
        
        # Initialize LLM
        if llm is None and api_key:
            try:
                if provider == "gemini":
                    # Try LangChain Google GenAI first
                    try:
                        from langchain_google_genai import ChatGoogleGenerativeAI
                        self.llm = ChatGoogleGenerativeAI(
                            model="gemini-1.5-flash",
                            temperature=0.3,
                            google_api_key=api_key
                        )
                        logger.info("ChatGoogleGenerativeAI initialized successfully")
                    except ImportError:
                        # Fallback to custom Gemini wrapper
                        from app.utils.simple_gemini import SimpleGeminiClient
                        gemini_client = SimpleGeminiClient(api_key)
                        self.llm = GeminiLangChainWrapper(gemini_client)
                        logger.info("Custom Gemini LangChain wrapper initialized")
                else:  # provider == "openai"
                    self.llm = ChatOpenAI(
                        model="gpt-3.5-turbo",
                        temperature=0.3,
                        api_key=api_key
                    )
                    logger.info("ChatOpenAI initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize {provider} LLM: {e}")
                # Initialize fallback when API key is invalid or API fails
                logger.info("Initializing with fallback LLM wrapper")
                self.llm = FallbackLLMWrapper()
        elif llm is None:
            # No API key provided, use fallback
            logger.warning("No API key provided, using fallback LLM")
            self.llm = FallbackLLMWrapper()
        else:
            self.llm = llm
        
        # Initialize tools and agent
        self.tools = self._create_tools()
        self.agent_executor = self._create_agent()
        
        logger.info(f"LangChainMedicalAgent initialized with {provider}")
    
    def _create_tools(self):
        """Create LangChain tools for medical scheduling."""
        
        @tool
        def search_patient(name: str) -> str:
            """Search for a patient by name in the database."""
            try:
                patients = self._load_data("patients.json")
                name_parts = name.lower().split()
                
                matching_patients = []
                for patient in patients:
                    patient_name = f"{patient['first_name']} {patient['last_name']}".lower()
                    if all(part in patient_name for part in name_parts):
                        matching_patients.append(patient)
                
                if matching_patients:
                    if len(matching_patients) == 1:
                        patient = matching_patients[0]
                        return f"Found patient: {patient['first_name']} {patient['last_name']}, DOB: {patient['date_of_birth']}, Patient ID: {patient['patient_id']}"
                    else:
                        result = f"Found {len(matching_patients)} patients with similar names:\n"
                        for i, patient in enumerate(matching_patients[:3]):  # Show max 3
                            result += f"{i+1}. {patient['first_name']} {patient['last_name']}, DOB: {patient['date_of_birth']}\n"
                        return result
                else:
                    return f"No patient found with name '{name}'. This appears to be a new patient."
            except Exception as e:
                logger.error(f"Error searching patient: {e}")
                return f"Error searching for patient: {e}"
        
        @tool
        def get_available_doctors(specialty: str = "") -> str:
            """Get list of available doctors, optionally filtered by specialty."""
            try:
                doctors = self._load_data("doctors.json")
                
                if specialty:
                    filtered_doctors = [d for d in doctors if specialty.lower() in d['specialty'].lower()]
                else:
                    filtered_doctors = doctors
                
                if not filtered_doctors:
                    return f"No doctors found for specialty: {specialty}"
                
                result = f"Available doctors" + (f" for {specialty}" if specialty else "") + ":\n"
                for doctor in filtered_doctors[:5]:  # Show max 5
                    result += f"- Dr. {doctor['first_name']} {doctor['last_name']} ({doctor['specialty']})\n"
                
                return result
            except Exception as e:
                logger.error(f"Error getting doctors: {e}")
                return f"Error retrieving doctors: {e}"
        
        @tool
        def check_doctor_availability(doctor_name: str, date: str) -> str:
            """Check if a doctor is available on a specific date."""
            try:
                doctors = self._load_data("doctors.json")
                appointments = self._load_data("appointments.json")
                
                # Find doctor
                doctor = None
                for d in doctors:
                    if doctor_name.lower() in f"{d['first_name']} {d['last_name']}".lower():
                        doctor = d
                        break
                
                if not doctor:
                    return f"Doctor '{doctor_name}' not found."
                
                # Check existing appointments for that date
                existing_appointments = [
                    a for a in appointments 
                    if a['doctor_id'] == doctor['doctor_id'] and a['date'] == date
                ]
                
                # Simulate available time slots (9 AM - 5 PM, 1-hour slots)
                available_slots = []
                for hour in range(9, 17):
                    time_slot = f"{hour:02d}:00"
                    if not any(a['time'] == time_slot for a in existing_appointments):
                        available_slots.append(time_slot)
                
                if available_slots:
                    return f"Dr. {doctor['first_name']} {doctor['last_name']} is available on {date} at: {', '.join(available_slots[:5])}"
                else:
                    return f"Dr. {doctor['first_name']} {doctor['last_name']} has no available slots on {date}."
                    
            except Exception as e:
                logger.error(f"Error checking availability: {e}")
                return f"Error checking doctor availability: {e}"
        
        @tool
        def book_appointment_enhanced(patient_name: str, doctor_name: str, date: str, time: str, patient_type: str = "returning", patient_email: str = "", patient_phone: str = "") -> str:
            """Book an appointment with enhanced calendar integration and notifications."""
            try:
                # Load data
                patients = self._load_data("patients.json")
                doctors = self._load_data("doctors.json")
                
                # Find patient
                patient = None
                for p in patients:
                    if patient_name.lower() in f"{p['first_name']} {p['last_name']}".lower():
                        patient = p
                        break
                
                if not patient:
                    return f"Patient '{patient_name}' not found. Please register first."
                
                # Find doctor
                doctor = None
                for d in doctors:
                    if doctor_name.lower() in f"{d['first_name']} {d['last_name']}".lower():
                        doctor = d
                        break
                
                if not doctor:
                    return f"Doctor '{doctor_name}' not found."
                
                # Update patient contact info if provided
                if patient_email:
                    patient['email'] = patient_email
                if patient_phone:
                    patient['phone'] = patient_phone
                
                # Determine duration
                duration = 60 if patient_type == "new" else 30
                
                # Use calendar manager to book
                patient_data = {
                    'patient_id': patient['patient_id'],
                    'name': f"{patient['first_name']} {patient['last_name']}",
                    'type': patient_type,
                    'notes': f"Patient type: {patient_type}"
                }
                
                booking_result = self.calendar_manager.book_slot(
                    doctor['doctor_id'], date, time, patient_data, duration
                )
                
                if not booking_result.get('success'):
                    return f"❌ {booking_result.get('message', 'Booking failed')}"
                
                appointment = booking_result['appointment']
                
                # Send confirmation email
                confirmation_result = self.notification_manager.send_confirmation_email(appointment, patient)
                
                # Send intake forms
                forms_result = self.notification_manager.send_intake_forms(appointment, patient)
                
                # Schedule reminders
                self.notification_manager.schedule_reminders(appointment, patient)
                
                result_message = f"✅ Appointment booked successfully!\n\n"
                result_message += f"**Appointment Details:**\n"
                result_message += f"• ID: {appointment['appointment_id']}\n"
                result_message += f"• Patient: {patient['first_name']} {patient['last_name']}\n"
                result_message += f"• Doctor: {appointment['doctor_name']} ({appointment['specialty']})\n"
                result_message += f"• Date: {date}\n"
                result_message += f"• Time: {time}\n"
                result_message += f"• Duration: {duration} minutes\n"
                result_message += f"• Location: {appointment.get('location', 'Main Office')}\n\n"
                
                if confirmation_result.get('success'):
                    result_message += f"📧 Confirmation email sent to: {patient.get('email', 'N/A')}\n"
                
                if forms_result.get('success'):
                    result_message += f"📋 Intake forms sent to patient\n"
                
                result_message += f"🕐 Automatic reminders scheduled (7, 3, and 1 days before)\n"
                
                return result_message
                
            except Exception as e:
                logger.error(f"Error booking appointment: {e}")
                return f"Error booking appointment: {e}"
        
        @tool 
        def get_calendar_availability(doctor_name: str, date: str, duration_minutes: int = 30) -> str:
            """Get available time slots for a doctor on a specific date."""
            try:
                doctors = self._load_data("doctors.json")
                
                # Find doctor
                doctor = None
                for d in doctors:
                    if doctor_name.lower() in f"{d['first_name']} {d['last_name']}".lower():
                        doctor = d
                        break
                
                if not doctor:
                    return f"Doctor '{doctor_name}' not found."
                
                # Get available slots
                available_slots = self.calendar_manager.get_available_slots(
                    doctor['doctor_id'], date, duration_minutes
                )
                
                if not available_slots:
                    return f"No available slots for {doctor['first_name']} {doctor['last_name']} on {date}"
                
                result = f"Available slots for Dr. {doctor['first_name']} {doctor['last_name']} on {date}:\n"
                for slot in available_slots[:8]:  # Show max 8 slots
                    result += f"• {slot}\n"
                
                if len(available_slots) > 8:
                    result += f"... and {len(available_slots) - 8} more slots available"
                
                return result
                
            except Exception as e:
                logger.error(f"Error getting availability: {e}")
                return f"Error checking availability: {e}"
        
        @tool
        def reschedule_appointment(appointment_id: str, new_date: str, new_time: str) -> str:
            """Reschedule an existing appointment to a new date and time."""
            try:
                result = self.calendar_manager.reschedule_appointment(appointment_id, new_date, new_time)
                
                if not result.get('success'):
                    return f"❌ {result.get('message', 'Rescheduling failed')}"
                
                appointment = result['appointment']
                
                # Load patient data for notifications
                patients = self._load_data("patients.json")
                patient = next((p for p in patients if p['patient_id'] == appointment['patient_id']), None)
                
                if patient:
                    # Send rescheduling confirmation
                    confirmation_result = self.notification_manager.send_confirmation_email(appointment, patient)
                    
                    # Reschedule reminders
                    self.notification_manager.schedule_reminders(appointment, patient)
                
                return f"✅ {result.get('message', 'Appointment rescheduled successfully')}\n\n" \
                       f"📧 New confirmation sent to patient\n" \
                       f"🕐 Reminders updated for new date"
                
            except Exception as e:
                logger.error(f"Error rescheduling appointment: {e}")
                return f"Error rescheduling appointment: {e}"
        
        @tool
        def cancel_appointment(appointment_id: str, reason: str = "") -> str:
            """Cancel an existing appointment."""
            try:
                result = self.calendar_manager.cancel_appointment(appointment_id, reason)
                
                if not result.get('success'):
                    return f"❌ {result.get('message', 'Cancellation failed')}"
                
                appointment = result['appointment']
                
                # Load patient data
                patients = self._load_data("patients.json")
                patient = next((p for p in patients if p['patient_id'] == appointment['patient_id']), None)
                
                if patient:
                    # Send cancellation confirmation (simulated)
                    logger.info(f"📧 Cancellation confirmation sent to {patient.get('email', 'N/A')}")
                    print(f"\n📧 Cancellation confirmation sent to: {patient.get('first_name', '')} {patient.get('last_name', '')}")
                
                return f"✅ {result.get('message', 'Appointment cancelled successfully')}\n\n" \
                       f"📧 Cancellation confirmation sent to patient\n" \
                       f"Reason: {reason or 'No reason provided'}"
                
            except Exception as e:
                logger.error(f"Error cancelling appointment: {e}")
                return f"Error cancelling appointment: {e}"
        
        @tool
        def export_appointments_to_excel(start_date: str = "", end_date: str = "") -> str:
            """Export appointments to Excel file for admin review."""
            try:
                filepath = self.calendar_manager.export_to_excel(start_date, end_date)
                
                if filepath:
                    return f"✅ Appointments exported successfully to: {filepath}\n\n" \
                           f"The Excel file contains all appointment data " \
                           f"{'for the specified date range' if start_date and end_date else 'for all dates'}."
                else:
                    return "❌ Failed to export appointments to Excel."
                
            except Exception as e:
                logger.error(f"Error exporting to Excel: {e}")
                return f"Error exporting appointments: {e}"
        
        @tool
        def send_reminder_now(appointment_id: str, reminder_type: str = "first") -> str:
            """Send a reminder for a specific appointment immediately."""
            try:
                # Load data
                appointments = self._load_data("appointments.json")
                patients = self._load_data("patients.json")
                
                # Find appointment
                appointment = next((a for a in appointments if a['appointment_id'] == appointment_id), None)
                if not appointment:
                    return f"Appointment {appointment_id} not found."
                
                # Find patient
                patient = next((p for p in patients if p['patient_id'] == appointment['patient_id']), None)
                if not patient:
                    return f"Patient not found for appointment {appointment_id}."
                
                # Send reminder
                if reminder_type in ["second", "third"]:
                    # Interactive reminder
                    result = self.notification_manager.send_interactive_reminder(appointment, patient, reminder_type)
                else:
                    # Regular reminder
                    email_result = self.notification_manager.send_reminder_email(appointment, patient, reminder_type)
                    sms_result = self.notification_manager.send_sms_reminder(appointment, patient, reminder_type)
                    
                    result = {
                        "success": email_result.get('success') or sms_result.get('success'),
                        "message": f"Email: {email_result.get('message', 'Failed')}, SMS: {sms_result.get('message', 'Failed')}"
                    }
                
                if result.get('success'):
                    return f"✅ {reminder_type.title()} reminder sent successfully for appointment {appointment_id}"
                else:
                    return f"❌ Failed to send reminder: {result.get('message', 'Unknown error')}"
                
            except Exception as e:
                logger.error(f"Error sending reminder: {e}")
                return f"Error sending reminder: {e}"
        
        @tool
        def validate_insurance(carrier: str, member_id: str, group_number: str = "") -> str:
            """Validate insurance information."""
            try:
                # Simple validation logic
                if not carrier or len(carrier) < 3:
                    return "❌ Invalid insurance carrier name."
                
                if not member_id or len(member_id) < 5:
                    return "❌ Invalid member ID. Must be at least 5 characters."
                
                # Simulate insurance validation
                valid_carriers = [
                    "blue cross", "aetna", "cigna", "united healthcare", "humana",
                    "kaiser", "anthem", "bcbs", "medicare", "medicaid"
                ]
                
                if any(vc in carrier.lower() for vc in valid_carriers):
                    return f"✅ Insurance validated: {carrier}, Member ID: {member_id}" + (f", Group: {group_number}" if group_number else "")
                else:
                    return f"⚠️ Insurance carrier '{carrier}' not recognized. Please verify spelling."
                    
            except Exception as e:
                logger.error(f"Error validating insurance: {e}")
                return f"Error validating insurance: {e}"
        
        @tool
        def get_patient_appointments(patient_name: str) -> str:
            """Get all appointments for a specific patient."""
            try:
                appointments = self._load_data("appointments.json")
                
                patient_appointments = [
                    a for a in appointments 
                    if patient_name.lower() in a['patient_name'].lower()
                ]
                
                if not patient_appointments:
                    return f"No appointments found for {patient_name}."
                
                result = f"Appointments for {patient_name}:\n"
                for apt in patient_appointments:
                    result += f"- {apt['appointment_id']}: {apt['date']} at {apt['time']} with {apt.get('doctor_name', 'Unknown Doctor')} ({apt['status']})\n"
                
                return result
                
            except Exception as e:
                logger.error(f"Error getting patient appointments: {e}")
                return f"Error retrieving appointments: {e}"
        
        return [
            search_patient,
            get_available_doctors,
            check_doctor_availability,
            book_appointment_enhanced,
            get_calendar_availability,
            reschedule_appointment,
            cancel_appointment,
            validate_insurance,
            get_patient_appointments,
            export_appointments_to_excel,
            send_reminder_now
        ]
    
    def _create_agent(self):
        """Create the LangChain agent with tools."""
        try:
            # Define the prompt template for OpenAI tools agent
            openai_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a professional medical scheduling assistant for HealthCare+ Medical Center.

Your responsibilities:
1. Help patients schedule, reschedule, or cancel appointments
2. Look up patient information and appointment history
3. Collect and validate insurance information
4. Provide doctor availability and schedule information
5. Ensure accurate patient data collection (name, DOB, contact info)

Key guidelines:
- Always be professional, empathetic, and helpful
- For new patients: collect full information (name, DOB, contact, insurance)
- For returning patients: verify identity with name and DOB
- New patient appointments are 60 minutes, returning patients are 30 minutes
- Always confirm appointment details before booking
- Ask for insurance information for all appointments
- Be clear about next steps and what patients should expect

Use the available tools to search for patients, check doctor availability, book appointments, and validate insurance information.
"""),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}")
            ])
            
            # Define the prompt template for React agent (with tools and tool_names)
            react_prompt = ChatPromptTemplate.from_messages([
                ("system", """You are a professional medical scheduling assistant for HealthCare+ Medical Center.

Your responsibilities:
1. Help patients schedule, reschedule, or cancel appointments
2. Look up patient information and appointment history
3. Collect and validate insurance information
4. Provide doctor availability and schedule information
5. Ensure accurate patient data collection (name, DOB, contact info)

Key guidelines:
- Always be professional, empathetic, and helpful
- For new patients: collect full information (name, DOB, contact, insurance)
- For returning patients: verify identity with name and DOB
- New patient appointments are 60 minutes, returning patients are 30 minutes
- Always confirm appointment details before booking
- Ask for insurance information for all appointments
- Be clear about next steps and what patients should expect

You have access to the following tools:
{tools}

Tool names: {tool_names}

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question
"""),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}")
            ])
            
            # Create the agent - use different agent types based on provider
            if isinstance(self.llm, FallbackLLMWrapper):
                # For fallback LLM, create a simple fallback executor
                logger.warning("Using fallback LLM, creating fallback agent executor")
                agent_executor = FallbackAgentExecutor(self.tools)
            elif self.provider == "gemini":
                # For Gemini, try OpenAI tools agent first, then fall back to React agent
                try:
                    # Try to use OpenAI tools agent anyway - it might work
                    agent = create_openai_tools_agent(self.llm, self.tools, openai_prompt)
                except Exception as e:
                    logger.warning(f"Could not create OpenAI tools agent for Gemini: {e}")
                    # Create a simple reactive agent as fallback
                    from langchain.agents import create_react_agent
                    agent = create_react_agent(self.llm, self.tools, react_prompt)
            else:
                # For OpenAI, use the standard OpenAI tools agent
                agent = create_openai_tools_agent(self.llm, self.tools, openai_prompt)
            
            # Create agent executor (only if not using fallback)
            if not isinstance(self.llm, FallbackLLMWrapper):
                agent_executor = AgentExecutor(
                    agent=agent,
                    tools=self.tools,
                    verbose=True,
                    handle_parsing_errors=True,
                    max_iterations=10
                )
            
            return agent_executor
            
        except Exception as e:
            logger.error(f"Error creating agent: {e}")
            raise
    
    def generate_response(self, user_input: str) -> str:
        """Generate a response using the LangChain agent."""
        try:
            response = self.agent_executor.invoke({"input": user_input})
            return response.get("output", "I apologize, but I couldn't process your request.")
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"I apologize, but I encountered an error: {e}. Please try again."
    
    def _load_data(self, filename: str) -> List[Dict]:
        """Load data from JSON file."""
        file_path = os.path.join(self.data_dir, filename)
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    return json.load(f)
            else:
                logger.warning(f"Data file {file_path} not found")
                return []
        except Exception as e:
            logger.error(f"Error loading {filename}: {e}")
            return []
    
    def _save_data(self, filename: str, data: List[Dict]):
        """Save data to JSON file."""
        file_path = os.path.join(self.data_dir, filename)
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Data saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving {filename}: {e}")


class FallbackAgentExecutor:
    """Fallback agent executor that provides basic scheduling functionality."""
    
    def __init__(self, tools):
        self.tools = tools
        # Import the basic scheduler agent for fallback functionality
        try:
            from app.agents.scheduler_agent import SchedulerAgent
            from app.config import get_llm
            fallback_llm = get_llm()
            self.scheduler_agent = SchedulerAgent(llm=fallback_llm)
        except Exception as e:
            logger.warning(f"Could not initialize fallback scheduler agent: {e}")
            self.scheduler_agent = None
    
    def invoke(self, inputs):
        """Handle user inputs using the basic scheduler agent."""
        try:
            if self.scheduler_agent:
                response = self.scheduler_agent.generate_response(inputs.get("input", ""))
                return {"output": response}
            else:
                return {"output": "I'm currently in offline mode. Basic scheduling functionality is available through the main application."}
        except Exception as e:
            logger.error(f"Fallback agent error: {e}")
            return {"output": "I'm experiencing technical difficulties. Please try again or use the basic scheduler."}


class FallbackLLMWrapper:
    """Fallback LLM wrapper that provides basic responses when no API is available."""
    
    def __init__(self):
        self.model_name = "fallback-mock"
        self.temperature = 0.3
        
    def bind(self, **kwargs):
        """Mock bind method for LangChain compatibility."""
        return self
        
    def invoke(self, messages):
        """Mock invoke method that returns a basic response."""
        from langchain_core.messages import AIMessage
        return AIMessage(content="I'm currently running in offline mode. I can help with basic appointment scheduling using our local system. What would you like to do?")
        
    def generate(self, messages):
        """Mock generate method."""
        from langchain_core.outputs import LLMResult, Generation
        return LLMResult(generations=[[Generation(text="I'm here to help with appointment scheduling.")]])


class GeminiLangChainWrapper:
    """Wrapper to make SimpleGeminiClient compatible with LangChain."""
    
    def __init__(self, gemini_client):
        self.client = gemini_client
        self.model_name = "gemini-1.5-flash"
    
    def invoke(self, messages, **kwargs):
        """Invoke method for LangChain compatibility."""
        # Convert LangChain messages to our format
        converted_messages = []
        for message in messages:
            if hasattr(message, 'content'):
                if hasattr(message, 'type'):
                    role = "system" if message.type == "system" else "user" if message.type == "human" else "assistant"
                else:
                    role = "user"  # Default to user
                converted_messages.append({"role": role, "content": message.content})
            elif isinstance(message, dict):
                converted_messages.append(message)
        
        try:
            response_data = self.client.create_completion(
                model=self.model_name,
                messages=converted_messages,
                temperature=kwargs.get('temperature', 0.7),
                max_tokens=kwargs.get('max_tokens', 500)
            )
            
            # Return the content directly
            from app.utils.simple_gemini import SimpleGeminiResponse
            response = SimpleGeminiResponse(response_data)
            
            # Create a simple response object that LangChain can use
            class SimpleAIMessage:
                def __init__(self, content):
                    self.content = content
                    self.type = "ai"
            
            return SimpleAIMessage(response.choices[0].message.content)
            
        except Exception as e:
            logger.error(f"Error in GeminiLangChainWrapper: {e}")
            # Return a fallback response
            class SimpleAIMessage:
                def __init__(self, content):
                    self.content = content
                    self.type = "ai"
            return SimpleAIMessage("I'm sorry, I'm having trouble processing your request right now. Please try again later.")


# Test functionality is available in test_agent.py
# Run: python test_agent.py to test the medical scheduling agent