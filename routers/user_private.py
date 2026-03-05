from aiogram import Router, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from db.commands import get_user_or_create
from db.engine import async_session
from keyboard.mkp_main import mkp_main

router_start = Router()


@router_start.message(Command("start"))
async def start_message(
    msg: types.Message, state: FSMContext, db_session: async_session
):
    await get_user_or_create(
        session=db_session,
        user_id=msg.from_user.id,
        username=msg.from_user.username,
        full_name=msg.from_user.full_name,
    )
    await msg.answer(
        "<b>Добро пожаловать CatDomainBot 🐱"
        "\nКотики помогут вам найти идеальный домен по низкой цене! 🐱✨"
        "\nВведите желаемое доменное имя, и наши пушистые помощники тщательно проберутся через интернет, чтобы найти все доступные варианты!</b>",
        parse_mode="html",
        reply_markup=mkp_main,
    )
    await state.clear()
