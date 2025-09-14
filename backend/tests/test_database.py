import json
from datetime import date, datetime

import pytest
import requests
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.models import Patient
from src.schemas.patient import Patient as SchemaPatient


def test_create_patient(session: Session, patient_json: dict) -> None:
    """Creates a new patient and commits it to the database."""

    new_patient = Patient(
        full_name="Maria Clara",
        password="securepassword123",
        email="maria.clara@example.com",
        birthdate=datetime(1990, 5, 15),
        biological_sex="Female",
        weight=65.5,
        ancestry="Latin",
        medical_record=patient_json['medical_record']
    )
    session.add(new_patient)
    session.commit()
    session.refresh(new_patient)
    
    # Retrieving the user from posgresql
    patient_from_db = session.query(Patient).filter_by(email=new_patient.email).one()

    assert patient_from_db is not None
    assert patient_from_db.id is not None
    assert patient_from_db.full_name == "Maria Clara"
    assert patient_from_db.email == "maria.clara@example.com"
    assert patient_from_db.medical_record['conditions'][0]['condition_name'] == "Asthma"
