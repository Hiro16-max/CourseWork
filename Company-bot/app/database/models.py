from sqlalchemy import BigInteger, String, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine, AsyncSession
from config import DB

engine = create_async_engine(url=DB)
async_session = async_sessionmaker(engine)


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Department(Base):
    __tablename__ = 'departments'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    employees = relationship("Employee", back_populates="department")


class Team(Base):
    __tablename__ = 'teams'

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    employees = relationship("Employee", back_populates="team")


class Employee(Base):
    __tablename__ = 'employees'

    id: Mapped[int] = mapped_column(primary_key=True)
    mail: Mapped[str] = mapped_column(String(120))
    fio: Mapped[str] = mapped_column(String(120))
    phone: Mapped[str] = mapped_column(String(120))
    company_id: Mapped[int] = mapped_column()
    department_id: Mapped[int] = mapped_column(ForeignKey('departments.id'))
    team_id: Mapped[int] = mapped_column(ForeignKey('teams.id'))
    telegram_id: Mapped[int] = mapped_column(BigInteger, nullable=True)
    working: Mapped[bool] = mapped_column(Boolean, default=False)

    department = relationship("Department", back_populates="employees")
    team = relationship("Team", back_populates="employees")

    __table_args__ = (UniqueConstraint('fio', 'company_id', name='uq_fio_company_id'),)


class WorkShedule(Base):
    __tablename__ = 'work_shedules'

    id: Mapped[int] = mapped_column(primary_key=True)
    employee_id: Mapped[int] = mapped_column(ForeignKey('employees.id'))
    Monday: Mapped[str] = mapped_column(String(10))
    Tuesday: Mapped[str] = mapped_column(String(10))
    Wednesday: Mapped[str] = mapped_column(String(10))
    Thursday: Mapped[str] = mapped_column(String(10))
    Friday: Mapped[str] = mapped_column(String(10))
    Saturday: Mapped[str] = mapped_column(String(10))
    Sunday: Mapped[str] = mapped_column(String(10))

    employee = relationship("Employee", foreign_keys=[employee_id])


async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
