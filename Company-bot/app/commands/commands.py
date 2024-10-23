from sqlalchemy import func
from sqlalchemy.orm import joinedload

from app.database.models import async_session, Employee, WorkShedule
from sqlalchemy.future import select

PAGE_SIZE = 5


async def check_user_exists(telegram_id) -> bool:
    async with async_session() as session:
        async with session.begin():
            query = select(Employee).where(Employee.telegram_id == telegram_id)
            result = await session.execute(query)
            user = result.scalars().first()
            return user is not None


async def update_employee(telegram_id, name, company_id) -> bool:
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(Employee).where(Employee.fio == name, Employee.company_id == company_id)
            )
            employee = result.scalar_one_or_none()

            if employee:
                employee.telegram_id = telegram_id
                return True
            else:
                return False


async def get_employees_page(page: int, page_size: int) -> list[Employee]:
    offset = (page - 1) * page_size
    async with async_session() as session:
        query = select(Employee).order_by(Employee.id).offset(offset).limit(page_size)
        result = await session.execute(query)
        employees = result.scalars().all()
    return employees


async def get_total_pages(page_size: int) -> int:
    async with async_session() as session:
        count_query = select(func.count()).select_from(Employee)
        count_result = await session.execute(count_query)
        total_employees = count_result.scalar()
        total_pages = (total_employees + page_size - 1) // page_size
    return total_pages


async def search_employee_by_fio(fio):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(Employee)
                .options(joinedload(Employee.department), joinedload(Employee.team))
                .where(Employee.fio == fio)
            )
            employees = result.scalars().all()
            return [
                {
                    "fio": employee.fio,
                    "working": employee.working,
                    "phone": employee.phone,
                    "mail": employee.mail,
                    "department": employee.department.name,
                    "team": employee.team.name,
                    "id": employee.id
                }
                for employee in employees
            ]


async def get_work_schedule(employee_id: int):
    async with async_session() as session:
        result = await session.execute(
            select(
                WorkShedule.Monday,
                WorkShedule.Tuesday,
                WorkShedule.Wednesday,
                WorkShedule.Thursday,
                WorkShedule.Friday,
                WorkShedule.Saturday,
                WorkShedule.Sunday,
                Employee.fio
            ).join(Employee, Employee.id == WorkShedule.employee_id).where(WorkShedule.employee_id == employee_id)
        )
        schedule = result.first()

        if schedule:
            return {
                "fio": schedule.fio,
                "Monday": schedule.Monday,
                "Tuesday": schedule.Tuesday,
                "Wednesday": schedule.Wednesday,
                "Thursday": schedule.Thursday,
                "Friday": schedule.Friday,
                "Saturday": schedule.Saturday,
                "Sunday": schedule.Sunday
            }
        return None
