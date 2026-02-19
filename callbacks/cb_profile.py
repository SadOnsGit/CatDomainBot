from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram import Router, F
from aiogram.fsm.state import State, StatesGroup


from db.commands import get_user_or_create
from db.engine import async_session
from keyboard.mkp_profile_actions import mkp_profile

router_profile = Router()


@router_profile.callback_query(F.data.startswith('user.'))
async def profile(call: CallbackQuery, state: FSMContext, db_session: async_session):

    action = call.data.split('.')[1]
    if action == 'profile':
        user = await get_user_or_create(
            session=db_session,
            user_id=call.from_user.id,
            username=call.from_user.username,
            full_name=call.from_user.full_name
        )
        balance = user.balance

        await call.message.edit_text(
            "<b>Мой профиль:</b>\n"
            f"🆔 ID: <code>{user.id}</code>\n"
            f"💰 Баланс: <b>{str(balance)}</b> $\n",
            parse_mode='HTML',
            reply_markup=mkp_profile
        )