from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Dispatcher, Bot

from middleware.db import DBSessionMiddleware
from db.config import settings

token = settings.bot_token
DYNADOT_API_KEY = settings.dynadot_api_key
DYNADOT_API_URL = "https://api.dynadot.com/api3.json"
PERCENT_BUY = 1.4

bot = Bot(token=token)
dp = Dispatcher(storage=MemoryStorage())
dp.message.middleware(DBSessionMiddleware())
dp.callback_query.middleware(DBSessionMiddleware())