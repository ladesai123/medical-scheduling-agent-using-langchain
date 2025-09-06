"""
Calendar Integration Module
Simulates Calendly integration and provides calendar management functionality.
"""

import json
import os
import logging
from datetime import datetime, timedelta, date
from typing import Dict, List, Optional, Tuple
import pandas as pd

logger = logging.getLogger(__name__)


class CalendarManager:
    """Manages calendar operations and scheduling logic."""
    
    def __init__(self, data_dir: str = None):
        """Initialize calendar manager."""
        if data_dir is None:
            self.data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
        else:
            self.data_dir = data_dir
        
        self.business_hours = {
            "start": 9,  # 9 AM
            "end": 17,   # 5 PM
            "lunch_start": 12,  # 12 PM
            "lunch_end": 13     # 1 PM
        }
        
        self.working_days = [0, 1, 2, 3, 4]  # Monday to Friday
        
        logger.info("CalendarManager initialized")
    
    def get_available_slots(self, doctor_id: str, date_str: str, duration_minutes: int = 30) -> List[str]:
        """Get available time slots for a doctor on a specific date."""
        try:
            # Parse date
            target_date = datetime.strptime(date_str, "%Y-%m-%d").date()
            
            # Check if it's a working day
            if target_date.weekday() not in self.working_days:
                return []
            
            # Check if date is in the future
            if target_date <= date.today():
                return []
            
            # Load existing appointments
            appointments = self._load_appointments()
            
            # Get existing appointments for this doctor and date
            existing_appointments = [
                apt for apt in appointments
                if apt.get('doctor_id') == doctor_id and apt.get('date') == date_str
            ]
            
            # Generate all possible slots
            available_slots = []
            current_hour = self.business_hours["start"]
            
            while current_hour < self.business_hours["end"]:
                # Skip lunch hour
                if self.business_hours["lunch_start"] <= current_hour < self.business_hours["lunch_end"]:
                    current_hour += 1
                    continue
                
                time_slot = f"{current_hour:02d}:00"
                
                # Check if slot is already booked
                is_booked = any(
                    apt.get('time') == time_slot for apt in existing_appointments
                )
                
                if not is_booked:
                    available_slots.append(time_slot)
                
                # Move to next slot based on duration
                current_hour += max(1, duration_minutes // 60)
            
            return available_slots
            
        except Exception as e:
            logger.error(f"Error getting available slots: {e}")
            return []
    
    def book_slot(self, doctor_id: str, date_str: str, time_str: str, patient_data: Dict, duration_minutes: int = 30) -> Dict:
        """Book a time slot for a patient."""
        try:
            # Validate slot is available
            available_slots = self.get_available_slots(doctor_id, date_str, duration_minutes)
            
            if time_str not in available_slots:
                return {
                    "success": False,
                    "message": f"Time slot {time_str} is not available on {date_str}"
                }
            
            # Load existing data
            appointments = self._load_appointments()
            doctors = self._load_doctors()
            
            # Find doctor
            doctor = next((d for d in doctors if d.get('doctor_id') == doctor_id), None)
            if not doctor:
                return {
                    "success": False,
                    "message": f"Doctor with ID {doctor_id} not found"
                }
            
            # Create appointment
            appointment_id = f"APT{len(appointments) + 1:04d}"
            
            appointment = {
                "appointment_id": appointment_id,
                "patient_id": patient_data.get('patient_id'),
                "patient_name": patient_data.get('name', f"{patient_data.get('first_name', '')} {patient_data.get('last_name', '')}").strip(),
                "doctor_id": doctor_id,
                "doctor_name": f"Dr. {doctor['first_name']} {doctor['last_name']}",
                "specialty": doctor.get('specialty', 'General'),
                "date": date_str,
                "time": time_str,
                "duration_minutes": duration_minutes,
                "status": "scheduled",
                "type": patient_data.get('type', 'returning'),
                "created_at": datetime.now().isoformat(),
                "calendar_event_id": f"cal_event_{appointment_id}",  # Simulated Calendly ID
                "location": doctor.get('location', 'Main Office'),
                "notes": patient_data.get('notes', '')
            }
            
            # Save appointment
            appointments.append(appointment)
            self._save_appointments(appointments)
            
            # Generate calendar event (simulated)
            calendar_event = self._create_calendar_event(appointment)
            
            return {
                "success": True,
                "appointment": appointment,
                "calendar_event": calendar_event,
                "message": f"Appointment successfully booked for {date_str} at {time_str}"
            }
            
        except Exception as e:
            logger.error(f"Error booking slot: {e}")
            return {
                "success": False,
                "message": f"Error booking appointment: {e}"
            }
    
    def reschedule_appointment(self, appointment_id: str, new_date: str, new_time: str) -> Dict:
        """Reschedule an existing appointment."""
        try:
            appointments = self._load_appointments()
            
            # Find appointment
            appointment_index = None
            for i, apt in enumerate(appointments):
                if apt.get('appointment_id') == appointment_id:
                    appointment_index = i
                    break
            
            if appointment_index is None:
                return {
                    "success": False,
                    "message": f"Appointment {appointment_id} not found"
                }
            
            appointment = appointments[appointment_index]
            
            # Check if new slot is available
            available_slots = self.get_available_slots(
                appointment['doctor_id'], 
                new_date, 
                appointment.get('duration_minutes', 30)
            )
            
            if new_time not in available_slots:
                return {
                    "success": False,
                    "message": f"Time slot {new_time} is not available on {new_date}"
                }
            
            # Update appointment
            old_date = appointment['date']
            old_time = appointment['time']
            
            appointment['date'] = new_date
            appointment['time'] = new_time
            appointment['rescheduled_at'] = datetime.now().isoformat()
            appointment['status'] = 'rescheduled'
            
            appointments[appointment_index] = appointment
            self._save_appointments(appointments)
            
            return {
                "success": True,
                "appointment": appointment,
                "message": f"Appointment rescheduled from {old_date} {old_time} to {new_date} {new_time}"
            }
            
        except Exception as e:
            logger.error(f"Error rescheduling appointment: {e}")
            return {
                "success": False,
                "message": f"Error rescheduling appointment: {e}"
            }
    
    def cancel_appointment(self, appointment_id: str, reason: str = "") -> Dict:
        """Cancel an existing appointment."""
        try:
            appointments = self._load_appointments()
            
            # Find appointment
            appointment_index = None
            for i, apt in enumerate(appointments):
                if apt.get('appointment_id') == appointment_id:
                    appointment_index = i
                    break
            
            if appointment_index is None:
                return {
                    "success": False,
                    "message": f"Appointment {appointment_id} not found"
                }
            
            # Update appointment status
            appointment = appointments[appointment_index]
            appointment['status'] = 'cancelled'
            appointment['cancelled_at'] = datetime.now().isoformat()
            appointment['cancellation_reason'] = reason
            
            appointments[appointment_index] = appointment
            self._save_appointments(appointments)
            
            return {
                "success": True,
                "appointment": appointment,
                "message": f"Appointment {appointment_id} has been cancelled"
            }
            
        except Exception as e:
            logger.error(f"Error cancelling appointment: {e}")
            return {
                "success": False,
                "message": f"Error cancelling appointment: {e}"
            }
    
    def get_doctor_schedule(self, doctor_id: str, start_date: str, end_date: str) -> Dict:
        """Get doctor's schedule for a date range."""
        try:
            appointments = self._load_appointments()
            doctors = self._load_doctors()
            
            # Find doctor
            doctor = next((d for d in doctors if d.get('doctor_id') == doctor_id), None)
            if not doctor:
                return {
                    "success": False,
                    "message": f"Doctor with ID {doctor_id} not found"
                }
            
            # Filter appointments for this doctor in date range
            doctor_appointments = []
            for apt in appointments:
                if (apt.get('doctor_id') == doctor_id and 
                    start_date <= apt.get('date', '') <= end_date and
                    apt.get('status') not in ['cancelled']):
                    doctor_appointments.append(apt)
            
            # Sort by date and time
            doctor_appointments.sort(key=lambda x: (x.get('date', ''), x.get('time', '')))
            
            return {
                "success": True,
                "doctor": doctor,
                "appointments": doctor_appointments,
                "schedule": self._format_schedule(doctor_appointments, start_date, end_date)
            }
            
        except Exception as e:
            logger.error(f"Error getting doctor schedule: {e}")
            return {
                "success": False,
                "message": f"Error retrieving schedule: {e}"
            }
    
    def export_to_excel(self, start_date: str = None, end_date: str = None) -> str:
        """Export appointments to Excel file."""
        try:
            appointments = self._load_appointments()
            
            # Filter by date range if provided
            if start_date and end_date:
                appointments = [
                    apt for apt in appointments
                    if start_date <= apt.get('date', '') <= end_date
                ]
            
            # Convert to DataFrame
            df = pd.DataFrame(appointments)
            
            # Create export filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"appointments_export_{timestamp}.xlsx"
            filepath = os.path.join(self.data_dir, filename)
            
            # Export to Excel
            df.to_excel(filepath, index=False, sheet_name='Appointments')
            
            logger.info(f"Appointments exported to {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"Error exporting to Excel: {e}")
            return ""
    
    def _create_calendar_event(self, appointment: Dict) -> Dict:
        """Create a simulated calendar event (like Calendly integration)."""
        return {
            "event_id": appointment.get('calendar_event_id'),
            "title": f"Medical Appointment - {appointment.get('patient_name')}",
            "description": f"Appointment with {appointment.get('doctor_name')} ({appointment.get('specialty')})",
            "start_time": f"{appointment.get('date')}T{appointment.get('time')}:00",
            "duration_minutes": appointment.get('duration_minutes', 30),
            "location": appointment.get('location', 'Main Office'),
            "attendees": [
                appointment.get('patient_name'),
                appointment.get('doctor_name')
            ],
            "status": "confirmed",
            "created_at": appointment.get('created_at')
        }
    
    def _format_schedule(self, appointments: List[Dict], start_date: str, end_date: str) -> str:
        """Format schedule for display."""
        if not appointments:
            return f"No appointments scheduled from {start_date} to {end_date}"
        
        schedule_lines = [f"Schedule from {start_date} to {end_date}:\n"]
        
        current_date = None
        for apt in appointments:
            apt_date = apt.get('date', '')
            if apt_date != current_date:
                current_date = apt_date
                schedule_lines.append(f"\n📅 {apt_date}:")
            
            schedule_lines.append(
                f"  • {apt.get('time', '')} - {apt.get('patient_name', '')} "
                f"({apt.get('duration_minutes', 30)} min) [{apt.get('status', '')}]"
            )
        
        return "\n".join(schedule_lines)
    
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
            logger.info("Appointments saved successfully")
        except Exception as e:
            logger.error(f"Error saving appointments: {e}")
    
    def _load_doctors(self) -> List[Dict]:
        """Load doctors from file."""
        filepath = os.path.join(self.data_dir, "doctors.json")
        try:
            if os.path.exists(filepath):
                with open(filepath, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading doctors: {e}")
        return []


if __name__ == "__main__":
    # Test the calendar manager
    print("Testing CalendarManager...")
    
    calendar_mgr = CalendarManager()
    
    # Test getting available slots
    doctor_id = "DOC001"
    test_date = (date.today() + timedelta(days=7)).strftime("%Y-%m-%d")
    
    print(f"Available slots for doctor {doctor_id} on {test_date}:")
    slots = calendar_mgr.get_available_slots(doctor_id, test_date)
    print(slots)
    
    # Test booking
    if slots:
        patient_data = {
            "patient_id": "P0001",
            "name": "Test Patient",
            "type": "new"
        }
        
        result = calendar_mgr.book_slot(doctor_id, test_date, slots[0], patient_data, 60)
        print(f"Booking result: {result}")
    
    print("CalendarManager test completed!")