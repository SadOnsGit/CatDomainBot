from os import environ

from aiogram.fsm.storage.memory import MemoryStorage
from aiogram import Dispatcher, Bot
from dotenv import load_dotenv

load_dotenv()

token = environ.get('BOT_TOKEN')
group_id = environ.get('GROUP_ID')
DYNADOT_API_KEY = environ.get('DYNADOT_API_KEY')
DYNADOT_API_URL = "https://api.dynadot.com/api3.json"
PERCENT_BUY = 1.4

bot = Bot(token=token)
dp = Dispatcher(storage=MemoryStorage())