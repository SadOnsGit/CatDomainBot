from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message

from .api_commands import (
    change_domain_nameservers,
    get_domain_nameservers,
    register_domain,
    search_domain,
)
from db.commands import buy_domain, get_domain_by_id
from db.config import runtime
from db.engine import async_session
from keyboard.mkp_buy_domain import mkp_buy_domain
from keyboard.mkp_cancel import mkp_cancel, mkp_menu
from keyboard.mkp_profile_actions import mkp_domain_actions


class FindDomain(StatesGroup):
    get_domain = State()


class BuyDomain(StatesGroup):
    get_years = State()
    get_ns = State()


class ChangeNS(StatesGroup):
    waiting_ns = State()


cb_domain_action = Router()


@cb_domain_action.callback_query(F.data.startswith("domain."))
async def domain_actions(
    call: CallbackQuery, state: FSMContext, db_session: async_session
):
    action = call.data.split(".")[1]
    if action == "search":
        await call.message.edit_text(
            f"<b>😼 Котики готовы найти домен для вас, введите в формате:"
            "\n\nexample.com"
            "\n----------"
            "\nexample1.com"
            "\nexample2.com"
            "\nexample3.com </b>",
            parse_mode="html",
            reply_markup=mkp_cancel,
        )
        await state.set_state(FindDomain.get_domain)
    elif action == "buy":
        data = await state.get_data()
        domain = data.get("domain")
        years = data.get("years")
        ns = data.get("ns")
        price = data.get("price", 0.0)
        payment_method = "balance"
        user_id = call.from_user.id
        status, desc = await buy_domain(
            db_session,
            user_id,
            price,
            domain,
            years,
            payment_method,
        )
        if desc == "insufficient_funds":
            await call.message.edit_text(
                f"<b>🙀 Недостаточно средств. Пополните баланс</b>",
                parse_mode="html",
                reply_markup=mkp_menu
            )
            await state.clear()
        if status:
            res = await register_domain(ns, domain, years)
            reg = res.get("RegisterResponse", {})
            success = (
                reg.get("ResponseCode") == "0"
                or "success" in str(reg.get("Status", "")).lower()
            )
            if success:
                await call.message.edit_text(
                    f"<b>😼 Котики успешно купили для вас домен:"
                    "\n\nИнформация о домене:"
                    "\n----------"
                    f"\n1. Домен - {domain}"
                    f"\n2. NS-Сервера - {' '.join(ns)}"
                    f"\n3. Срок действия домена: {years} год/лет</b>",
                    parse_mode="html",
                    reply_markup=mkp_menu
                )
                await state.clear()


@cb_domain_action.message(FindDomain.get_domain)
async def get_domain(msg: Message, state: FSMContext):
    if len(msg.text) < 4 or "." not in msg.text:
        await msg.reply("❌ Пожалуйста, введите корректное доменное имя.")
        return

    res = await search_domain(msg.text)
    search_results = res["SearchResponse"]["SearchResults"]
    if "Error" in search_results[0]:
        error = search_results[0].get("Error")
        if "unsupported domain type" in error:
            await msg.reply("❌ Неподдерживаемый домен. Выберите другой")
            return
    if search_results and search_results[0]["Available"] == "yes":
        price = search_results[0]["Price"].split()[2]
        final_price = float(price) * runtime.percent_buy
        await msg.reply(
            "<b>😼 Котики сказали, что домен свободен и вы можете его приобрести!"
            f"\n💰 Цена домена: {final_price:.2f}$"
            "\nНа сколько лет возьмёте домен? (от 1 до 10)</b>",
            parse_mode="html",
            reply_markup=mkp_cancel
        )
        await state.update_data(domain=msg.text, price=final_price)
        await state.set_state(BuyDomain.get_years)
    else:
        await msg.reply(
            "❌ К сожалению котики сказали что домен недоступен 😿"
            "\nВам нужно выбрать другой домен."
        )


@cb_domain_action.message(BuyDomain.get_years)
async def get_years(msg: Message, state: FSMContext):
    try:
        years = int(msg.text)
    except ValueError:
        await msg.answer("❌ Год должен быть числовым значением!")
        return
    if years > 10 and years < 1:
        await msg.answer("❌ Значение должно быть в диапазоне от 1 до 10!")
        return
    await state.update_data(years=years)
    await msg.answer(
        "<b>😼 Отлично! Хотите ли вы сразу указать NS сервера?"
        "Напишите их через пробел или укажите «нет» / «пропустить» - чтобы сделать это потом.</b>",
        parse_mode="html",
        reply_markup=mkp_cancel
    )
    await state.set_state(BuyDomain.get_ns)


