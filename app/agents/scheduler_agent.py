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
        input_lower = user_input.lower()
        
        analysis = {
            "intent": "general",
            "entities": {},
            "needs_info": []
        }
        
        # Detect intent
        if any(word in input_lower for word in ["schedule", "book", "appointment", "see doctor"]):
            analysis["intent"] = "schedule_appointment"
        elif any(word in input_lower for word in ["cancel", "reschedule"]):
            analysis["intent"] = "modify_appointment"
        elif any(word in input_lower for word in ["hello", "hi", "help"]):
            analysis["intent"] = "greeting"
        
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
        
        return analysis
    
    def generate_response(self, user_input: str) -> str:
        """Generate a response to user input."""
        try:
            # Analyze the input
            analysis = self.analyze_user_input(user_input)
            
            # Use LLM if available, otherwise use rule-based responses
            if self.llm:
                # Create context for the LLM
                context = f"""
                User input: {user_input}
                Intent: {analysis['intent']}
                Entities: {analysis['entities']}
                Current conversation state: {self.conversation_state}
                """
                
                response = self.llm.generate_response(context)
            else:
                response = self._generate_rule_based_response(user_input, analysis)
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "I apologize, but I'm experiencing some technical difficulties. Please try again."
    
    def _generate_rule_based_response(self, user_input: str, analysis: Dict) -> str:
        """Generate rule-based responses when LLM is not available."""
        intent = analysis["intent"]
        
        if intent == "greeting":
            return ("Hello! Welcome to our medical scheduling system. "
                   "I'm here to help you schedule an appointment. "
                   "Could you please tell me your name?")
        
        elif intent == "schedule_appointment":
            if "patient_name" not in self.conversation_state:
                return ("I'd be happy to help you schedule an appointment. "
                       "Could you please tell me your full name?")
            else:
                return ("Great! What type of doctor would you like to see, "
                       "and do you have a preferred date and time?")
        
        elif intent == "modify_appointment":
            return ("I can help you with appointment changes. "
                   "Could you please provide your name and current appointment details?")
        
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