from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram import Router, F
from aiogram.fsm.state import State, StatesGroup

from db.commands import topup_balance
from db.engine import async_session
from db.config import runtime
from keyboard.mkp_cancel import mkp_cancel

router_admin = Router()


class TopUpAction(StatesGroup):
    get_id = State()
    get_amount = State()


class CreatePromocode(StatesGroup):
    get_promo = State()
    get_use_count = State()
    get_amount = State()


class ChangeBuyPercent(StatesGroup):
    get_percent = State()


class SendMessage(StatesGroup):
    get_message = State()


@router_admin.callback_query(F.data.startswith('admin.'))
async def admin_actions(call: CallbackQuery, state: FSMContext):
    action = call.data.split('.')[1]
    if action == 'top_up':
        await call.message.edit_text(
            f'<b>Введите айди пользователя:</b>',
            parse_mode='html',
            reply_markup=mkp_cancel
        )
        await state.set_state(TopUpAction.get_id)
    elif action == 'percent_buy':
        await call.message.edit_text(
            f'<b>Введите новый процент продажи в формате (1.0-2.0):</b>',
            parse_mode='html',
            reply_markup=mkp_cancel
        )
        await state.set_state(ChangeBuyPercent.get_percent)
    elif action == 'add_promocode':
        await call.message.edit_text(
            f'<b>Введите промокод:</b>',
            parse_mode='html',
            reply_markup=mkp_cancel
        )
        await state.set_state(CreatePromocode.get_promo)
    elif action == 'send_message':
        await call.message.edit_text(
            f'<b>Введите текст для рассылки(можно с HTML тегами):</b>',
            parse_mode='html',
            reply_markup=mkp_cancel
        )
        await state.set_state(SendMessage.get_message)


@router_admin.message(TopUpAction.get_id)
async def get_id(msg: Message, state: FSMContext):
    try:
        user_id = int(msg.text)
    except ValueError:
        await msg.answer('❌ Айди должен быть числом!')
        return
    await state.update_data(user_id=user_id)
    await msg.answer(
        '<b>Теперь введите сумму пополнения</b>',
        parse_mode='html',
        reply_markup=mkp_cancel
    )
    await state.set_state(TopUpAction.get_amount)


@router_admin.message(TopUpAction.get_amount)
async def get_id(msg: Message, state: FSMContext, db_session: async_session):
    try:
        amount = float(msg.text)
    except ValueError:
        await msg.answer('❌ Сумма должна быть числом!')
        return
    data = await state.get_data()
    user_id = data.get('user_id')
    res, desc = await topup_balance(
        db_session,
        user_id,
        amount
    )
    if not res:
        await msg.answer(
            f'❌ Произошла ошибка: {desc}'
        )
        await state.clear()

    await msg.answer(
        f'<b>✅ Успешное пополнение баланса - {user_id} на сумму {amount} $</b>',
        parse_mode='html'
    )
    await state.clear()


@router_admin.message(ChangeBuyPercent.get_percent)
async def change_procent(msg: Message, state: FSMContext):
    try:
        percent = float(msg.text)
    except ValueError:
        await msg.answer('❌ Процент должен быть числом!')
    runtime.percent_buy = percent
    await msg.answer(
        f'<b>✅ Успешное изменение процента на - {percent}</b>',
        parse_mode='html'
    )
    await state.clear()