@cb_domain_action.message(BuyDomain.get_ns)
async def get_ns(msg: Message, state: FSMContext):
    text = msg.text.strip().lower()
    ns_list = []
    if text not in ("нет", "пропустить") or "." in text:
        ns_list = [ns.strip() for ns in text.split()]
    await state.update_data(ns=ns_list)
    data = await state.get_data()
    domain = data.get("domain")
    years = data.get("years")
    price = data.get("price", 0.0)
    ns_info = (
        f"NS: {' '.join(ns_list)}\n" if ns_list else "Без NS (по умолчанию)\n"
    )

    await msg.answer(
        f"Подтверждение покупки:\n\n"
        f"Домен: <b>{domain}</b>\n"
        f"Срок: {years} лет\n"
        f"Цена: <b>{price} $</b>\n"
        f"{ns_info}"
        f"Спишется с баланса ⚠️",
        reply_markup=mkp_buy_domain,
        parse_mode="HTML",
    )


@cb_domain_action.callback_query(F.data.startswith("domain:info:"))
async def show_domain_detail(call: CallbackQuery, db_session: async_session):
    """
    Показывает подробную информацию о домене + кнопки управления
    """
    domain_id = int(call.data.split(":")[-1])
    domain = await get_domain_by_id(domain_id, db_session)

    bought_str = (
        domain.created_at.strftime("%Y-%m-%d") if domain.created_at else "—"
    )
    expires_str = (
        domain.expires_at.strftime("%Y-%m-%d") if domain.expires_at else "—"
    )

    current_ns = await get_domain_nameservers(domain.domain_name)
    ns_text = "не указаны (используются по умолчанию)"
    if current_ns:
        ns_text = "\n".join(f"  ┗ {ns}" for ns in current_ns)

    text = (
        f"🌐 <b>{domain.domain_name}</b>\n\n"
        f"┠ Куплен: {bought_str}\n"
        f"┠ Истекает: {expires_str}\n\n"
        f"<b>💻 NS-сервера:</b>\n"
        f"{ns_text}"
    )
    keyboard = await mkp_domain_actions(domain.id)
    try:
        await call.message.edit_text(
            text, parse_mode="HTML", reply_markup=keyboard
        )
    except Exception as e:
        await call.message.answer(
            text, parse_mode="HTML", reply_markup=keyboard
        )

    await call.answer()


@cb_domain_action.callback_query(F.data.startswith("domain:change_ns:"))
async def start_change_ns(call: CallbackQuery, state: FSMContext):
    try:
        domain_id = int(call.data.split(":")[-1])
    except:
        await call.answer("Ошибка", show_alert=True)
        return

    await state.update_data(domain_id=domain_id)

    await call.message.edit_text(
        "Введите новые NS-сервера:\n\n"
        "• По одному на строку\n"
        "• Или через пробел/запятую\n\n"
        "Примеры:\n"
        "ns0.cloudflare.com ns1.cloudflare.com\n\n"
        "Напишите «пропустить» или «отмена», чтобы не менять.",
        parse_mode="HTML",
        reply_markup=mkp_cancel
    )

    await state.set_state(ChangeNS.waiting_ns)
    await call.answer()


@cb_domain_action.message(ChangeNS.waiting_ns)
async def process_new_ns(
    msg: Message, state: FSMContext, db_session: async_session
):
    text = msg.text.strip()

    ns_raw = text.replace(",", " ").replace("\n", " ").split()
    new_ns = [ns.strip() for ns in ns_raw if ns.strip() and "." in ns]

    if not new_ns:
        await msg.answer("Не удалось распознать NS-сервера. Попробуйте снова.")
        return

    data = await state.get_data()
    domain_id = data.get("domain_id")

    domain = await get_domain_by_id(domain_id, db_session)
    if not domain:
        await msg.answer("Домен не найден.")
        await state.clear()
        return

    success, message = await change_domain_nameservers(
        domain.domain_name, new_ns
    )

    if success:
        await msg.answer(
            f"✅ NS-сервера успешно изменены!\n\n"
            f"Новые NS:\n"
            + "\n".join(f"• {ns}" for ns in new_ns)
            + f"\n\nИзменение может занять до 24–48 часов."
        )
    else:
        await msg.answer(f"❌ Не удалось изменить NS:\n{message}")

    await state.clear()
