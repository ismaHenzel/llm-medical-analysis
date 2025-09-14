from datetime import date, datetime
from typing import List, Optional

from sqlalchemy import CheckConstraint, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, registry

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
    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    full_name: Mapped[str]
    password: Mapped[str]
    email: Mapped[str]
    birthdate: Mapped[datetime]
    biological_sex: Mapped[str]
    weight: Mapped[float]
    ancestry: Mapped[str]
    medical_record: Mapped[dict] = mapped_column(JSONB)
    creation_date: Mapped[datetime] = mapped_column(
        init=False, server_default=func.now()
    )
