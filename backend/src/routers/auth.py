from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session
from src.database import get_db
from src.models import Patient
from src.schemas.auth import Token
from src.security import create_access_token, verify_password

router = APIRouter(prefix='/auth', tags=['auth'])

OAuth2Form = Annotated[OAuth2PasswordRequestForm, Depends()]
DbSession = Annotated[Session, Depends(get_db)]

@router.post('/token', response_model=Token)
def login_for_access_token(form_data: OAuth2Form, session: DbSession):
    patient = session.scalar(select(Patient).where(Patient.email == form_data.username))

    if not patient or not verify_password(form_data.password, patient.password):
        raise HTTPException(
            status_code=HTTPStatus.UNAUTHORIZED,
            detail='Incorrect email or password',
        )

    access_token = create_access_token(data={'sub': patient.email})

    return {'access_token': access_token, 'token_type': 'bearer'}
