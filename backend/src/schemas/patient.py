from datetime import date
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, EmailStr, Field


class BiologicalSexEnum(str, Enum):
    male = 'Male'
    female = 'Female'

class AncestryEnum(str, Enum):
    white = 'White'
    black = 'Black'
    latin = 'Latin'
    asian = 'Asian'
    multiracial = 'Multiracial'

# --- Nested Schemas for the Medical Record ---
class Condition(BaseModel):
    condition_name: str
    diagnosis_date: date
    condition_status: str

class Allergy(BaseModel):
    substance: str
    reaction_type: str
    discovery_date: date

class Medication(BaseModel):
    medication_name: str
    dosage: str
    frequency: str
    treatment_start_date: date

class Injury(BaseModel):
    injury_description: str
    type: str
    occurrence_date: date
    severity: str

class FamilyHistory(BaseModel):
    relationship_to_patient: str
    medical_condition: str

class MedicalRecordSchema(BaseModel):
    conditions: List[Condition]
    allergies: List[Allergy]
    medications: List[Medication]
    injuries: List[Injury]
    family_histories: List[FamilyHistory]
    free_user_text: str

# --- Main Patient Schemas ---
class PatientBase(BaseModel):
    full_name: str = Field(..., min_length=2, description="Patient's full name")
    email: EmailStr
    birthdate: date
    biological_sex: BiologicalSexEnum
    weight: float = Field(..., gt=0, description="Patient's weight in kilograms")
    ancestry: AncestryEnum
    medical_record: MedicalRecordSchema

class PatientCreate(PatientBase):
    password: str = Field(..., min_length=8, description="Patient's password (min 8 characters)")

class Patient(PatientBase):
    id: int
    model_config = {
        "from_attributes": True
    }
