import uuid
from datetime import date, datetime
from enum import Enum
from typing import List, Optional

from sqlalchemy import (CheckConstraint, Date, DateTime, ForeignKey, Integer,
                        String, Text, func)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, registry, relationship

table_registry = registry()

@table_registry.mapped_as_dataclass
class Patient:
    __tablename__ = 'patients'
    __table_args__ = (
        CheckConstraint(
            "biological_sex IN ('Male', 'Female')",
            name="biological_sex_field_check"
        ),
        CheckConstraint(
                "ancestry IN ('White', 'Black', 'Latin','Asian','Multiracial')",
                name="ancestry_sex_field_check"
            ),
    )

    id: Mapped[uuid.UUID] = mapped_column(init=False, primary_key=True,insert_default=uuid.uuid4)
    full_name: Mapped[str]
    password: Mapped[str]
    email: Mapped[str]
    birthdate: Mapped[datetime]
    biological_sex: Mapped[str]
    weight: Mapped[float]
    ancestry: Mapped[str]
    creation_date: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )

    # Relationships back to the other models
    conditions: Mapped[List['MedicalCondition']] = relationship(
        back_populates='patient', cascade='all, delete-orphan',init=False, default_factory=list
    )
    allergies: Mapped[List['Allergy']] = relationship(
        back_populates='patient', cascade='all, delete-orphan',init=False, default_factory=list
    )
    medications: Mapped[List['PrescribedMedication']] = relationship(
        back_populates='patient', cascade='all, delete-orphan',init=False, default_factory=list
    )
    injuries: Mapped[List['InjuryHistory']] = relationship(
        back_populates='patient', cascade='all, delete-orphan',init=False, default_factory=list
    )
    family_histories: Mapped[List['FamilyHistory']] = relationship(
        back_populates='patient', cascade='all, delete-orphan',init=False, default_factory=list
    )

@table_registry.mapped_as_dataclass
class MedicalCondition:
    __tablename__ = 'medical_conditions'

    # Relationships
    patient: Mapped['Patient'] = relationship(back_populates='conditions')

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), init=False, primary_key=True, insert_default=uuid.uuid4
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('patients.id'))
    condition_name: Mapped[str] = mapped_column(String(255))
    diagnosis_date: Mapped[date] = mapped_column(Date)
    condition_status: Mapped[str] = mapped_column(String(50), default='Active')
    creation_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), init=False, server_default=func.now()
    )

@table_registry.mapped_as_dataclass
class Allergy:
    __tablename__ = 'allergies'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), init=False, primary_key=True, insert_default=uuid.uuid4
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('patients.id'))
    substance: Mapped[str] = mapped_column(String(255))
    reaction_type: Mapped[Optional[str]] = mapped_column(Text)
    discovery_date: Mapped[Optional[date]] = mapped_column(Date)
    creation_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), init=False, server_default=func.now()
    )

    # Relationship
    patient: Mapped['Patient'] = relationship(back_populates='allergies')


@table_registry.mapped_as_dataclass
class PrescribedMedication:
    __tablename__ = 'prescribed_medications'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), init=False, primary_key=True, insert_default=uuid.uuid4
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('patients.id'))
    medication_name: Mapped[str] = mapped_column(String(255))
    dosage: Mapped[Optional[str]] = mapped_column(String(100))
    frequency: Mapped[Optional[str]] = mapped_column(String(100))
    treatment_start_date: Mapped[date] = mapped_column(Date)
    creation_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), init=False, server_default=func.now()
    )

    # Relationships
    patient: Mapped['Patient'] = relationship(back_populates='medications')

@table_registry.mapped_as_dataclass
class InjuryHistory:
    __tablename__ = 'injury_histories'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), init=False, primary_key=True, insert_default=uuid.uuid4
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('patients.id'))
    injury_description: Mapped[str] = mapped_column(String(255))
    type: Mapped[str] = mapped_column(String(50)) # e.g., 'Fracture', 'Surgery'
    occurrence_date: Mapped[date] = mapped_column(Date)
    severity: Mapped[Optional[str]] = mapped_column(String(50))
    creation_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), init=False, server_default=func.now()
    )

    # Relationship
    patient: Mapped['Patient'] = relationship(back_populates='injuries')


@table_registry.mapped_as_dataclass
class FamilyHistory:
    __tablename__ = 'family_histories'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), init=False, primary_key=True, insert_default=uuid.uuid4
    )
    patient_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('patients.id'))
    relationship_to_patient: Mapped[str] = mapped_column(String(100))
    medical_condition: Mapped[str] = mapped_column(String(255))
    creation_date: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), init=False, server_default=func.now()
    )

    # Relationship
    patient: Mapped['Patient'] = relationship(back_populates='family_histories')
