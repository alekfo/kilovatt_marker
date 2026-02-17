from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram import types

def get_number_keyboard():
    """Клавиатура для получения номера телефона"""
    keyboard = [
        [types.KeyboardButton(
            text="📱 Отправить номер телефона",
            request_contact=True
        )],
        [types.KeyboardButton(text="Отмена")]
    ]
    return types.ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder="Нажмите кнопку для отправки контакта"
    )