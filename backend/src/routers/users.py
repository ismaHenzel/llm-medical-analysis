from http import HTTPStatus
from typing import Annotated, List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.database import get_db
from src.models import Patient
from src.schemas.patient import Patient as PatientSchema
from src.schemas.patient import PatientCreate as PatientCreateSchema
from src.security import get_current_user, get_password_hash

router = APIRouter()

DbSession = Annotated[Session, Depends(get_db)] # inherits database session
CurrentPatient = Annotated[Patient, Depends(get_current_user)] # Verify if the user is logged in

@router.post("/patients/", response_model=PatientSchema, status_code=201)
def create_patient(patient_data: PatientCreateSchema, db: DbSession):
    """
    Create a new patient record, including their associated medical history.
    """

    email_already_exists = db.scalar(
        select(Patient)
            .where(Patient.email == patient_data.email)
    )

    if email_already_exists :
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="A patient with this email already exists."
        )

    # Create the main Patient object
    new_patient = Patient(
        full_name=patient_data.full_name,
        password=get_password_hash(patient_data.password), # encrypt password
        email=patient_data.email,
        birthdate=patient_data.birthdate,
        biological_sex=patient_data.biological_sex,
        weight=patient_data.weight,
        ancestry=patient_data.ancestry,
        medical_record=patient_data.medical_record.model_dump(mode='json')
    )

    try:
        db.add(new_patient)
        db.commit()
        db.refresh(new_patient)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while creating the patient: {e}"
        )

    return new_patient

@router.get("/patients/me", response_model=PatientSchema, status_code=200)
def get_users_me(current_patient: CurrentPatient):
    """
    Route to validate User token and respond Patient data.

    Fetch the patient data for the currently authenticated user.
    The `CurrentPatient` dependency handles all the token validation.
    """
    return current_patient

@router.get("/patients/", response_model=List[PatientSchema], status_code=200)
def get_all_patients(db: DbSession, skip: int = 0, limit: int = 100):
    """
    Retrieve a list of all patients with pagination.
    """
    patients = db.scalars(
        select(Patient).offset(skip).limit(limit)
    ).all()
    return patients

@router.get("/patients/{patient_id}", response_model=Patient, status_code=200)
def get_patient(patient_id: int, db: DbSession):
    """
    Retrieve a single patient by their ID.
    """
    patient = db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Patient not found")
        
    return patient


@router.put("/patients/{patient_id}", response_model=PatientSchema, status_code=200)
def update_patient(
        patient_id: int, 
        patient_data: PatientCreateSchema, 
        db: DbSession,
        current_patient: CurrentPatient
):
    """
    Update an existing patient's record by their ID.
    """

    # Verify if the user that is trying to update is the correct user
    if current_patient.id != patient_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="Not enough permissions"
        )

    patient = db.scalar(
        select(Patient).where(Patient.id == patient_id)
    )

    if not patient:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Patient not found")

    if patient_data.email != patient.email:
        email_already_exists = db.scalar(
            select(Patient).where(Patient.email == patient_data.email)
        )
        if email_already_exists:
            raise HTTPException(
                status_code=400,
                detail="A patient with this email already exists."
            )

    # Update all fields from the input data
    patient.full_name = patient_data.full_name
    patient.password = patient_data.password
    patient.email = patient_data.email
    patient.birthdate = patient_data.birthdate
    patient.biological_sex = patient_data.biological_sex
    patient.weight = patient_data.weight
    patient.ancestry = patient_data.ancestry
    patient.medical_record = patient_data.medical_record.model_dump(mode='json')

    try:
        db.commit()
        db.refresh(patient)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while updating the patient: {e}"
        )
    return patient

@router.delete("/patients/{patient_id}", response_model=PatientSchema, status_code=200)
def delete_patient(patient_id: int, db: DbSession, current_patient: CurrentPatient):
    """
    Delete a patient record by their ID.
    """

    # Verify if the user that is trying to delete is the correct user
    if current_patient.id != patient_id:
        raise HTTPException(
            status_code=HTTPStatus.FORBIDDEN, detail="Not enough permissions"
        )

    patient = db.get(Patient, patient_id)
    if not patient:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail="Patient not found")

    try:
        db.delete(patient)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while deleting the patient: {e}"
        )

    # Return the deleted object as confirmation
    return patient
