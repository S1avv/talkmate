from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

main_kb = ReplyKeyboardMarkup(
    keyboard= [
        [
            KeyboardButton(text="🔍 Начать поиск")
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите действие из меню"
)

leave_chat = ReplyKeyboardMarkup(
    keyboard= [
        [
            KeyboardButton(text="🚫 Закончить диалог")
        ]
    ],
    resize_keyboard=True,
)