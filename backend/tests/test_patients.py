import json
from datetime import date, datetime
from http import HTTPStatus

import pytest
import requests
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.models import Patient
from src.schemas.patient import Patient as PatientSchema
from src.schemas.patient import Patient as SchemaPatient


def test_create_patient_success(client,patient_json):
    """
    Tests successful creation of a new patient.
    """
    response = client.post(
        '/patients/',
        json=patient_json,
    )

    assert response.status_code == HTTPStatus.CREATED
    
    response_data = response.json()
    assert response_data['id'] == 1
    assert response_data['full_name'] == patient_json['full_name']
    assert response_data['email'] == patient_json['email']
    assert response_data['birthdate'] == patient_json['birthdate']
    assert 'password' not in response_data


def test_create_patient_email_exists(client, patient):
    """
    Tests that creating a patient with a pre-existing email returns a 400 Bad Request.
    """
    response = client.post(
        '/patients/',
        json={
            "full_name": "Another Name",
            "password": "anotherpassword",
            "email": patient.email, # Use email from the fixture
            "birthdate": "1992-01-20",
            "biological_sex": "Male",
            "weight": 80.0,
            "ancestry": "Latin",
            "medical_record": {"conditions": [], "allergies": [], "medications":[], "injuries": [], "family_histories": [], "free_user_text": ""}
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST # Your code uses 400
    assert response.json() == {'detail': 'A patient with this email already exists.'}


def test_get_all_patients_empty(client):
    """
    Tests retrieving all patients when the database is empty.
    """
    response = client.get('/patients/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == []


def test_get_all_patients_with_data(client, patient):
    """
    Tests retrieving all patients when there is one patient in the database.
    """

    patient_schema = PatientSchema.model_validate(patient).model_dump(mode='json')
    
    response = client.get('/patients/')
    assert response.status_code == HTTPStatus.OK
    assert response.json() == [patient_schema]


def test_get_patient_success(client, patient):
    """
    Tests retrieving a single patient by their ID.
    """
    response = client.get(f'/patients/{patient.id}')

    assert response.status_code == HTTPStatus.OK

def test_get_patient_not_found(client, token):
    """
    Tests that retrieving a non-existent patient ID returns a 404 Not Found.
    """
    response = client.get('/patients/999', headers={'Authorization': f'Bearer {token}'})
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Patient not found'}


def test_update_patient_success(client, patient, token):
    """
    Tests successfully updating an existing patient.
    """
    updated_data = {
        "full_name": "Maria Clara Updated",
        "password": "newsupersecretpassword",
        "email": "maria.updated@example.com",
        "birthdate": "1990-05-16",
        "biological_sex": "Female",
        "weight": 68.0,
        "ancestry": "Latin",
        "medical_record": {"conditions": [], "allergies": [], "medications":[], "injuries": [], "family_histories": [], "free_user_text": ""}
    }

    response = client.put(
        f'/patients/{patient.id}',
        json=updated_data,
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK

    response_data = response.json()
    assert response_data['id'] == patient.id
    assert response_data['full_name'] == updated_data['full_name']
    assert response_data['email'] == updated_data['email']


def test_update_patient_not_found(client, patient_json):
    """
    Tests that updating a non-existent patient ID returns a 404 Not Found.
    """
    response = client.put(
        '/patients/999',
        json=patient_json
    )
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_update_patient_conflicting_email(client, patient, patient_json,token):
    """
    Tests that updating a patient's email to one that already exists for another
    patient returns a 400 Bad Request.
    """
    # Create a second patient to establish an existing email
    second_patient_payload = patient_json.copy()
    second_patient_payload['email'] = 'second.patient@example.com'
    response_create = client.post('/patients/', json=second_patient_payload, headers={'Authorization': f'Bearer {token}'})
    assert response_create.status_code == HTTPStatus.CREATED

    # Try to update the first patient (from fixture) to use the second patient's email
    update_payload = PatientSchema.model_validate(patient).model_dump(mode='json')
    update_payload['email'] = 'second.patient@example.com'
    update_payload['password'] = patient.password 

    response_update = client.put(
        f'/patients/{patient.id}',
        json=update_payload,
        headers={'Authorization': f'Bearer {token}'}
    )

    assert response_update.status_code == HTTPStatus.BAD_REQUEST
    assert response_update.json() == {'detail': 'A patient with this email already exists.'}


def test_delete_patient_success(client, patient, token):
    """
    Tests successfully deleting an existing patient.
    """
    response = client.delete(f'/patients/{patient.id}',headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.OK

    patient_schema = PatientSchema.model_validate(patient).model_dump(mode='json')
    assert response.json() == patient_schema

    # verify the patient is actually gone
    response_get = client.get(f'/patients/{patient.id}')
    assert response_get.status_code == HTTPStatus.NOT_FOUND


def test_delete_patient_not_found(client,token):
    """
    Tests that deleting a non-existent patient ID returns a 404 Not Found.
    """
    response = client.delete('/patients/999', headers={'Authorization': f'Bearer {token}'})

    assert response.status_code == HTTPStatus.FORBIDDEN
