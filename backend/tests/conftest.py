import os
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from sqlalchemy_utils import create_database, database_exists
from src.database import get_db
from src.main import app
from src.models import Patient, table_registry
from src.security import get_password_hash

db_user = os.environ.get('POSTGRES_USER', 'postgres')
db_password = os.environ.get('POSTGRES_PASSWORD', 'changeme')
db_host = os.environ.get('DB_HOST', 'postgres')
db_port = os.environ.get('DB_PORT', '5432')
db_name = 'medical_analysis_tests'

DATABASE_URL = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"

engine = create_engine(DATABASE_URL,poolclass=StaticPool)

if not database_exists(engine.url):
    create_database(engine.url)
    print(f"Database '{db_name}' created successfully.")
    table_registry.metadata.create_all(engine)
    print("Tables created successfully")

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture
def session():
    table_registry.metadata.create_all(engine) # create all the tables for the test
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

    table_registry.metadata.drop_all(engine) # drop all the tables for the test

# creates the fastapi routes session fixture
@pytest.fixture
def client(session):
    def get_session_override():
        return session

    with TestClient(app) as client:
        app.dependency_overrides[get_db] = get_session_override
        yield client

    app.dependency_overrides.clear()

# default json to test create patients
@pytest.fixture
def patient_json():
    patient_json = {
    "full_name": "Maria Oliveira da Silva",
    "password": "securePassword123!",
    "email": "maria.silva@example.com",
    "birthdate": "1988-07-22",
    "biological_sex": "Female",
    "weight": 72.5,
    "ancestry": "Latin",
    "medical_record": {
    "conditions":
        [
        {
            "condition_name": "Asthma",
            "diagnosis_date": "2005-09-15",
            "condition_status": "Active"
        },
        {
            "condition_name": "Type 2 Diabetes",
            "diagnosis_date": "2023-01-30",
            "condition_status": "Monitored"
        }
        ],
    "allergies": [
        {
        "substance": "Penicillin",
        "reaction_type": "Hives and skin rash",
        "discovery_date": "1995-03-12"
        }
    ],
    "medications": [
        {
        "medication_name": "Metformin",
        "dosage": "500mg",
        "frequency": "Twice daily with meals",
        "treatment_start_date": "2023-02-01"
        },
        {
        "medication_name": "Albuterol Inhaler",
        "dosage": "90mcg/actuation",
        "frequency": "As needed for shortness of breath",
        "treatment_start_date": "2005-09-15"
        }
    ],
    "injuries": [
        {
        "injury_description": "Right ankle sprain",
        "type": "Sprain",
        "occurrence_date": "2019-11-05",
        "severity": "Moderate"
        }
    ],
    "family_histories": [
        {
        "relationship_to_patient": "Mother",
        "medical_condition": "Hypertension"
        },
        {
        "relationship_to_patient": "Father",
        "medical_condition": "Type 2 Diabetes"
        }
    ],
    "free_user_text":  ""
    }
    }

    return patient_json 

@pytest.fixture
def patient(session, patient_json):

    new_patient = Patient(
        full_name="Maria Clara",
        password= get_password_hash("securepassword123"),
        email="maria.clara10@example.com",
        birthdate=datetime(1990, 5, 15),
        biological_sex="Female",
        weight=65.5,
        ancestry="Latin",
        medical_record=patient_json["medical_record"]
    )
    new_patient.clean_password = "securepassword123"

    session.add(new_patient)
    session.commit()
    session.refresh(new_patient)
    return new_patient 

@pytest.fixture
def token(client, patient):
    response = client.post(
        '/auth/token',
        data={'username': patient.email, 'password': patient.clean_password},
    )
    return response.json()['access_token']
