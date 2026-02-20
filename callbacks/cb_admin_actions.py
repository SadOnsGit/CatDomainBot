import asyncio

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram import Router, F
from aiogram.fsm.state import State, StatesGroup

from db.commands import get_all_users, topup_balance, create_promocode
from db.engine import async_session
from db.config import runtime
from keyboard.mkp_cancel import mkp_cancel

router_admin = Router()


class TopUpAction(StatesGroup):
    get_id = State()
    get_amount = State()


class CreatePromocode(StatesGroup):
    get_promo = State()
    get_max_uses = State()
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


@router_admin.message(CreatePromocode.get_promo)
async def get_promo(msg: Message, state: FSMContext):
    if len(msg.text) < 3:
        await msg.answer('❌ Промокод должен быть более 3 символов')
        return
    await state.update_data(promo=msg.text)
    await msg.answer(
        '<b>Введите количество использований промокода</b>',
        parse_mode='html'
    )
    await state.set_state(CreatePromocode.get_max_uses)


@router_admin.message(CreatePromocode.get_max_uses)
async def get_max_uses(msg: Message, state: FSMContext):
    try:
        max_uses = int(msg.text)
    except ValueError:
        await msg.answer(
            '<b>❌ Количество использований должно быть числом!</b>',
            parse_mode='html'
        )
    await state.update_data(max_uses=max_uses)
    await msg.answer(
        '<b>Теперь введите сумму промокода</b>',
        parse_mode='html'
    )
    await state.set_state(CreatePromocode.get_amount)


@router_admin.message(CreatePromocode.get_amount)
async def get_amount(msg: Message, state: FSMContext, db_session: async_session):
    try:
        amount = float(msg.text)
    except ValueError:
        await msg.answer(
            '<b>❌ Сумма должна быть числом!</b>',
            parse_mode='html'
        )
    data = await state.get_data()
    promo = data.get('promo')
    max_uses = data.get('max_uses')
    res, desc = await create_promocode(
        db_session,
        promo,
        max_uses,
        amount
    )
    if not res:
        await msg.answer(
            f'❌ Произошла ошибка: {desc}'
        )
        await state.clear()
    await msg.answer(
        f'<b>✅ Успешное создание промокода - </b> <code> {promo}</code>'
        f'\n<b>Количество использований: {max_uses}'
        f'\nСумма промокода: {amount}$</b>',
        parse_mode='html'
    )
    await state.clear()
    

@router_admin.message(SendMessage.get_message)
async def get_message(msg: Message, state: FSMContext, db_session: async_session):
    text = msg.text.strip()
    if not text:
        await msg.answer("Сообщение пустое, отправка отменена")
        await state.clear()
        return

    users = await get_all_users(db_session)
    if not users:
        await msg.answer("В базе нет пользователей")
        await state.clear()
        return

    sent_count = 0
    failed_count = 0

    for user in users:
        try:
            await msg.bot.send_message(
                chat_id=user.id,
                text=text,
                parse_mode="HTML",
                disable_web_page_preview=True
            )
            sent_count += 1
            await asyncio.sleep(0.05)
        except Exception as e:
            if "blocked" in str(e).lower() or "chat not found" in str(e).lower():
                print(f"Пользователь {user.id} заблокировал бота или удалил чат")
            failed_count += 1
        except Exception as e:
            print(f"Ошибка при отправке пользователю {user.id}: {e}")
            failed_count += 1

    await msg.answer(
        f"Рассылка завершена\n"
        f"Отправлено: {sent_count}\n"
        f"Не удалось: {failed_count}\n"
        f"Всего пользователей: {len(users)}"
    )

    await state.clear()