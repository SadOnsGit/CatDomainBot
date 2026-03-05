from aiogram import Router, types
from aiogram.filters import Command

from db.config import settings
from keyboard.mkp_admin_actions import mkp_adminpanel

router_admin_panel = Router()


@router_admin_panel.message(Command("admin"))
async def admin_panel(msg: types.Message):
    if msg.from_user.id in settings.admins:
        await msg.answer(
            "<b>Админ панель CatDomainBot 🐱</b>",
            parse_mode="html",
            reply_markup=mkp_adminpanel,
        )
