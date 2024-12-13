# models
from sqlalchemy import String, BIGINT, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
import datetime
from typing import Annotated

intpk = Annotated[int, mapped_column(primary_key=True)]
str_256 = Annotated[str, mapped_column(String(256))]
bigint = Annotated[int, mapped_column(BIGINT)]


class Base(DeclarativeBase):
    type_annotation_map = {
        str_256: String(256),
        bigint: BIGINT,
    }

    repr_cols_num = 6
    repr_cols = tuple()

    def __repr__(self):
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col, None)}")
        return f"<{self.__class__.__name__} {', '.join(cols)}>"


class ProdEmployeesRegistry(Base):
    __tablename__ = 'prod_employees_registry'

    id: Mapped[intpk]
    fio: Mapped[str_256]
    phone_number: Mapped[bigint | None]
    birthdate: Mapped[datetime.date | None]
    employment_date: Mapped[datetime.date | None]
    telegram_id: Mapped[bigint] = mapped_column(default=0, nullable=True)
    telegram_username: Mapped[str_256 | None]
    whatsapp_id: Mapped[str_256 | None]
    whatsapp_username: Mapped[str_256 | None]
    trello_id: Mapped[str_256 | None]
    trello_token: Mapped[str_256 | None]
    owamos_login: Mapped[str_256 | None]
    owamos_pass: Mapped[str_256 | None]
    mail: Mapped[str_256 | None]
    management: Mapped[str_256 | None]
    residence: Mapped[str_256 | None]
    is_moscow: Mapped[bool | None] = mapped_column(default=False)
    is_office: Mapped[bool | None] = mapped_column(default=False)
    is_deleted: Mapped[bool | None] = mapped_column(default=False)

    vacations = relationship("ProdVacation", back_populates="employee", cascade="all, delete-orphan")


class ProdVacation(Base):
    __tablename__ = 'prod_vacation'

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey('prod_employees_registry.id'))
    date_start: Mapped[datetime.date]
    date_end: Mapped[datetime.date]
    is_deleted: Mapped[bool | None] = mapped_column(default=False)

    employee = relationship("ProdEmployeesRegistry", back_populates="vacations")


class Departments(Base):
    __tablename__ = 'departments'

    id: Mapped[intpk]
    department_name: Mapped[str_256]
    department_key: Mapped[str_256]


class ProdEmployeeDepartment(Base):
    __tablename__ = 'prod_employee_department'

    id: Mapped[intpk]
    user_id: Mapped[int] = mapped_column(ForeignKey('prod_employees_registry.id'))
    department_id: Mapped[int] = mapped_column(ForeignKey('departments.id'))
    is_deleted: Mapped[bool | None] = mapped_column(default=False)