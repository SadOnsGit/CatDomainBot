import asyncio

from bot_create import dp, bot
from routers.user_private import router_start
from callbacks.cb_find_domain import cb_domain_action
from db import engine, base

dp.include_routers(
    router_start,
    cb_domain_action
)


async def main():
    """Главная функция старта бота"""
    async with engine.begin() as conn:
        await conn.run_sync(base.Base.metadata.create_all)
    await dp.start_polling(bot)


asyncio.run(main())
