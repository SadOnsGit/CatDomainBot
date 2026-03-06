from decimal import Decimal

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from .api_commands import check_payment, create_and_send_invoice
from db.commands import (
    create_promo_use,
    get_all_domains_user,
    get_promo_or_none,
    get_user_or_create,
    topup_balance,
)
from db.engine import async_session
from keyboard.mkp_profile_actions import mkp_profile, mkp_user_domains
from keyboard.mkp_cancel import mkp_cancel, mkp_menu

router_profile = Router()


class TopUpBalance(StatesGroup):
    get_amount = State()


class GetPromocode(StatesGroup):
    get_promocode = State()


@router_profile.callback_query(F.data.startswith("user."))
async def profile(
    call: CallbackQuery, state: FSMContext, db_session: async_session
):
    action = call.data.split(".")[1]
    if action == "profile":
        user = await get_user_or_create(
            session=db_session,
            user_id=call.from_user.id,
            username=call.from_user.username,
            full_name=call.from_user.full_name,
        )
        balance = user.balance

        await call.message.edit_text(
            "<b>Мой профиль:</b>\n"
            f"🆔 ID: <code>{user.id}</code>\n"
            f"💰 Баланс: <b>{str(balance)}</b> $\n",
            parse_mode="HTML",
            reply_markup=mkp_profile,
        )
    elif action == "domains":
        domains = await get_all_domains_user(db_session, call.from_user.id)
        keyboard = await mkp_user_domains(domains)
        await call.message.edit_text(
            "<b>Мои домены:</b>\n", parse_mode="HTML", reply_markup=keyboard
        )
    elif action == "top_up":
        await call.message.edit_text(
            "<b>Введите сумму пополнения (в $):</b>\n",
            parse_mode="HTML",
            reply_markup=mkp_cancel
        )
        await state.set_state(TopUpBalance.get_amount)
    elif action == "check_payment":
        _, _, payment_id, amount = call.data.split(".")
        result_payment = await check_payment(payment_id)
        if result_payment:
            result_topup = await topup_balance(
                session=db_session, user_id=call.from_user.id, amount=amount
            )
            if result_topup:
                await call.message.edit_text(
                    "<b>✅ Успешное пополнение баланса!</b>\n",
                    parse_mode="HTML",
                    reply_markup=mkp_menu
                )
        await call.answer("❌ Не оплачено")
    elif action == "promocode":
        await call.message.edit_text(
            "<b>Введите промокод:</b>\n",
            parse_mode="HTML",
            reply_markup=mkp_cancel
        )
        await state.set_state(GetPromocode.get_promocode)


@router_profile.message(TopUpBalance.get_amount)
async def get_amount(msg: Message, state: FSMContext):
    try:
        amount = Decimal(msg.text)
    except ValueError:
        await msg.answer("❌ Сумма должна быть числовым значением!")
    await create_and_send_invoice(msg, amount, msg.from_user.id, state)


@router_profile.message(GetPromocode.get_promocode)
async def get_promocode(
    msg: Message, state: FSMContext, db_session: async_session
):
    promo = await get_promo_or_none(msg.text, db_session)
    status, desc = await create_promo_use(promo, msg.from_user.id, db_session)
    if not status:
        if desc == "promocode_used":
            await msg.answer("❌ Вы уже использовали данный промокод!")
            return
        elif desc == "promo_uses_limit_reached":
            await msg.answer(
                "❌ Достигнуто максимальное количество использований данного промокода!"
            )
            return
    if not promo:
        await msg.answer("❌ Такого промокода не существует!")
        return
    amount = Decimal(promo.bonus_amount)
    res, desc = await topup_balance(db_session, msg.from_user.id, amount)
    if res:
        await msg.answer(
            "<b>✅ Успешное использование промокода."
            f"\nНа ваш баланс зачислено {amount}$</b>",
            parse_mode="HTML",
            reply_markup=mkp_menu
        )
    await state.clear()
