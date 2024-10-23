from aiogram.fsm.state import StatesGroup, State


class Registration(StatesGroup):
    waiting_for_fio = State()
    waiting_for_company_id = State()


class Find(StatesGroup):
    waiting_for_fio = State()
    waiting_for_selection = State()


class EmployeeStates(StatesGroup):
    waiting_for_page = State()