import aiohttp
import logging
from typing import Dict, Any


logger = logging.getLogger(__name__)


class BitrixSender:
    def __init__(self, webhook_url: str):
        self.webhook_url = webhook_url

    async def send_client_to_bitrix(self, client_data: Dict[str, Any]) -> bool:
        """
        Отправка данных клиента в Битрикс24
        """
        try:
            # Формируем URL для метода crm.lead.add
            method_url = f"{self.webhook_url}/crm.lead.add.json"

            # Формируем данные для создания лида в Битрикс24
            lead_data = {
                "fields": {
                    "TITLE": f"Клиент из Telegram: {client_data['name']}",
                    "NAME": client_data['name'],
                    "PHONE": [
                        {
                            "VALUE": client_data['number'],
                            "VALUE_TYPE": "WORK"
                        }
                    ],
                    "POST": client_data['position'],
                    "COMMENTS": client_data['description'],
                    "SOURCE_ID": "TELEGRAM_BOT",  # Источник - Telegram бот
                    "SOURCE_DESCRIPTION": f"Telegram ID: {client_data['telegram_id']}",
                    "UF_CRM_TELEGRAM_ID": str(client_data['telegram_id'])  # Если есть такое поле
                },
                "params": {
                    "REGISTER_SONET_EVENT": "Y"  # Создать событие в ленте
                }
            }

            logger.info(f"Отправка данных в Битрикс: {lead_data}")

            async with aiohttp.ClientSession() as session:
                async with session.post(method_url, json=lead_data) as response:
                    response_text = await response.text()
                    logger.info(f"Ответ от Битрикс: статус {response.status}, тело: {response_text}")

                    if response.status == 200:
                        result = await response.json()
                        if result.get('result'):
                            logger.info(f"Лид для клиента {client_data['name']} создан, ID: {result['result']}")
                            return True
                        else:
                            error_msg = result.get('error_description', 'Неизвестная ошибка')
                            raise ValueError(f"Ошибка создания лида: {error_msg}")
                    else:
                        raise ValueError(f"HTTP ошибка {response.status}: {response_text}")

        except Exception as e:
            raise e

    async def send_message_to_bitrix(self, message: str, client_data: Dict[str, Any]):
        """
        Отправка обычного сообщения в Битрикс
        """
        pass