import logging
import asyncio

from aiogram import types, Router, F, Bot
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart


from states import ClientStates
from config import admin_id_main, admin_id_add_1
from keyboards.main_keyboards import get_number_keyboard, clients_link_keyboard
from data.db_control import is_client, add_client
from bitrix_integration import BitrixSender
from config import BITRIX_WEBHOOK_URL

# Создаем экземпляр отправителя
bitrix_sender = BitrixSender(BITRIX_WEBHOOK_URL)

logger = logging.getLogger(__name__)
common_router = Router()
cancel_router = Router()

ADMIN_IDS = [admin_id_main, admin_id_add_1]

@common_router.message(Command("start"))
async def cmd_start(message: types.Message, state: FSMContext):
    """
    Этот обработчик срабатывает на команду /start и при первом входе
    """
    user_id = message.from_user.id

    if user_id in ADMIN_IDS:
        await message.answer(
            f'⚙️Вы яляетесь администратором чат-бота\n\n'
        )
        return

    if is_client(user_id):
        await message.answer(
            f'⏳Дождитесь звонка оператора. Ваш запрос обрабатывается...\n\n'
        )
        return

    # Сохраняем данные пользователя в state
    await state.update_data(
        clients_id=user_id
    )

    await message.answer(
        '👋Здравствуйте! Вы пишите менеджеру Киловатт Маркет.\n\n'
        '📲Для начала отправьте разрешение для передачи номера телефона для связи.',
            reply_markup=get_number_keyboard()
    )

    await state.set_state(ClientStates.getting_number)

@common_router.message(StateFilter(ClientStates.getting_number), F.contact)
async def get_contact(message: types.Message, state: FSMContext, bot: Bot):

    contact = message.contact

    if contact and contact.user_id == message.from_user.id:
        # Сохраняем номер
        await state.update_data(clients_number=contact.phone_number)

    await message.answer(
        '✅Благодарим Вас, за оставленный контакт.\n\n'
        '📝Назовите пожалуйста Ваше имя.',
        reply_markup=types.ReplyKeyboardRemove()
    )

    await state.set_state(ClientStates.getting_name)


@common_router.message(StateFilter(ClientStates.getting_name))
async def get_name(message: types.Message, state: FSMContext, bot: Bot):
    gotten_name = message.text
    # if len(gotten_name.strip().split()) != 3:
    #     await message.answer(
    #         '❌Введите полное ФИО, пожалуйста.\n\n👉Пример:\n'
    #         '*Иванов Иван Иванович*',
    #         parse_mode="Markdown"
    #     )
    #     return
    #
    # if not all([i_part.isalpha() for i_part in gotten_name.strip().split()]):
    #     await message.answer(
    #         '❌ФИО может состоять только из букв. Повторите попытку.\n\n👉Пример:\n'
    #         '*Иванов Иван Иванович*',
    #         parse_mode="Markdown"
    #     )
    #     return

    await state.update_data(clients_name=gotten_name.strip())

    await message.answer(
        '✅Записал!\n\n💼Теперь пришлите Вашу должность.'
    )

    await state.set_state(ClientStates.getting_position)

@common_router.message(StateFilter(ClientStates.getting_position))
async def get_position(message: types.Message, state: FSMContext, bot: Bot):

    gotten_position = message.text
    await state.update_data(clients_position=gotten_position.strip())

    await message.answer(
        '✅  Огромное спасибо за предоставленную информацию.\n\n💬Опишите пожалуйста Вашу проблему'
    )

    await state.set_state(ClientStates.getting_description)


@common_router.message(StateFilter(ClientStates.getting_description))
async def get_description(message: types.Message, state: FSMContext, bot: Bot):

    gotten_description = message.text
    user_id = message.from_user.id

    await state.update_data(clients_description=gotten_description.strip())

    await message.answer(
        '✅Вся необходимая информация получена, наш менеджер скоро свяжется с Вами.'
    )

    saved_data = await state.get_data()

    try:
        client = add_client(
            saved_data['clients_id'],
            saved_data['clients_name'],
            saved_data['clients_number'],
            saved_data['clients_position'],
            saved_data['clients_description']
        )
    except Exception as e:
        # Отправляем сообщение админу
        logger.error(f"Ошибка добавления клиента #{saved_data['clients_id']} в базу")
        admin_message = (
            f"Ошибка при добавлении клиента #{saved_data['clients_id']} в базу. Клиент ожидает звонка - его имя - {saved_data['clients_name']}, его номер - {saved_data['clients_number']}"
        )
    else:
        admin_message = (
            "👤*Новый клиент!*\n\n"
            f"👤*Имя:* {client.name}\n"
            f"🆔*Телеграм-ID:* {client.telegram_id}\n"
            f"📞*Номер телефона:* {client.number}\n"
            f"💼*Должность:* {client.position}\n"
            f"📝*Описание проблемы:* {client.description}\n"
        )
    for admin_id_i in ADMIN_IDS:
        try:
            await bot.send_message(
                chat_id=admin_id_i,
                text=admin_message,
                reply_markup=clients_link_keyboard(user_id),
                parse_mode="Markdown"
            )
            logger.info(f"Сообщение отправлено админу {admin_id_i}")
        except Exception as e:
            logger.error(f"Ошибка отправки админу {admin_id_i}: {e}")

    try:

        #Отправка в Битрикс
        bitrix_data = {
            'telegram_id': saved_data['clients_id'],
            'name': saved_data['clients_name'],
            'number': saved_data['clients_number'],
            'position': saved_data['clients_position'],
            'description': saved_data['clients_description']
        }

        # Ждем результат отправки
        result = await bitrix_sender.send_client_to_bitrix(bitrix_data)

        if result:
            output_mssg = '✅ Информация о клиенте успешно отправлена в Битрикс'
            logger.info(output_mssg)
        else:
            output_mssg = '⚠️ Не удалось отправить данные в Битрикс (сервер вернул ошибку)'
            logger.warning(output_mssg)

    except Exception as e:
        output_mssg = f'❌ Ошибка отправки в Битрикс: {str(e)}'
        logger.error(output_mssg)

    # Отправляем результат админам
    for admin_id_i in ADMIN_IDS:
        try:
            await bot.send_message(
                chat_id=admin_id_i,
                text=output_mssg,
                parse_mode="Markdown"
            )
            logger.info(f"Сообщение об отправке в Битрикс отправлено админу {admin_id_i}")
        except Exception as e:
            logger.error(f"Ошибка отправки админу {admin_id_i}: {e}")

    await state.clear()



@common_router.message(StateFilter(None))
async def handle_any_message(message: types.Message, state: FSMContext):
    """Обработчик любых сообщений без состояния"""
    await cmd_start(message, state)


@cancel_router.message(Command("cancel"))
@cancel_router.message(lambda message: message.text == "↩️Отмена")
async def cancel_handler(message: types.Message, state: FSMContext):
    """Сброс состояния"""

    await state.clear()

    await message.answer(
        "🚀Используйте /start для начала работы.",
        reply_markup=types.ReplyKeyboardRemove()
    )