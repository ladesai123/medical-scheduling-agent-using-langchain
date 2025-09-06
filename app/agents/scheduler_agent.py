"""
Medical Scheduling Agent
Handles patient interactions and appointment scheduling logic.
"""
import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Optional

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
    
    def _find_or_create_patient(self) -> Dict:
        """Find existing patient or create a new one from conversation state."""
        patients = self.load_data("patients.json")
        patient_name = self.conversation_state.get("patient_name", "")
        patient_email = self.conversation_state.get("patient_email", "")
        
        # Parse name into first and last
        name_parts = patient_name.strip().split()
        first_name = name_parts[0] if name_parts else "Unknown"
        last_name = " ".join(name_parts[1:]) if len(name_parts) > 1 else "Patient"
        
        # Try to find existing patient by name or email
        for patient in patients:
            if (patient.get("first_name", "").lower() == first_name.lower() and 
                patient.get("last_name", "").lower() == last_name.lower()) or \
               patient.get("email", "").lower() == patient_email.lower():
                # Update email if provided
                if patient_email and patient.get("email") != patient_email:
                    patient["email"] = patient_email
                    self.save_data("patients.json", patients)
                return patient
        
        # Create new patient if not found
        new_patient_id = f"P{len(patients) + 1:04d}"
        new_patient = {
            "patient_id": new_patient_id,
            "first_name": first_name,
            "last_name": last_name,
            "email": patient_email,
            "phone": "",
            "date_of_birth": "",
            "address": {
                "street": "",
                "city": "",
                "state": "",
                "zip_code": ""
            },
            "insurance": {
                "provider": self.conversation_state.get("insurance_provider", ""),
                "policy_number": "",
                "group_number": ""
            },
            "medical_history": [],
            "emergency_contact": {
                "name": "",
                "relationship": "",
                "phone": ""
            },
            "is_new_patient": True
        }
        
        patients.append(new_patient)
        self.save_data("patients.json", patients)
        return new_patient
    
    def _find_available_doctor(self) -> Optional[Dict]:
        """Find an available doctor based on conversation context."""
        doctors = self.load_data("doctors.json")
        specialty_mentioned = self.conversation_state.get("specialty", "").lower()
        
        # If no specialty stored, try to extract from recent inputs
        if not specialty_mentioned:
            specialty_mentioned = ""
        
        # Mapping common terms to specialties
        specialty_mapping = {
            "cardiologist": "cardiology",
            "heart doctor": "cardiology", 
            "heart": "cardiology",
            "dermatologist": "dermatology",
            "skin doctor": "dermatology",
            "skin": "dermatology",
            "general practitioner": "general practice",
            "gp": "general practice",
            "family doctor": "family medicine",
            "anesthesiologist": "anesthesiology"
        }
        
        # Check for specialty matches
        target_specialty = specialty_mentioned
        for term, spec in specialty_mapping.items():
            if term in specialty_mentioned:
                target_specialty = spec
                break
        
        # Find doctors matching the specialty
        if target_specialty:
            for doctor in doctors:
                doctor_specialty = doctor.get("specialty", "").lower()
                if target_specialty in doctor_specialty or doctor_specialty in target_specialty:
                    return doctor
        
        # If looking for cardiologist specifically, try to find cardiology
        if "cardio" in specialty_mentioned:
            for doctor in doctors:
                if "cardio" in doctor.get("specialty", "").lower():
                    return doctor
        
        # Return first available doctor if no specialty match
        return doctors[0] if doctors else None
    
    def _send_confirmation_email(self, appointment: Dict, patient_data: Dict) -> None:
        """Simulate sending a confirmation email."""
        email = patient_data.get("email", "")
        if email:
            logger.info(f"[EMAIL CONFIRMATION] Sent to {email} for appointment {appointment['appointment_id']}")
            # In a real implementation, this would send an actual email
            print(f"\n📧 Email sent to: {email}")
            print(f"Subject: Appointment Confirmation - {appointment['appointment_id']}")
            print(f"Your appointment is confirmed for {appointment['date']} at {appointment['time']}")
        else:
            logger.warning("No email address available for confirmation")
    
    def _handle_appointment_lookup(self, user_input: str, action: str) -> str:
        """Handle appointment lookup for modifications."""
        appointments = self.load_data("appointments.json")
        patients = self.load_data("patients.json")
        doctors = self.load_data("doctors.json")
        
        # Extract name from input
        user_lower = user_input.lower()
        name_parts = []
        
        # Try to extract name (look for patterns like "my name is" or just assume the input is a name)
        if "my name is " in user_lower:
            name_text = user_input[user_lower.index("my name is ") + 11:].strip()
            name_parts = name_text.split()
        elif "i'm " in user_lower:
            name_text = user_input[user_lower.index("i'm ") + 4:].strip()
            name_parts = name_text.split()
        elif "i am " in user_lower:
            name_text = user_input[user_lower.index("i am ") + 5:].strip()
            name_parts = name_text.split()
        else:
            # Remove action words and assume the rest is a name
            clean_input = user_input
            for word in ["cancel", "reschedule", "check", "appointment", "my", "existing"]:
                clean_input = clean_input.replace(word, "").strip()
            name_parts = clean_input.split()
        
        if not name_parts:
            return "Please provide your name so I can look up your appointments."
        
        # Find patient appointments
        patient_appointments = []
        for appointment in appointments:
            appointment_name = appointment.get("patient_name", "").lower()
            if any(part.lower() in appointment_name for part in name_parts):
                # Find doctor info
                doctor = next((d for d in doctors if d["doctor_id"] == appointment["doctor_id"]), None)
                appointment_info = {
                    **appointment,
                    "doctor_name": f"Dr. {doctor['first_name']} {doctor['last_name']}" if doctor else "Unknown Doctor",
                    "doctor_specialty": doctor.get("specialty", "Unknown") if doctor else "Unknown"
                }
                patient_appointments.append(appointment_info)
        
        if not patient_appointments:
            return (f"I couldn't find any appointments for that name. "
                   f"Please make sure you've provided the correct name, or call our office at (555) 123-4567.")
        
        # Handle different actions
        if action == "check":
            self.conversation_state = {}  # Reset conversation
            appointment_list = "\n".join([
                f"• {apt['appointment_id']}: {apt['date']} at {apt['time']} with {apt['doctor_name']} ({apt['doctor_specialty']}) - {apt['status'].title()}"
                for apt in patient_appointments
            ])
            return (f"Here are your appointments:\n\n{appointment_list}\n\n"
                   f"Is there anything else I can help you with?")
        
        elif action == "cancel":
            if len(patient_appointments) == 1:
                apt = patient_appointments[0]
                return self._cancel_appointment(apt)
            else:
                self.conversation_state["appointments_to_modify"] = patient_appointments
                self.conversation_state["conversation_step"] = "select_appointment_cancel"
                appointment_list = "\n".join([
                    f"{i+1}. {apt['appointment_id']}: {apt['date']} at {apt['time']} with {apt['doctor_name']}"
                    for i, apt in enumerate(patient_appointments)
                ])
                return (f"You have multiple appointments. Which one would you like to cancel?\n\n"
                       f"{appointment_list}\n\n"
                       f"Please enter the number of the appointment you want to cancel.")
        
        elif action == "reschedule":
            if len(patient_appointments) == 1:
                apt = patient_appointments[0]
                self.conversation_state["appointment_to_reschedule"] = apt
                self.conversation_state["conversation_step"] = "reschedule_datetime"
                return (f"I'll help you reschedule your appointment:\n"
                       f"Current: {apt['date']} at {apt['time']} with {apt['doctor_name']}\n\n"
                       f"When would you like to reschedule it to? Please provide your preferred date and time.")
            else:
                self.conversation_state["appointments_to_modify"] = patient_appointments
                self.conversation_state["conversation_step"] = "select_appointment_reschedule"
                appointment_list = "\n".join([
                    f"{i+1}. {apt['appointment_id']}: {apt['date']} at {apt['time']} with {apt['doctor_name']}"
                    for i, apt in enumerate(patient_appointments)
                ])
                return (f"You have multiple appointments. Which one would you like to reschedule?\n\n"
                       f"{appointment_list}\n\n"
                       f"Please enter the number of the appointment you want to reschedule.")
    
    def _cancel_appointment(self, appointment: Dict) -> str:
        """Cancel a specific appointment."""
        appointments = self.load_data("appointments.json")
        
        # Find and update the appointment
        for i, apt in enumerate(appointments):
            if apt["appointment_id"] == appointment["appointment_id"]:
                appointments[i]["status"] = "cancelled"
                appointments[i]["cancelled_at"] = datetime.now().isoformat()
                self.save_data("appointments.json", appointments)
                
                self.conversation_state = {}  # Reset conversation
                return (f"Your appointment has been successfully cancelled.\n\n"
                       f"Cancelled Appointment:\n"
                       f"ID: {appointment['appointment_id']}\n"
                       f"Date & Time: {appointment['date']} at {appointment['time']}\n"
                       f"Doctor: {appointment['doctor_name']}\n\n"
                       f"If you need to schedule a new appointment, just let me know!")
        
        return "Sorry, I couldn't find that appointment to cancel."
    
    
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
        
        # Detect intent - check more specific intents first
        if any(word in input_lower for word in ["cancel", "reschedule", "change", "modify", "move"]):
            analysis["intent"] = "modify_appointment"
        elif any(word in input_lower for word in ["schedule", "book", "see doctor", "new appointment"]):
            analysis["intent"] = "schedule_appointment"  
        elif "appointment" in input_lower and any(word in input_lower for word in ["need", "want", "like"]):
            # Only classify as schedule if it's clearly about scheduling
            analysis["intent"] = "schedule_appointment"
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
        if intent == "greeting" and current_step == "initial" and "cancel" not in input_lower and "reschedule" not in input_lower:
            self.conversation_state["conversation_step"] = "name_requested"
            return ("Hello! Welcome to our medical scheduling system. "
                   "I'm here to help you schedule an appointment. "
                   "Could you please tell me your full name?")
        
        # Handle appointment modifications first (before other intents)
        elif intent == "modify_appointment":
            # Direct handling based on the input
            user_lower = user_input.lower()
            if "cancel" in user_lower:
                return self._handle_appointment_lookup(user_input, "cancel")
            elif "reschedule" in user_lower:
                return self._handle_appointment_lookup(user_input, "reschedule")
            elif "check" in user_lower:
                return self._handle_appointment_lookup(user_input, "check")
            else:
                self.conversation_state["conversation_step"] = "modification_type"
                return ("I can help you with appointment changes. "
                       "Would you like to:\n"
                       "1. Cancel an appointment\n"
                       "2. Reschedule an appointment\n"
                       "3. Check your existing appointments\n\n"
                       "Please tell me what you'd like to do and provide your name.")
        
        # Handle name collection - if not obviously an intent, treat as name
        elif current_step == "name_requested":
            if intent not in ["schedule_appointment", "modify_appointment", "greeting"]:
                # Assume this is a name - extract just the name part
                name_input = user_input.strip()
                # Remove common prefixes like "My name is"
                if name_input.lower().startswith("my name is "):
                    name_input = name_input[11:]
                elif name_input.lower().startswith("i'm "):
                    name_input = name_input[4:]
                elif name_input.lower().startswith("i am "):
                    name_input = name_input[5:]
                    
                self.conversation_state["patient_name"] = name_input.strip()
                self.conversation_state["conversation_step"] = "appointment_type"
                return (f"Thank you, {name_input.strip()}. "
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
                # Store the specialty mentioned
                specialty = analysis["entities"].get("specialty")
                if specialty:
                    self.conversation_state["specialty"] = specialty
                    self.conversation_state["conversation_step"] = "datetime_preference"
                    return (f"Great! I'll help you find a {specialty}. "
                           "When would you prefer your appointment? "
                           "Please provide your preferred date and time.")
                else:
                    # If no specialty mentioned yet, capture it from this input
                    if current_step == "appointment_type":
                        self.conversation_state["specialty"] = user_input.strip()
                        self.conversation_state["conversation_step"] = "datetime_preference"
                        return (f"Perfect! I'll help you schedule an appointment with a {user_input.strip()}. "
                               "When would you prefer your appointment? "
                               "Please provide your preferred date and time.")
                    else:
                        self.conversation_state["conversation_step"] = "appointment_type"
                        return ("What type of doctor would you like to see? "
                               "We have cardiologists, dermatologists, general practitioners, "
                               "and many other specialists available.")
        
        # Handle date/time preferences
        elif current_step == "datetime_preference":
            # Parse date and time from user input
            date_time_input = user_input.lower().strip()
            date_pref = "tomorrow"  # default
            time_pref = "10:00 AM"  # default
            
            # Extract date preferences
            if "tomorrow" in date_time_input:
                date_pref = "tomorrow"
            elif "today" in date_time_input:
                date_pref = "today"
            elif "next week" in date_time_input:
                date_pref = "next week"
            elif "monday" in date_time_input:
                date_pref = "next Monday"
            elif "tuesday" in date_time_input:
                date_pref = "next Tuesday"
            elif "wednesday" in date_time_input:
                date_pref = "next Wednesday"
            elif "thursday" in date_time_input:
                date_pref = "next Thursday"
            elif "friday" in date_time_input:
                date_pref = "next Friday"
            else:
                date_pref = user_input.strip()
            
            # Extract time preferences
            if "morning" in date_time_input:
                time_pref = "9:00 AM"
            elif "afternoon" in date_time_input:
                time_pref = "2:00 PM"
            elif "evening" in date_time_input:
                time_pref = "5:00 PM"
            elif "noon" in date_time_input:
                time_pref = "12:00 PM"
            
            self.conversation_state["date_preference"] = date_pref
            self.conversation_state["time_preference"] = time_pref
            self.conversation_state["conversation_step"] = "insurance_info"
            
            return (f"Perfect! I'll check our availability for {date_pref} at {time_pref}. "
                   "Before I confirm your appointment, could you please provide "
                   "your insurance information? What insurance provider do you have?")
        
        # Handle insurance information
        elif current_step == "insurance_info":
            self.conversation_state["insurance_provider"] = user_input.strip()
            self.conversation_state["conversation_step"] = "email_collection"
            return ("Thank you for providing your insurance information. "
                   "To send you a confirmation, could you please provide your email address?")
        
        # Handle email collection and book the appointment
        elif current_step == "email_collection":
            self.conversation_state["patient_email"] = user_input.strip()
            
            # Now actually book the appointment
            try:
                # Find or create patient data
                patient_data = self._find_or_create_patient()
                
                # Find available doctor
                doctor = self._find_available_doctor()
                
                if doctor:
                    # Book the appointment
                    appointment = self.book_appointment(
                        patient_data=patient_data,
                        doctor_id=doctor["doctor_id"],
                        date=self.conversation_state.get("date_preference", "tomorrow"),
                        time=self.conversation_state.get("time_preference", "10:00 AM")
                    )
                    
                    # Send confirmation email (simulated)
                    self._send_confirmation_email(appointment, patient_data)
                    
                    self.conversation_state["conversation_step"] = "confirmation"
                    return (f"Perfect! Your appointment has been successfully booked.\n\n"
                           f"📅 **Appointment Confirmation**\n"
                           f"Appointment ID: {appointment['appointment_id']}\n"
                           f"Patient: {appointment['patient_name']}\n"
                           f"Doctor: Dr. {doctor['first_name']} {doctor['last_name']} ({doctor['specialty']})\n"
                           f"Date & Time: {appointment['date']} at {appointment['time']}\n"
                           f"Status: {appointment['status'].title()}\n\n"
                           f"📧 A confirmation email has been sent to {self.conversation_state['patient_email']}\n\n"
                           f"Is there anything else I can help you with today?")
                else:
                    self.conversation_state["conversation_step"] = "confirmation"
                    return ("I apologize, but we don't have any available doctors for your requested specialty at this time. "
                           "Please call our office at (555) 123-4567 to check alternative options. "
                           "Is there anything else I can help you with?")
                    
            except Exception as e:
                logger.error(f"Error booking appointment: {e}")
                self.conversation_state["conversation_step"] = "confirmation"
                return ("I apologize, but there was an error booking your appointment. "
                       "Please call our office at (555) 123-4567 to book manually. "
                       "Is there anything else I can help you with?")
        
        # Handle appointment modifications
        elif intent == "modify_appointment":
            self.conversation_state["conversation_step"] = "modification_type"
            return ("I can help you with appointment changes. "
                   "Would you like to:\n"
                   "1. Cancel an appointment\n"
                   "2. Reschedule an appointment\n"
                   "3. Check your existing appointments\n\n"
                   "Please tell me what you'd like to do and provide your name.")
        
        # Handle modification requests
        elif current_step == "modification_type":
            user_lower = user_input.lower()
            
            if "cancel" in user_lower:
                self.conversation_state["modification_action"] = "cancel"
                return self._handle_appointment_lookup(user_input, "cancel")
            elif "reschedule" in user_lower:
                self.conversation_state["modification_action"] = "reschedule"
                return self._handle_appointment_lookup(user_input, "reschedule")
            elif "check" in user_lower or "existing" in user_lower:
                self.conversation_state["modification_action"] = "check"
                return self._handle_appointment_lookup(user_input, "check")
            else:
                # Try to extract name and ask for clarification
                return ("Please specify whether you want to cancel, reschedule, or check your appointments.")
        
        # Handle completion
        elif current_step == "confirmation":
            if intent == "negative" or any(word in input_lower for word in ["no", "nothing", "bye", "goodbye", "thanks", "thank you"]):
                self.conversation_state = {}  # Reset for next conversation
                return ("You're welcome! Have a great day and see you at your appointment!")
            else:
                return ("How else can I assist you today? I can help with scheduling, "
                       "rescheduling, or answering questions about our services.")
        
        # Handle appointment selection for cancellation
        elif current_step == "select_appointment_cancel":
            try:
                selection = int(user_input.strip()) - 1
                appointments_list = self.conversation_state.get("appointments_to_modify", [])
                if 0 <= selection < len(appointments_list):
                    return self._cancel_appointment(appointments_list[selection])
                else:
                    return "Please enter a valid appointment number."
            except ValueError:
                return "Please enter a number corresponding to the appointment you want to cancel."
        
        # Handle appointment selection for rescheduling  
        elif current_step == "select_appointment_reschedule":
            try:
                selection = int(user_input.strip()) - 1
                appointments_list = self.conversation_state.get("appointments_to_modify", [])
                if 0 <= selection < len(appointments_list):
                    apt = appointments_list[selection]
                    self.conversation_state["appointment_to_reschedule"] = apt
                    self.conversation_state["conversation_step"] = "reschedule_datetime"
                    return (f"I'll help you reschedule your appointment:\n"
                           f"Current: {apt['date']} at {apt['time']} with {apt['doctor_name']}\n\n"
                           f"When would you like to reschedule it to? Please provide your preferred date and time.")
                else:
                    return "Please enter a valid appointment number."
            except ValueError:
                return "Please enter a number corresponding to the appointment you want to reschedule."
        
        # Handle rescheduling date/time
        elif current_step == "reschedule_datetime":
            # Parse new date and time
            date_time_input = user_input.lower().strip()
            new_date = "tomorrow"  # default
            new_time = "10:00 AM"  # default
            
            # Extract date preferences (same logic as before)
            if "tomorrow" in date_time_input:
                new_date = "tomorrow"
            elif "today" in date_time_input:
                new_date = "today"
            elif "next week" in date_time_input:
                new_date = "next week"
            elif "monday" in date_time_input:
                new_date = "next Monday"
            elif "tuesday" in date_time_input:
                new_date = "next Tuesday"
            elif "wednesday" in date_time_input:
                new_date = "next Wednesday"
            elif "thursday" in date_time_input:
                new_date = "next Thursday"
            elif "friday" in date_time_input:
                new_date = "next Friday"
            else:
                new_date = user_input.strip()
            
            # Extract time preferences
            if "morning" in date_time_input:
                new_time = "9:00 AM"
            elif "afternoon" in date_time_input:
                new_time = "2:00 PM"
            elif "evening" in date_time_input:
                new_time = "5:00 PM"
            elif "noon" in date_time_input:
                new_time = "12:00 PM"
            
            # Update the appointment
            appointment_to_reschedule = self.conversation_state.get("appointment_to_reschedule")
            if appointment_to_reschedule:
                appointments = self.load_data("appointments.json")
                for i, apt in enumerate(appointments):
                    if apt["appointment_id"] == appointment_to_reschedule["appointment_id"]:
                        old_date = apt["date"]
                        old_time = apt["time"]
                        appointments[i]["date"] = new_date
                        appointments[i]["time"] = new_time
                        appointments[i]["rescheduled_at"] = datetime.now().isoformat()
                        self.save_data("appointments.json", appointments)
                        
                        self.conversation_state = {}  # Reset conversation
                        return (f"Your appointment has been successfully rescheduled!\n\n"
                               f"**Updated Appointment Details:**\n"
                               f"ID: {appointment_to_reschedule['appointment_id']}\n"
                               f"Previous: {old_date} at {old_time}\n"
                               f"New: {new_date} at {new_time}\n"
                               f"Doctor: {appointment_to_reschedule['doctor_name']}\n\n"
                               f"Is there anything else I can help you with?")
                
            return "Sorry, I couldn't find that appointment to reschedule."
        
        # Default response
        else:
            return ("I'm here to help with scheduling medical appointments. "
                   "You can ask me to schedule a new appointment, cancel an existing one, "
                   "or check available times. How can I assist you today?")


# Test functionality is available in test_agent.py  
# Run: python test_agent.py to test the medical scheduling agent