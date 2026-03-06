from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from db.config import settings
from middleware.db import DBSessionMiddleware

token = settings.bot_token
DYNADOT_API_KEY = settings.dynadot_api_key
test_cryptopay_token = settings.test_crypto_pay_token
cryptopay_token = settings.crypto_pay_token
DYNADOT_API_URL = "https://api.dynadot.com/api3.json"

bot = Bot(token=token)
dp = Dispatcher(storage=MemoryStorage())
dp.message.middleware(DBSessionMiddleware())
dp.callback_query.middleware(DBSessionMiddleware())
