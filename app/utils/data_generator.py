"""
Data generator for creating synthetic patients and doctors
"""
import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any


def generate_patient(patient_id: str) -> Dict[str, Any]:
    """Generate a synthetic patient record."""
    first_names = [
        "John", "Jane", "Michael", "Sarah", "David", "Emily", "Robert", "Lisa",
        "William", "Jessica", "James", "Amanda", "Christopher", "Ashley", "Daniel",
        "Stephanie", "Matthew", "Melissa", "Anthony", "Nicole", "Mark", "Kimberly",
        "Donald", "Donna", "Steven", "Carol", "Paul", "Ruth", "Andrew", "Sharon"
    ]
    
    last_names = [
        "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
        "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
        "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
        "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson"
    ]
    
    insurance_providers = [
        "Blue Cross Blue Shield", "Aetna", "Cigna", "United Healthcare", "Kaiser Permanente",
        "Humana", "Anthem", "Medicaid", "Medicare", "TRICARE"
    ]
    
    # Generate basic info
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    
    # Generate date of birth (18-80 years old)
    today = datetime.now()
    min_age = today - timedelta(days=80*365)
    max_age = today - timedelta(days=18*365)
    random_days = random.randint(0, (max_age - min_age).days)
    dob = min_age + timedelta(days=random_days)
    
    patient = {
        "patient_id": patient_id,
        "first_name": first_name,
        "last_name": last_name,
        "date_of_birth": dob.strftime("%Y-%m-%d"),
        "phone": f"({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}",
        "email": f"{first_name.lower()}.{last_name.lower()}@email.com",
        "address": {
            "street": f"{random.randint(100, 9999)} {random.choice(['Main', 'Oak', 'Pine', 'Elm', 'Maple'])} {random.choice(['St', 'Ave', 'Dr', 'Ln'])}",
            "city": random.choice(["New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego", "Dallas", "San Jose"]),
            "state": random.choice(["NY", "CA", "IL", "TX", "AZ", "PA", "TX", "CA", "TX", "CA"]),
            "zip_code": f"{random.randint(10000, 99999)}"
        },
        "insurance": {
            "provider": random.choice(insurance_providers),
            "policy_number": f"POL{random.randint(100000, 999999)}",
            "group_number": f"GRP{random.randint(1000, 9999)}"
        },
        "medical_history": [],
        "emergency_contact": {
            "name": f"{random.choice(first_names)} {random.choice(last_names)}",
            "relationship": random.choice(["Spouse", "Parent", "Child", "Sibling", "Friend"]),
            "phone": f"({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}"
        },
        "is_new_patient": random.choice([True, False])
    }
    
    return patient


def generate_doctor(doctor_id: str) -> Dict[str, Any]:
    """Generate a synthetic doctor record."""
    first_names = [
        "Alexander", "Benjamin", "Catherine", "Diana", "Edward", "Fiona", "Gregory",
        "Helena", "Isaac", "Julia", "Kenneth", "Laura", "Marcus", "Nina", "Oliver"
    ]
    
    last_names = [
        "Adams", "Baker", "Clark", "Davis", "Evans", "Foster", "Green", "Harris",
        "Jackson", "King", "Lewis", "Mitchell", "Nelson", "Parker", "Roberts"
    ]
    
    specialties = [
        "Family Medicine", "Internal Medicine", "Pediatrics", "Cardiology",
        "Dermatology", "Orthopedics", "Neurology", "Psychiatry", "Radiology",
        "Emergency Medicine", "Anesthesiology", "Pathology"
    ]
    
    first_name = random.choice(first_names)
    last_name = random.choice(last_names)
    specialty = random.choice(specialties)
    
    # Generate weekly schedule
    schedule = {}
    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
    
    for day in days:
        # Some doctors work different hours
        if random.random() > 0.2:  # 80% chance of working this day
            start_hour = random.choice([8, 9, 10])
            end_hour = random.choice([16, 17, 18])
            schedule[day] = {
                "start_time": f"{start_hour:02d}:00",
                "end_time": f"{end_hour:02d}:00",
                "lunch_break": f"{12}:00-{13}:00"
            }
    
    doctor = {
        "doctor_id": doctor_id,
        "first_name": first_name,
        "last_name": last_name,
        "specialty": specialty,
        "phone": f"({random.randint(200, 999)}) {random.randint(200, 999)}-{random.randint(1000, 9999)}",
        "email": f"dr.{first_name.lower()}.{last_name.lower()}@clinic.com",
        "schedule": schedule,
        "appointment_duration": {
            "new_patient": 60,  # minutes
            "returning_patient": 30  # minutes
        }
    }
    
    return doctor


if __name__ == "__main__":
    # Test the generators
    patient = generate_patient("P0001")
    doctor = generate_doctor("D001")
    
    print("Sample Patient:")
    print(json.dumps(patient, indent=2))
    print("\nSample Doctor:")
    print(json.dumps(doctor, indent=2))