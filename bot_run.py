import asyncio

from bot_create import bot, dp
from callbacks.cb_admin_actions import router_admin
from callbacks.cb_find_domain import cb_domain_action
from callbacks.cb_profile import router_profile
from callbacks.cb_cancel import cb_cancel_router
from db import base, engine
from routers.admin import router_admin_panel
from routers.user_private import router_start

dp.include_routers(
    router_start,
    cb_cancel_router,
    cb_domain_action,
    router_profile,
    router_admin_panel,
    router_admin,
)


async def main():
    """Главная функция старта бота"""
    async with engine.begin() as conn:
        await conn.run_sync(base.Base.metadata.create_all)
    await dp.start_polling(bot)


asyncio.run(main())
