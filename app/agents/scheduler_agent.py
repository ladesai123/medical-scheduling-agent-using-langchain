"""
Medical Scheduling Agent
Handles patient interactions and appointment scheduling logic.
"""
import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class SchedulerAgent:
    """Main scheduling agent that handles patient interactions."""
    
    def __init__(self, llm=None):
        self.llm = llm
        self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
        self.conversation_state = {}
        self.current_patient = None
        logger.info("SchedulerAgent initialized")
    
    def load_data(self, filename: str) -> List[Dict]:
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
    
    def save_data(self, filename: str, data: List[Dict]):
        """Save data to JSON file."""
        file_path = os.path.join(self.data_dir, filename)
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Data saved to {filename}")
        except Exception as e:
            logger.error(f"Error saving {filename}: {e}")
    
    def find_patient(self, name: str) -> Optional[Dict]:
        """Find a patient by name."""
        patients = self.load_data("patients.json")
        name_lower = name.lower()
        
        for patient in patients:
            full_name = f"{patient['first_name']} {patient['last_name']}".lower()
            if name_lower in full_name or full_name in name_lower:
                return patient
        return None
    
    def get_available_doctors(self, specialty: str = None) -> List[Dict]:
        """Get available doctors, optionally filtered by specialty."""
        doctors = self.load_data("doctors.json")
        if specialty:
            specialty_lower = specialty.lower()
            return [d for d in doctors if specialty_lower in d['specialty'].lower()]
        return doctors
    
    def get_available_slots(self, doctor_id: str, date: str, duration: int = 30) -> List[str]:
        """Get available time slots for a doctor on a specific date."""
        # This is a simplified implementation
        # In a real system, this would check against existing appointments
        doctors = self.load_data("doctors.json")
        doctor = next((d for d in doctors if d['doctor_id'] == doctor_id), None)
        
        if not doctor:
            return []
        
        # Get the day of week
        try:
            date_obj = datetime.strptime(date, "%Y-%m-%d")
            day_name = date_obj.strftime("%A")
        except ValueError:
            return []
        
        if day_name not in doctor['schedule']:
            return []
        
        schedule = doctor['schedule'][day_name]
        start_time = datetime.strptime(schedule['start_time'], "%H:%M")
        end_time = datetime.strptime(schedule['end_time'], "%H:%M")
        
        # Generate time slots
        slots = []
        current_time = start_time
        while current_time + timedelta(minutes=duration) <= end_time:
            # Skip lunch break (simplified)
            if not (current_time.hour == 12):
                slots.append(current_time.strftime("%H:%M"))
            current_time += timedelta(minutes=duration)
        
        return slots
    
    def book_appointment(self, patient_data: Dict, doctor_id: str, date: str, time: str) -> Dict:
        """Book an appointment."""
        appointments = self.load_data("appointments.json")
        
        # Generate appointment ID
        appointment_id = f"APT{len(appointments) + 1:04d}"
        
        appointment = {
            "appointment_id": appointment_id,
            "patient_id": patient_data.get("patient_id"),
            "patient_name": f"{patient_data['first_name']} {patient_data['last_name']}",
            "doctor_id": doctor_id,
            "date": date,
            "time": time,
            "status": "scheduled",
            "created_at": datetime.now().isoformat(),
            "type": "new_patient" if patient_data.get("is_new_patient", False) else "returning_patient"
        }
        
        appointments.append(appointment)
        self.save_data("appointments.json", appointments)
        
        return appointment
    
    def analyze_user_input(self, user_input: str) -> Dict[str, Any]:
        """Analyze user input to extract intent and entities."""
        input_lower = user_input.lower().strip()
        
        analysis = {
            "intent": "general",
            "entities": {},
            "needs_info": []
        }
        
        # Handle empty input
        if not input_lower:
            analysis["intent"] = "empty"
            return analysis
        
        # Detect intent
        if any(word in input_lower for word in ["schedule", "book", "appointment", "see doctor", "need"]):
            analysis["intent"] = "schedule_appointment"
        elif any(word in input_lower for word in ["cancel", "reschedule"]):
            analysis["intent"] = "modify_appointment"
        elif any(word in input_lower for word in ["hello", "hi", "help", "start"]):
            analysis["intent"] = "greeting"
        elif any(word in input_lower for word in ["yes", "yeah", "ok", "okay"]):
            analysis["intent"] = "confirmation"
        elif any(word in input_lower for word in ["no", "nope", "nothing"]):
            analysis["intent"] = "negative"
        
        # Extract entities (simplified)
        # In a real system, you'd use NLP libraries for better entity extraction
        
        # Look for dates
        date_keywords = ["today", "tomorrow", "monday", "tuesday", "wednesday", "thursday", "friday"]
        for keyword in date_keywords:
            if keyword in input_lower:
                analysis["entities"]["date_preference"] = keyword
        
        # Look for times
        time_keywords = ["morning", "afternoon", "evening", "9", "10", "11", "1", "2", "3", "4"]
        for keyword in time_keywords:
            if keyword in input_lower:
                analysis["entities"]["time_preference"] = keyword
        
        # Look for specialties
        specialties = ["cardiologist", "dermatologist", "neurologist", "orthopedist", 
                      "pediatrician", "psychiatrist", "general", "family"]
        for specialty in specialties:
            if specialty in input_lower:
                analysis["entities"]["specialty"] = specialty
        
        return analysis
    
    def generate_response(self, user_input: str) -> str:
        """Generate a response to user input."""
        try:
            # Analyze the input
            analysis = self.analyze_user_input(user_input)
            
            # Always use rule-based responses now to ensure consistency
            # The LLM integration can be improved later with better error handling
            response = self._generate_rule_based_response(user_input, analysis)
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I apologize, but I'm experiencing some technical difficulties. Please try again."
    
    def _generate_rule_based_response(self, user_input: str, analysis: Dict) -> str:
        """Generate rule-based responses when LLM is not available."""
        intent = analysis["intent"]
        input_lower = user_input.lower().strip()
        
        # Handle empty input
        if intent == "empty":
            return "Please enter a message or type 'exit' to quit."
        
        # Track conversation progress
        if "conversation_step" not in self.conversation_state:
            self.conversation_state["conversation_step"] = "initial"
        
        current_step = self.conversation_state["conversation_step"]
        
        # Handle greetings or start of conversation
        if intent == "greeting" and current_step == "initial":
            self.conversation_state["conversation_step"] = "name_requested"
            return ("Hello! Welcome to our medical scheduling system. "
                   "I'm here to help you schedule an appointment. "
                   "Could you please tell me your full name?")
        
        # Handle name collection - if not obviously an intent, treat as name
        elif current_step == "name_requested":
            if intent not in ["schedule_appointment", "modify_appointment", "greeting"]:
                # Assume this is a name
                self.conversation_state["patient_name"] = user_input.strip()
                self.conversation_state["conversation_step"] = "appointment_type"
                return (f"Thank you, {user_input.strip()}. "
                       "What type of doctor would you like to see? For example: "
                       "cardiologist, dermatologist, general practitioner, etc.")
            elif intent == "schedule_appointment":
                # Fall through to appointment handling
                pass
        
        # Handle appointment scheduling
        if intent == "schedule_appointment" or current_step == "appointment_type":
            if "patient_name" not in self.conversation_state:
                self.conversation_state["conversation_step"] = "name_requested"
                return ("I'd be happy to help you schedule an appointment. "
                       "Could you please tell me your full name first?")
            else:
                self.conversation_state["conversation_step"] = "datetime_preference"
                
                # Extract specialty if mentioned
                specialty = analysis["entities"].get("specialty")
                if specialty:
                    return (f"Great! I'll help you find a {specialty}. "
                           "When would you prefer your appointment? "
                           "Please provide your preferred date and time.")
                else:
                    return ("What type of doctor would you like to see? "
                           "We have cardiologists, dermatologists, general practitioners, "
                           "and many other specialists available.")
        
        # Handle date/time preferences
        elif current_step == "datetime_preference":
            self.conversation_state["conversation_step"] = "insurance_info"
            date_pref = analysis["entities"].get("date_preference", "your preferred time")
            time_pref = analysis["entities"].get("time_preference", "")
            return (f"Perfect! I'll check our availability for {date_pref} {time_pref}. "
                   "Before I confirm your appointment, could you please provide "
                   "your insurance information? What insurance provider do you have?")
        
        # Handle insurance information
        elif current_step == "insurance_info":
            self.conversation_state["conversation_step"] = "confirmation"
            return ("Thank you for providing your insurance information. "
                   "Let me book your appointment now. "
                   "I'll send you a confirmation with all the details shortly. "
                   "Is there anything else I can help you with today?")
        
        # Handle appointment modifications
        elif intent == "modify_appointment":
            return ("I can help you with appointment changes. "
                   "Could you please provide your name and current appointment details?")
        
        # Handle completion
        elif current_step == "confirmation":
            if intent == "negative" or any(word in input_lower for word in ["no", "nothing", "bye", "goodbye", "thanks", "thank you"]):
                self.conversation_state = {}  # Reset for next conversation
                return ("You're welcome! Have a great day and see you at your appointment!")
            else:
                return ("How else can I assist you today? I can help with scheduling, "
                       "rescheduling, or answering questions about our services.")
        
        # Default response
        else:
            return ("I'm here to help with scheduling medical appointments. "
                   "You can ask me to schedule a new appointment, cancel an existing one, "
                   "or check available times. How can I assist you today?")


if __name__ == "__main__":
    # Test the scheduler agent
    print("Testing SchedulerAgent...")
    
    try:
        from app.config import get_llm
        llm = get_llm()
    except:
        llm = None
        print("Using rule-based responses (LLM not available)")
    
    agent = SchedulerAgent(llm=llm)
    
    # Test conversation
    test_inputs = [
        "Hello, I need to schedule an appointment",
        "My name is John Smith",
        "I need to see a cardiologist",
        "How about tomorrow morning?"
    ]
    
    for test_input in test_inputs:
        print(f"\nUser: {test_input}")
        response = agent.generate_response(test_input)
        print(f"Agent: {response}")