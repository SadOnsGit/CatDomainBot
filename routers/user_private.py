from aiogram import Router
from aiogram.filters import Command
from aiogram import types

from keyboard.mkp_main import mkp_main

router_start = Router()


@router_start.message(Command('start'))
async def start_message(msg: types.Message):
    await msg.answer('<b>Добро пожаловать CatDomainBot 🐱'
                     '\nКотики помогут вам найти идеальный домен по низкой цене! 🐱✨'
                     '\nВведите желаемое доменное имя, и наши пушистые помощники тщательно проберутся через интернет, чтобы найти все доступные варианты!</b>',
                     parse_mode='html', reply_markup=mkp_main)