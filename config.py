from dotenv import load_dotenv
import os

load_dotenv()

BOT_TOKEN = os.getenv('BOT_TOKEN')
admin_id_main = int(os.getenv('ADMIN_ID_main'))
admin_id_add_1 = int(os.getenv('ADMIN_ID_add_1'))
BITRIX_WEBHOOK_URL = os.getenv('BITRIX_WEBHOOK_URL')