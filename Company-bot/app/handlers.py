from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery
from aiogram.fsm.context import FSMContext

from app.keyboards.keyboards import get_registration_keyboard, get_menu_keyboard, create_pagination_buttons, get_workshedule_keyboard
from app.commands.commands import check_user_exists, update_employee, get_employees_page, get_total_pages, \
    search_employee_by_fio, get_work_schedule
from app.states import Registration, Find

PAGE_SIZE = 5
router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    user_exists = await check_user_exists(message.from_user.id)
    if user_exists:
        await message.answer("Вот список доступных команд...", reply_markup=get_menu_keyboard())
    else:
        keyboard = get_registration_keyboard()
        await message.answer("Вы не зарегистрированы в системе. Желаете зарегистророваться?",
                             reply_markup=keyboard)


@router.callback_query(lambda c: c.data.startswith('register_'))
async def handle_registration_callback(query: CallbackQuery, state: FSMContext):
    callback_data = query.data
    if callback_data == "register_yes":
        await query.message.answer("Для начала регистрации, пожалуйста, укажите ваше полное ФИО.",
                                   reply_markup=ReplyKeyboardRemove())
        await state.set_state(Registration.waiting_for_fio)
    elif callback_data == "register_no":
        await query.message.answer("Регистрация отменена.", reply_markup=ReplyKeyboardRemove())

    await query.message.edit_reply_markup()


@router.message(Registration.waiting_for_fio)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer("Теперь укажите ваш id внутри компании.")
    await state.set_state(Registration.waiting_for_company_id)


@router.message(Registration.waiting_for_company_id)
async def process_company_id(message: Message, state: FSMContext):
    await state.update_data(company_id=message.text)

    data = await state.get_data()
    name, company_id = data.get('name'), data.get('company_id')

    if await update_employee(message.from_user.id, name, company_id):
        await message.answer(f"Спасибо за регистрацию, {name}! Ваши данные сохранены.",
                             reply_markup=get_menu_keyboard())
        await state.clear()
    else:
        await message.answer(f"Такого сотрудника не существует, попробуйте зарегистрироваться еще раз")
        await state.clear()
        await handle_registration_callback("register_yes", state)


@router.message(lambda message: message.text == "Список сотрудников")
async def show_employees(message: Message, state: FSMContext):
    if not await check_user_exists(message.from_user.id):
        keyboard = get_registration_keyboard()
        await message.answer("У вас нет доступа к этой команде, пройдите регистрацию", reply_markup=keyboard)
        await handle_registration_callback("register_yes", state)
        return
    page = 1
    employees = await get_employees_page(page, PAGE_SIZE)
    total_pages = await get_total_pages(PAGE_SIZE)

    employees_text = format_employees(employees)
    keyboard = create_pagination_buttons(page, total_pages)

    await message.answer(
        text=f"Список сотрудников:\n{employees_text}\n\nСтраница {page} из {total_pages}",
        reply_markup=keyboard
    )


@router.callback_query(lambda c: c.data.startswith('page_'))
async def handle_page_navigation(callback_query: CallbackQuery):
    page = int(callback_query.data.split("_")[1])

    employees = await get_employees_page(page, PAGE_SIZE)
    total_pages = await get_total_pages(PAGE_SIZE)
    employees_text = format_employees(employees)

    keyboard = create_pagination_buttons(page, total_pages)

    await callback_query.message.edit_text(
        text=f"Список сотрудников:\n{employees_text}\n\nСтраница {page} из {total_pages}",
        reply_markup=keyboard
    )



def format_employees(employees):
    return "\n".join([f"{emp.fio} - {'работает' if emp.working else 'не работает'}" for emp in
                      employees]) or "Нет сотрудников для отображения."


@router.message(lambda message: message.text == "Поиск по ФИО")
async def search_employee(message: Message, state: FSMContext):
    await message.answer("Пожалуйста, введите ФИО сотрудника для поиска:")
    await state.set_state(Find.waiting_for_fio)


@router.message(Find.waiting_for_fio)
async def process_search_query(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    data = await state.get_data()
    name = data.get('name')

    employees = await search_employee_by_fio(name)

    if len(employees) == 1:
        employee = employees[0]
        response_message = (
            f"Сотрудник: {employee['fio']}\n"
            f"Телефон: {employee['phone']}\n"
            f"Почта: {employee['mail']}\n"
            f"Работает: {'Да' if employee['working'] else 'Нет'}"
        )
        await message.answer(response_message, reply_markup=get_workshedule_keyboard(employee['id']))
        await state.clear()
    elif len(employees) > 1:
        response_message = "Найдено несколько сотрудников. Введите номер нужного:\n\n"
        for i, employee in enumerate(employees, start=1):
            response_message += (
                f"🔢 {i}. \n"
                f"👤 ФИО: {employee['fio']}\n"
                f"🏢 Отдел: {employee['department']}\n"
                f"👥 Команда: {employee['team']}\n"
                f"{'-' * 30}\n"
            )

        await message.answer(response_message)
        await state.set_state(Find.waiting_for_selection)
    else:
        await message.answer("Сотрудник с таким ФИО не найден.", reply_markup=get_menu_keyboard())
        await state.clear()


@router.message(Find.waiting_for_selection)
async def process_employee_selection(message: Message, state: FSMContext):
    try:
        index = int(message.text) - 1
    except ValueError:
        await message.answer("Пожалуйста, введите корректный номер.")
        return

    data = await state.get_data()
    name = data.get('name')
    employees = await search_employee_by_fio(name)

    if 0 <= index < len(employees):
        employee = employees[index]
        response_message = (
            f"Сотрудник: {employee['fio']}\n"
            f"Телефон: {employee['phone']}\n"
            f"Почта: {employee['mail']}\n"
            f"Работает: {'Да' if employee['working'] else 'Нет'}"
        )
        await message.answer(response_message, reply_markup=get_workshedule_keyboard(employee['id']))
    else:
        await message.answer("Неправильный номер. Попробуйте еще раз.")
        return state.set_state(Find.waiting_for_selection)

    await state.clear()


@router.message(lambda message: message.text == "Получить рабочий график")
async def send_work_schedule(message: Message):
    employee_id = message.from_user.id
    schedule = await get_work_schedule(employee_id)
    response_message = str(show_schedule(schedule))
    await message.answer(response_message, reply_markup=get_menu_keyboard())


@router.callback_query(lambda c: c.data.startswith("work_shedule:"))
async def handle_work_schedule_callback(callback_query: CallbackQuery):
    employee_id = int(callback_query.data.split(":")[1])
    schedule = await get_work_schedule(employee_id)
    response_message = show_schedule(schedule)
    await callback_query.message.answer(response_message)
    await callback_query.message.edit_reply_markup()
    await callback_query.answer()


def show_schedule(schedule: dict) -> str:
    if schedule:
        response_message = (
            f"Рабочий график для {schedule.get('fio', 'Неизвестно')}:\n\n"
            f"Понедельник: {schedule.get('Monday', 'Не указано')}\n"
            f"Вторник: {schedule.get('Tuesday', 'Не указано')}\n"
            f"Среда: {schedule.get('Wednesday', 'Не указано')}\n"
            f"Четверг: {schedule.get('Thursday', 'Не указано')}\n"
            f"Пятница: {schedule.get('Friday', 'Не указано')}\n"
            f"Суббота: {schedule.get('Saturday', 'Не указано')}\n"
            f"Воскресенье: {schedule.get('Sunday', 'Не указано')}\n"
        )
    else:
        response_message = "Рабочий график не найден."
    return response_message
