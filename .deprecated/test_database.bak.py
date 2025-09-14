from datetime import date, datetime

import pytest
from sqlalchemy import select
from sqlalchemy.orm import Session
# Import all your models
from src.models import (Allergy, FamilyHistory, InjuryHistory,
                        MedicalCondition, Patient, PrescribedMedication)


@pytest.fixture
def patient(session: Session) -> Patient:
    """Creates a new patient and commits it to the database."""
    new_patient = Patient(
        full_name="Maria Clara",
        password="securepassword123",
        email="maria.clara@example.com",
        birthdate=datetime(1990, 5, 15),
        biological_sex="Female",
        weight=65.5,
        ancestry="Latin"
    )
    session.add(new_patient)
    session.commit()
    # Refresh to get database-generated values like ID
    session.refresh(new_patient)
    return new_patient

# --- Tests for Each Model ---

def test_create_patient(patient: Patient):
    """Tests that the patient fixture works correctly."""
    assert patient.id is not None
    assert patient.full_name == "Maria Clara"
    assert patient.ancestry == "Latin"

def test_create_medical_condition(session: Session, patient: Patient):
    """Tests creating a MedicalCondition linked to a patient."""
    new_condition = MedicalCondition(
        patient_id=patient.id,
        condition_name="Hypertension",
        diagnosis_date=date(2022, 1, 10),
        condition_status="Active",
        patient=patient # Setting the relationship
    )
    session.add(new_condition)
    session.commit()

    # Verify it was created
    fetched_condition = session.get(MedicalCondition, new_condition.id)
    assert fetched_condition is not None
    assert fetched_condition.condition_name == "Hypertension"
    assert fetched_condition.patient_id == patient.id

def test_create_allergy(session: Session, patient: Patient):
    """Tests creating an Allergy linked to a patient."""
    new_allergy = Allergy(
        patient_id=patient.id,
        substance="Peanuts",
        reaction_type="Anaphylaxis",
        discovery_date=date(2005, 6, 1),
        patient=patient
    )
    session.add(new_allergy)
    session.commit()

    fetched_allergy = session.get(Allergy, new_allergy.id)
    assert fetched_allergy is not None
    assert fetched_allergy.substance == "Peanuts"
    assert fetched_allergy.patient_id == patient.id


def test_create_prescribed_medication(session: Session, patient: Patient):
    """Tests creating a PrescribedMedication linked to a patient."""
    new_medication = PrescribedMedication(
        patient_id=patient.id,
        medication_name="Lisinopril",
        dosage="10mg",
        frequency="Once a day",
        treatment_start_date=date(2022, 1, 15),
        patient=patient
    )
    session.add(new_medication)
    session.commit()

    fetched_med = session.get(PrescribedMedication, new_medication.id)
    assert fetched_med is not None
    assert fetched_med.medication_name == "Lisinopril"
    assert fetched_med.patient_id == patient.id


def test_create_injury_history(session: Session, patient: Patient):
    """Tests creating an InjuryHistory linked to a patient."""
    new_injury = InjuryHistory(
        patient_id=patient.id,
        injury_description="Left tibia fracture",
        type="Fracture",
        occurrence_date=date(2018, 12, 25),
        severity="High",
        patient=patient
    )
    session.add(new_injury)
    session.commit()

    fetched_injury = session.get(InjuryHistory, new_injury.id)
    assert fetched_injury is not None
    assert fetched_injury.type == "Fracture"
    assert fetched_injury.patient_id == patient.id


def test_create_family_history(session: Session, patient: Patient):
    """Tests creating a FamilyHistory linked to a patient."""
    new_history = FamilyHistory(
        patient_id=patient.id,
        relationship_to_patient="Mother",
        medical_condition="Type 2 Diabetes",
        patient=patient
    )
    session.add(new_history)
    session.commit()

    fetched_history = session.get(FamilyHistory, new_history.id)
    assert fetched_history is not None
    assert fetched_history.medical_condition == "Type 2 Diabetes"
    assert fetched_history.patient_id == patient.id
