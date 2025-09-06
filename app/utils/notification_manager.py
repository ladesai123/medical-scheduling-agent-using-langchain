"""
Notification System
Handles email and SMS reminders for appointments.
"""

import json
import os
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from email_validator import validate_email, EmailNotValidError
import schedule
import time

logger = logging.getLogger(__name__)


class NotificationManager:
    """Manages email and SMS notifications for appointments."""
    
    def __init__(self, data_dir: str = None):
        """Initialize notification manager."""
        if data_dir is None:
            self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
        else:
            self.data_dir = data_dir
        
        self.reminder_schedule = {
            "first_reminder": 7,   # 7 days before
            "second_reminder": 3,  # 3 days before
            "third_reminder": 1    # 1 day before
        }
        
        logger.info("NotificationManager initialized")
    
    def send_confirmation_email(self, appointment: Dict, patient: Dict) -> Dict:
        """Send appointment confirmation email."""
        try:
            email = patient.get("email", "")
            if not email:
                return {
                    "success": False,
                    "message": "No email address available"
                }
            
            # Validate email
            try:
                valid = validate_email(email)
                email = valid.email
            except EmailNotValidError:
                return {
                    "success": False,
                    "message": f"Invalid email address: {email}"
                }
            
            # Create email content
            email_content = self._create_confirmation_email_content(appointment, patient)
            
            # Simulate sending email
            result = self._simulate_email_send(email, email_content)
            
            # Log the confirmation
            logger.info(f"📧 Confirmation email sent to: {patient.get('first_name', '')} {patient.get('last_name', '')}")
            print(f"\n📧 Email sent to: {patient.get('first_name', '')} {patient.get('last_name', '')}")
            print(f"Subject: {email_content['subject']}")
            print(f"Message: {email_content['preview']}")
            
            return {
                "success": True,
                "message": f"Confirmation email sent to {email}",
                "email_id": result.get("email_id")
            }
            
        except Exception as e:
            logger.error(f"Error sending confirmation email: {e}")
            return {
                "success": False,
                "message": f"Error sending email: {e}"
            }
    
    def send_reminder_email(self, appointment: Dict, patient: Dict, reminder_type: str = "first") -> Dict:
        """Send appointment reminder email."""
        try:
            email = patient.get("email", "")
            if not email:
                return {
                    "success": False,
                    "message": "No email address available"
                }
            
            # Create reminder content
            email_content = self._create_reminder_email_content(appointment, patient, reminder_type)
            
            # Simulate sending email
            result = self._simulate_email_send(email, email_content)
            
            logger.info(f"📧 {reminder_type} reminder email sent to: {patient.get('first_name', '')} {patient.get('last_name', '')}")
            
            return {
                "success": True,
                "message": f"{reminder_type} reminder email sent to {email}",
                "email_id": result.get("email_id")
            }
            
        except Exception as e:
            logger.error(f"Error sending reminder email: {e}")
            return {
                "success": False,
                "message": f"Error sending reminder: {e}"
            }
    
    def send_sms_reminder(self, appointment: Dict, patient: Dict, reminder_type: str = "first") -> Dict:
        """Send appointment reminder SMS."""
        try:
            phone = patient.get("phone", "")
            if not phone:
                return {
                    "success": False,
                    "message": "No phone number available"
                }
            
            # Create SMS content
            sms_content = self._create_reminder_sms_content(appointment, patient, reminder_type)
            
            # Simulate sending SMS
            result = self._simulate_sms_send(phone, sms_content)
            
            logger.info(f"📱 {reminder_type} SMS reminder sent to: {patient.get('first_name', '')} {patient.get('last_name', '')}")
            print(f"\n📱 SMS sent to: {patient.get('first_name', '')} {patient.get('last_name', '')}")
            print(f"Message: {sms_content['message']}")
            
            return {
                "success": True,
                "message": f"{reminder_type} SMS reminder sent to {phone}",
                "sms_id": result.get("sms_id")
            }
            
        except Exception as e:
            logger.error(f"Error sending SMS reminder: {e}")
            return {
                "success": False,
                "message": f"Error sending SMS: {e}"
            }
    
    def send_intake_forms(self, appointment: Dict, patient: Dict) -> Dict:
        """Send patient intake forms after appointment confirmation."""
        try:
            email = patient.get("email", "")
            if not email:
                return {
                    "success": False,
                    "message": "No email address available for forms"
                }
            
            # Create forms email content
            email_content = self._create_forms_email_content(appointment, patient)
            
            # Simulate sending email with forms
            result = self._simulate_email_send(email, email_content)
            
            logger.info(f"📋 Intake forms sent to: {patient.get('first_name', '')} {patient.get('last_name', '')}")
            print(f"\n📋 Intake forms sent to: {patient.get('first_name', '')} {patient.get('last_name', '')}")
            print(f"Subject: {email_content['subject']}")
            
            return {
                "success": True,
                "message": f"Intake forms sent to {email}",
                "email_id": result.get("email_id")
            }
            
        except Exception as e:
            logger.error(f"Error sending intake forms: {e}")
            return {
                "success": False,
                "message": f"Error sending forms: {e}"
            }
    
    def schedule_reminders(self, appointment: Dict, patient: Dict):
        """Schedule all reminders for an appointment."""
        try:
            appointment_date = datetime.strptime(appointment.get('date', ''), "%Y-%m-%d")
            
            # Schedule first reminder (7 days before)
            first_reminder_date = appointment_date - timedelta(days=self.reminder_schedule["first_reminder"])
            if first_reminder_date > datetime.now():
                self._schedule_reminder(appointment, patient, first_reminder_date, "first")
            
            # Schedule second reminder (3 days before)
            second_reminder_date = appointment_date - timedelta(days=self.reminder_schedule["second_reminder"])
            if second_reminder_date > datetime.now():
                self._schedule_reminder(appointment, patient, second_reminder_date, "second")
            
            # Schedule third reminder (1 day before)
            third_reminder_date = appointment_date - timedelta(days=self.reminder_schedule["third_reminder"])
            if third_reminder_date > datetime.now():
                self._schedule_reminder(appointment, patient, third_reminder_date, "third")
            
            logger.info(f"Reminders scheduled for appointment {appointment.get('appointment_id')}")
            
        except Exception as e:
            logger.error(f"Error scheduling reminders: {e}")
    
    def send_interactive_reminder(self, appointment: Dict, patient: Dict, reminder_type: str) -> Dict:
        """Send interactive reminder with questions for 2nd and 3rd reminders."""
        try:
            email = patient.get("email", "")
            if not email:
                return {"success": False, "message": "No email available"}
            
            questions = []
            
            if reminder_type in ["second", "third"]:
                questions = [
                    "Have you completed the patient intake forms?",
                    "Is your visit still confirmed?",
                    "If cancelling, please provide a reason."
                ]
            
            # Create interactive email content
            email_content = self._create_interactive_email_content(appointment, patient, reminder_type, questions)
            
            # Simulate sending email
            result = self._simulate_email_send(email, email_content)
            
            logger.info(f"📧 Interactive {reminder_type} reminder sent to: {patient.get('first_name', '')} {patient.get('last_name', '')}")
            
            return {
                "success": True,
                "message": f"Interactive {reminder_type} reminder sent",
                "email_id": result.get("email_id"),
                "questions": questions
            }
            
        except Exception as e:
            logger.error(f"Error sending interactive reminder: {e}")
            return {"success": False, "message": f"Error: {e}"}
    
    def process_reminder_response(self, appointment_id: str, responses: Dict) -> Dict:
        """Process responses from interactive reminders."""
        try:
            # Load appointments
            appointments = self._load_appointments()
            
            # Find appointment
            appointment = None
            for apt in appointments:
                if apt.get('appointment_id') == appointment_id:
                    appointment = apt
                    break
            
            if not appointment:
                return {"success": False, "message": "Appointment not found"}
            
            # Process responses
            appointment['reminder_responses'] = appointment.get('reminder_responses', {})
            appointment['reminder_responses'][datetime.now().isoformat()] = responses
            
            # Handle cancellation if indicated
            if responses.get('visit_confirmed', '').lower() in ['no', 'false', 'cancel']:
                appointment['status'] = 'cancelled'
                appointment['cancelled_at'] = datetime.now().isoformat()
                appointment['cancellation_reason'] = responses.get('cancellation_reason', 'Patient initiated')
            
            # Update appointment
            self._save_appointments(appointments)
            
            return {
                "success": True,
                "message": "Reminder response processed",
                "appointment": appointment
            }
            
        except Exception as e:
            logger.error(f"Error processing reminder response: {e}")
            return {"success": False, "message": f"Error: {e}"}
    
    def _create_confirmation_email_content(self, appointment: Dict, patient: Dict) -> Dict:
        """Create confirmation email content."""
        subject = f"Appointment Confirmation - {appointment.get('appointment_id', 'N/A')}"
        
        content = f"""
Dear {patient.get('first_name', '')} {patient.get('last_name', '')},

Your appointment has been successfully scheduled!

📅 **Appointment Details:**
• Appointment ID: {appointment.get('appointment_id', 'N/A')}
• Date: {appointment.get('date', 'N/A')}
• Time: {appointment.get('time', 'N/A')}
• Duration: {appointment.get('duration_minutes', 30)} minutes
• Doctor: {appointment.get('doctor_name', 'N/A')}
• Specialty: {appointment.get('specialty', 'N/A')}
• Location: {appointment.get('location', 'Main Office')}

📋 **Next Steps:**
• You will receive patient intake forms shortly
• Please arrive 15 minutes early
• Bring a valid ID and insurance card
• Bring a list of current medications

If you need to reschedule or cancel, please contact us at least 24 hours in advance.

Thank you for choosing HealthCare+ Medical Center!

Best regards,
HealthCare+ Team
"""
        
        return {
            "subject": subject,
            "content": content,
            "preview": f"Your appointment is confirmed for {appointment.get('date')} at {appointment.get('time')}"
        }
    
    def _create_reminder_email_content(self, appointment: Dict, patient: Dict, reminder_type: str) -> Dict:
        """Create reminder email content."""
        days_map = {"first": 7, "second": 3, "third": 1}
        days = days_map.get(reminder_type, 1)
        
        subject = f"Appointment Reminder - {days} day{'s' if days > 1 else ''} to go"
        
        content = f"""
Dear {patient.get('first_name', '')} {patient.get('last_name', '')},

This is a friendly reminder about your upcoming appointment.

📅 **Appointment Details:**
• Date: {appointment.get('date', 'N/A')}
• Time: {appointment.get('time', 'N/A')}
• Doctor: {appointment.get('doctor_name', 'N/A')}
• Location: {appointment.get('location', 'Main Office')}

📋 **Reminders:**
• Please arrive 15 minutes early
• Bring your insurance card and ID
• Complete any intake forms if not done already

If you need to reschedule or cancel, please contact us as soon as possible.

See you soon!

HealthCare+ Team
"""
        
        return {
            "subject": subject,
            "content": content,
            "preview": f"Appointment reminder - {days} day{'s' if days > 1 else ''} to go"
        }
    
    def _create_reminder_sms_content(self, appointment: Dict, patient: Dict, reminder_type: str) -> Dict:
        """Create reminder SMS content."""
        days_map = {"first": 7, "second": 3, "third": 1}
        days = days_map.get(reminder_type, 1)
        
        message = f"HealthCare+ Reminder: Your appointment with {appointment.get('doctor_name', 'your doctor')} is in {days} day{'s' if days > 1 else ''} on {appointment.get('date')} at {appointment.get('time')}. Reply STOP to opt out."
        
        return {
            "message": message,
            "type": "reminder"
        }
    
    def _create_forms_email_content(self, appointment: Dict, patient: Dict) -> Dict:
        """Create intake forms email content."""
        subject = "Complete Your Patient Intake Forms"
        
        content = f"""
Dear {patient.get('first_name', '')} {patient.get('last_name', '')},

Thank you for scheduling your appointment with us! To help us provide you with the best care, please complete the attached patient intake forms before your visit.

📅 **Your Appointment:**
• Date: {appointment.get('date', 'N/A')}
• Time: {appointment.get('time', 'N/A')}
• Doctor: {appointment.get('doctor_name', 'N/A')}

📋 **Attached Forms:**
• Medical History Form
• Insurance Information Form
• Contact Information Update
• Consent Forms

📝 **Instructions:**
1. Please complete all forms before your appointment
2. Bring the completed forms with you or email them back
3. If you have questions, call our office

Completing these forms in advance will help reduce your wait time and ensure we have all the information needed for your visit.

Thank you for choosing HealthCare+ Medical Center!

HealthCare+ Team

--- Simulated Form Attachments ---
[Medical_History_Form.pdf]
[Insurance_Information_Form.pdf]
[Contact_Update_Form.pdf]
[Consent_Forms.pdf]
"""
        
        return {
            "subject": subject,
            "content": content,
            "preview": "Please complete your patient intake forms before your visit"
        }
    
    def _create_interactive_email_content(self, appointment: Dict, patient: Dict, reminder_type: str, questions: List[str]) -> Dict:
        """Create interactive reminder email content."""
        days_map = {"second": 3, "third": 1}
        days = days_map.get(reminder_type, 1)
        
        subject = f"Action Required - Appointment in {days} day{'s' if days > 1 else ''}"
        
        questions_html = ""
        for i, question in enumerate(questions, 1):
            questions_html += f"{i}. {question}\n"
        
        content = f"""
Dear {patient.get('first_name', '')} {patient.get('last_name', '')},

Your appointment is coming up soon! We need your help to ensure everything is ready.

📅 **Appointment Details:**
• Date: {appointment.get('date', 'N/A')}
• Time: {appointment.get('time', 'N/A')}
• Doctor: {appointment.get('doctor_name', 'N/A')}
• Appointment ID: {appointment.get('appointment_id', 'N/A')}

❓ **Please Respond to These Questions:**
{questions_html}

📞 **How to Respond:**
• Reply to this email with your answers
• Call our office at (555) 123-4567
• Use our patient portal

⚠️ **Important:**
If you need to cancel or reschedule, please do so at least 24 hours in advance to avoid any fees.

Thank you for your cooperation!

HealthCare+ Team
"""
        
        return {
            "subject": subject,
            "content": content,
            "preview": f"Action required for your appointment in {days} day{'s' if days > 1 else ''}"
        }
    
    def _simulate_email_send(self, email: str, content: Dict) -> Dict:
        """Simulate sending an email."""
        import uuid
        return {
            "email_id": str(uuid.uuid4()),
            "to": email,
            "subject": content["subject"],
            "sent_at": datetime.now().isoformat(),
            "status": "sent"
        }
    
    def _simulate_sms_send(self, phone: str, content: Dict) -> Dict:
        """Simulate sending an SMS."""
        import uuid
        return {
            "sms_id": str(uuid.uuid4()),
            "to": phone,
            "message": content["message"],
            "sent_at": datetime.now().isoformat(),
            "status": "sent"
        }
    
    def _schedule_reminder(self, appointment: Dict, patient: Dict, reminder_date: datetime, reminder_type: str):
        """Schedule a reminder (simulation)."""
        # In a real implementation, this would use a job scheduler like Celery
        logger.info(f"Reminder scheduled for {reminder_date.strftime('%Y-%m-%d')} ({reminder_type})")
        
        # For demonstration, we'll just log the scheduled reminder
        print(f"🕐 {reminder_type.title()} reminder scheduled for {reminder_date.strftime('%Y-%m-%d %H:%M')}")
    
    def _load_appointments(self) -> List[Dict]:
        """Load appointments from file."""
        filepath = os.path.join(self.data_dir, "appointments.json")
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading appointments: {e}")
        return []
    
    def _save_appointments(self, appointments: List[Dict]):
        """Save appointments to file."""
        filepath = os.path.join(self.data_dir, "appointments.json")
        try:
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            with open(filepath, 'w') as f:
                json.dump(appointments, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving appointments: {e}")


if __name__ == "__main__":
    # Test the notification manager
    print("Testing NotificationManager...")
    
    notification_mgr = NotificationManager()
    
    # Test data
    appointment = {
        "appointment_id": "APT0001",
        "date": "2025-01-15",
        "time": "10:00",
        "doctor_name": "Dr. Smith",
        "specialty": "Cardiology",
        "location": "Main Office",
        "duration_minutes": 60
    }
    
    patient = {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "+1234567890"
    }
    
    # Test confirmation email
    print("\n--- Testing Confirmation Email ---")
    result = notification_mgr.send_confirmation_email(appointment, patient)
    print(f"Result: {result}")
    
    # Test reminder SMS
    print("\n--- Testing Reminder SMS ---")
    result = notification_mgr.send_sms_reminder(appointment, patient, "first")
    print(f"Result: {result}")
    
    # Test intake forms
    print("\n--- Testing Intake Forms ---")
    result = notification_mgr.send_intake_forms(appointment, patient)
    print(f"Result: {result}")
    
    # Test interactive reminder
    print("\n--- Testing Interactive Reminder ---")
    result = notification_mgr.send_interactive_reminder(appointment, patient, "second")
    print(f"Result: {result}")
    
    print("\nNotificationManager test completed!")