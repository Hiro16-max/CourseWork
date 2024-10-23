from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder



def get_registration_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Да", callback_data="register_yes"),
             InlineKeyboardButton(text="Нет", callback_data="register_no")]
        ]
    )


def get_menu_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Список сотрудников"), KeyboardButton(text="Поиск по ФИО")],
            [KeyboardButton(text="Получить рабочий график")]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def create_pagination_buttons(current_page: int, total_pages: int) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    # Кнопка "Пред" отображается, если не на первой странице
    if current_page > 1:
        builder.add(InlineKeyboardButton(text="« Пред.", callback_data=f"page_{current_page - 1}"))

    # Кнопка "След" (Следующая) отображается, если не на последней странице
    if current_page < total_pages:
        builder.add(InlineKeyboardButton(text="След. »", callback_data=f"page_{current_page + 1}"))

    # Собираем клавиатуру
    keyboard = builder.as_markup()
    return keyboard

def get_employee_selection_keyboard(employees):
    """
    Создает клавиатуру для выбора сотрудника из списка.

    :param employees: Список сотрудников, где каждый элемент - это словарь с ключом 'fio'.
    :return: InlineKeyboardMarkup с кнопками для выбора сотрудника.
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=employee.fio, callback_data=f"select_employee_{employee.id}")]
        for employee in employees
    ])
    return keyboard


def get_workshedule_keyboard(employee_id: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Получить рабочий график?", callback_data=f"work_shedule:{employee_id}")]
        ]
    )

