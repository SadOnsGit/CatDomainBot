from aiogram import Router
from aiogram.filters import Command
from aiogram import types

from db.config import settings

router_admin_panel = Router()


@router_admin_panel.message(Command('admin'))
async def admin_panel(msg: types.Message):
    if msg.from_user.id in settings.admins:
        await msg.answer('<b>Админ панель CatDomainBot 🐱</b>',
                        parse_mode='html')