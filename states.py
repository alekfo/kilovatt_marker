from aiogram.fsm.state import State, StatesGroup

# 2. Создаем класс состояний
class ClientStates(StatesGroup):
    """Класс для хранения состояний админа"""
    getting_number = State()
    getting_name = State()
    getting_position = State()
    getting_description =State()