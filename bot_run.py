import asyncio

from bot_create import dp, bot
from routers.user_private import router_start
from callbacks.cb_find_domain import cb_domain_action

# Подключение роутеров
dp.include_routers(
    router_start,
    cb_domain_action
)


async def main():
    """Главная функция старта бота"""
    await dp.start_polling(bot)


asyncio.run(main())
