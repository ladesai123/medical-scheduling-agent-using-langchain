"""
Enhanced Medical Scheduling Agent with fallback
This version provides a robust fallback system when OpenAI API is not available.
"""

import json
import os
import logging
from datetime import datetime, timedelta, date
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class MockLangChainAgent:
    """Mock LangChain agent that provides rule-based responses with enhanced features."""
    
    def __init__(self, data_dir: str = None):
        """Initialize the mock agent."""
        if data_dir is None:
            self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
        else:
            self.data_dir = data_dir
        
        from app.utils.calendar_manager import CalendarManager
        from app.utils.notification_manager import NotificationManager
        
        self.calendar_manager = CalendarManager(self.data_dir)
        self.notification_manager = NotificationManager(self.data_dir)
        self.conversation_state = {}
        
        logger.info("MockLangChainAgent initialized with enhanced features")
    
    def generate_response(self, user_input: str) -> str:
        """Generate a rule-based response with enhanced functionality."""
        try:
            input_lower = user_input.lower()
            
            # Appointment booking workflow
            if any(word in input_lower for word in ["schedule", "book", "appointment", "need to see"]):
                return self._handle_booking_request(user_input)
            
            # Check availability
            elif any(word in input_lower for word in ["available", "availability", "free", "open slots"]):
                return self._handle_availability_request(user_input)
            
            # Reschedule request
            elif any(word in input_lower for word in ["reschedule", "change", "move"]):
                return self._handle_reschedule_request(user_input)
            
            # Cancel request
            elif any(word in input_lower for word in ["cancel", "delete"]):
                return self._handle_cancel_request(user_input)
            
            # Export request
            elif any(word in input_lower for word in ["export", "excel", "download", "report"]):
                return self._handle_export_request(user_input)
            
            # Insurance validation
            elif any(word in input_lower for word in ["insurance", "coverage", "policy"]):
                return self._handle_insurance_request(user_input)
            
            # Patient lookup
            elif any(word in input_lower for word in ["patient", "lookup", "find", "search"]):
                return self._handle_patient_lookup(user_input)
            
            # Greeting or general help
            elif any(word in input_lower for word in ["hello", "hi", "help", "start"]):
                return self._get_welcome_message()
            
            else:
                return self._get_help_message()
            
        except Exception as e:
            logger.error(f"Error in generate_response: {e}")
            return f"I apologize, but I encountered an error: {e}. Please try again."
    
    def _handle_booking_request(self, user_input: str) -> str:
        """Handle appointment booking requests."""
        try:
            # Extract information from input
            input_lower = user_input.lower()
            
            # Look for doctor specialties
            specialties = ["cardiologist", "dermatologist", "neurologist", "orthopedist", "general", "psychiatrist"]
            specialty = None
            for spec in specialties:
                if spec in input_lower:
                    specialty = spec
                    break
            
            if specialty:
                # Get available doctors
                doctors = self._load_data("doctors.json")
                matching_doctors = [d for d in doctors if specialty.lower() in d['specialty'].lower()]
                
                if matching_doctors:
                    doctor = matching_doctors[0]  # Take first match
                    
                    # Get next available date (7 days from now)
                    next_week = (date.today() + timedelta(days=7)).strftime("%Y-%m-%d")
                    available_slots = self.calendar_manager.get_available_slots(
                        doctor['doctor_id'], next_week, 30
                    )
                    
                    if available_slots:
                        response = f"I found Dr. {doctor['first_name']} {doctor['last_name']}, a {doctor['specialty']}.\n\n"
                        response += f"Available slots on {next_week}:\n"
                        for slot in available_slots[:5]:
                            response += f"• {slot}\n"
                        response += f"\nTo book an appointment, please provide:\n"
                        response += f"1. Your full name\n"
                        response += f"2. Your preferred time slot\n"
                        response += f"3. Your email address\n"
                        response += f"4. Are you a new or returning patient?\n"
                        return response
                    else:
                        return f"Dr. {doctor['first_name']} {doctor['last_name']} has no available slots on {next_week}. Would you like to check another date?"
                else:
                    return f"I couldn't find any {specialty}s available. Our available specialties include: Cardiology, Dermatology, Neurology, Orthopedics, General Practice, and Psychiatry."
            else:
                return "I'd be happy to help you schedule an appointment! What type of doctor would you like to see? (e.g., cardiologist, dermatologist, general practitioner)"
            
        except Exception as e:
            logger.error(f"Error handling booking request: {e}")
            return f"I'm having trouble processing your booking request. Please try again or contact our office directly."
    
    def _handle_availability_request(self, user_input: str) -> str:
        """Handle availability check requests."""
        try:
            # Extract doctor name or specialty from input
            words = user_input.lower().split()
            
            # Look for doctor names or specialties
            doctors = self._load_data("doctors.json")
            
            matching_doctor = None
            for doctor in doctors:
                doctor_name = f"{doctor['first_name']} {doctor['last_name']}".lower()
                if any(word in doctor_name for word in words):
                    matching_doctor = doctor
                    break
                elif doctor['specialty'].lower() in user_input.lower():
                    matching_doctor = doctor
                    break
            
            if matching_doctor:
                # Check availability for next week
                next_week = (date.today() + timedelta(days=7)).strftime("%Y-%m-%d")
                available_slots = self.calendar_manager.get_available_slots(
                    matching_doctor['doctor_id'], next_week, 30
                )
                
                response = f"Availability for Dr. {matching_doctor['first_name']} {matching_doctor['last_name']} ({matching_doctor['specialty']}) on {next_week}:\n\n"
                
                if available_slots:
                    for slot in available_slots[:8]:
                        response += f"• {slot}\n"
                    if len(available_slots) > 8:
                        response += f"... and {len(available_slots) - 8} more slots available\n"
                else:
                    response += "No available slots on this date.\n"
                
                response += "\nWould you like to check another date or book one of these slots?"
                return response
            else:
                return "Please specify which doctor or specialty you'd like to check availability for."
            
        except Exception as e:
            logger.error(f"Error handling availability request: {e}")
            return "I'm having trouble checking availability. Please try again."
    
    def _handle_reschedule_request(self, user_input: str) -> str:
        """Handle appointment rescheduling requests."""
        # For simplicity, ask for appointment ID
        return ("To reschedule your appointment, I'll need:\n"
                "1. Your appointment ID (e.g., APT0001)\n"
                "2. Your preferred new date\n"
                "3. Your preferred new time\n\n"
                "You can find your appointment ID in your confirmation email.")
    
    def _handle_cancel_request(self, user_input: str) -> str:
        """Handle appointment cancellation requests."""
        return ("To cancel your appointment, I'll need:\n"
                "1. Your appointment ID (e.g., APT0001)\n"
                "2. The reason for cancellation (optional)\n\n"
                "Please note: Cancellations must be made at least 24 hours in advance.")
    
    def _handle_export_request(self, user_input: str) -> str:
        """Handle data export requests."""
        try:
            filepath = self.calendar_manager.export_to_excel()
            if filepath:
                return f"✅ Appointment data has been exported to Excel file: {filepath}\n\nThe file contains all current appointment information for administrative review."
            else:
                return "❌ Failed to export appointment data. Please try again later."
        except Exception as e:
            logger.error(f"Error handling export request: {e}")
            return "I'm having trouble exporting the data. Please contact IT support."
    
    def _handle_insurance_request(self, user_input: str) -> str:
        """Handle insurance-related requests."""
        return ("I can help verify your insurance information. Please provide:\n"
                "1. Insurance carrier name (e.g., Blue Cross, Aetna, Cigna)\n"
                "2. Member ID number\n"
                "3. Group number (if applicable)\n\n"
                "This information helps us verify your coverage and benefits.")
    
    def _handle_patient_lookup(self, user_input: str) -> str:
        """Handle patient lookup requests."""
        words = user_input.split()
        
        # Try to extract a name
        potential_name = ""
        for i, word in enumerate(words):
            if word.lower() in ["find", "search", "lookup", "patient"]:
                if i + 1 < len(words):
                    potential_name = " ".join(words[i+1:])
                    break
        
        if potential_name:
            try:
                patients = self._load_data("patients.json")
                matching_patients = []
                
                for patient in patients:
                    full_name = f"{patient['first_name']} {patient['last_name']}".lower()
                    if potential_name.lower() in full_name:
                        matching_patients.append(patient)
                
                if matching_patients:
                    if len(matching_patients) == 1:
                        patient = matching_patients[0]
                        return f"Found patient: {patient['first_name']} {patient['last_name']}\nPatient ID: {patient['patient_id']}\nDate of Birth: {patient['date_of_birth']}"
                    else:
                        response = f"Found {len(matching_patients)} patients with similar names:\n"
                        for i, patient in enumerate(matching_patients[:3]):
                            response += f"{i+1}. {patient['first_name']} {patient['last_name']} (DOB: {patient['date_of_birth']})\n"
                        return response
                else:
                    return f"No patient found with name '{potential_name}'. This appears to be a new patient."
            except Exception as e:
                logger.error(f"Error in patient lookup: {e}")
                return "I'm having trouble looking up patient information. Please try again."
        else:
            return "To look up a patient, please provide their name. For example: 'Find patient John Smith'"
    
    def _get_welcome_message(self) -> str:
        """Get welcome message."""
        return ("👋 Hello! I'm your AI Medical Scheduling Assistant powered by LangChain. I can help you:\n\n"
                "• **Schedule new appointments** with our specialists\n"
                "• **Check doctor availability** and view open time slots\n"
                "• **Reschedule or cancel** existing appointments\n"
                "• **Verify insurance** information\n"
                "• **Look up patient** records and appointment history\n"
                "• **Export appointment data** for administrative review\n\n"
                "What would you like to do today? 😊")
    
    def _get_help_message(self) -> str:
        """Get help message."""
        return ("I can help you with medical appointment scheduling. Here are some things you can ask:\n\n"
                "• 'I need to schedule an appointment with a cardiologist'\n"
                "• 'Check availability for Dr. Smith next week'\n"
                "• 'Reschedule my appointment APT0001'\n"
                "• 'Cancel appointment APT0002'\n"
                "• 'Look up patient John Doe'\n"
                "• 'Export appointments to Excel'\n"
                "• 'Verify my insurance coverage'\n\n"
                "How can I assist you today?")
    
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


if __name__ == "__main__":
    # Test the mock agent
    print("Testing MockLangChainAgent...")
    
    import sys
    import os
    sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
    
    agent = MockLangChainAgent()
    
    test_inputs = [
        "Hello, I need help",
        "I need to schedule an appointment with a cardiologist", 
        "Check availability for next week",
        "Export appointments to Excel"
    ]
    
    for test_input in test_inputs:
        print(f"\nUser: {test_input}")
        response = agent.generate_response(test_input)
        print(f"Agent: {response}")
    
    print("\nMockLangChainAgent test completed!")