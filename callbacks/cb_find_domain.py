import requests

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram import Router, F
from aiogram.fsm.state import State, StatesGroup

from keyboard.mkp_cancel import mkp_cancel
from keyboard.mkp_buy_domain import mkp_buy_domain
from bot_create import DYNADOT_API_KEY, DYNADOT_API_URL, PERCENT_BUY

class FindDomain(StatesGroup):
    get_domain = State()


class BuyDomain(StatesGroup):
    get_years = State()
    get_ns = State()


cb_domain_action = Router()

@cb_domain_action.callback_query(F.data.startswith('domain.'))
async def domain_actions(call: CallbackQuery, state: FSMContext):
    action = call.data.split('.')[1]
    if action == 'search':
        await call.message.edit_text(
            f'<b>😼 Котики готовы найти домен для вас, введите в формате:'
            '\n\nexample.com'
            '\n----------'
            '\nexample1.com'
            '\nexample2.com'
            '\nexample3.com </b>',
            parse_mode='html',
            reply_markup=mkp_cancel
        )
        await state.set_state(FindDomain.get_domain)
    elif action == 'buy':
        data = await state.get_data()
        domain = data.get("domain")
        years = data.get("years")
        ns = data.get('ns')
        res = await register_domain(ns, domain, years)
        print(res)
        reg = res.get("RegisterResponse", {})
        success = reg.get("ResponseCode") == "0" or "success" in str(reg.get("Status", "")).lower()
        if success:
            await call.message.edit_text(
                f'<b>😼 Котики успешно купили для вас домен:'
                '\n\nИнформация о домене:'
                '\n----------'
                f'\n1. Домен - {domain}'
                f'\n2. NS-Сервера - {' '.join(ns)}'
                f'\n3. Срок действия домена: {years} год/лет</b>',
                parse_mode='html',
            )
            await state.clear()



@cb_domain_action.message(FindDomain.get_domain)
async def get_domain(msg: Message, state: FSMContext):
    if len(msg.text) < 4 or '.' not in msg.text:
        await msg.reply("❌ Пожалуйста, введите корректное доменное имя.")
        return

    res = await search_domain(msg.text)
    search_results = res['SearchResponse']['SearchResults']
    
    if search_results and search_results[0]['Available'] == 'yes':
        price = search_results[0]['Price'].split()[2]
        final_price = float(price) * PERCENT_BUY
        await msg.reply(
            '<b>😼 Котики сказали, что домен свободен и вы можете его приобрести!'
            f'\n💰 Цена домена: {final_price}$'
            '\nНа сколько лет возьмёте домен? (от 1 до 10)</b>',
            parse_mode='html',
        )
        await state.update_data(domain=msg.text, price=final_price)
        await state.set_state(BuyDomain.get_years)
    else:
        await msg.reply(
            '❌ К сожалению котики сказали что домен недоступен 😿'
            '\nВам нужно выбрать другой домен.'
        )
        await state.clear()


@cb_domain_action.message(BuyDomain.get_years)
async def get_years(msg: Message, state: FSMContext):
    try:
        years = int(msg.text)
    except ValueError:
        await msg.answer('❌ Год должен быть числовым значением!')
        return
    if years > 10 and years < 1:
        await msg.answer('❌ Значение должно быть в диапазоне от 1 до 10!')
        return
    await state.update_data(years=years)
    await msg.answer(
        '<b>😼 Отлично! Хотите ли вы сразу указать NS сервера?'
        'Напишите их через пробел или укажите «нет» / «пропустить» - чтобы сделать это потом.</b>',
        parse_mode='html'
    )
    await state.set_state(BuyDomain.get_ns)
    

@cb_domain_action.message(BuyDomain.get_ns)
async def get_ns(msg: Message, state: FSMContext):
    text = msg.text.strip().lower()
    ns_list = []
    if text not in ('нет', 'пропустить') or '.' in text:
        ns_list = [ns.strip() for ns in text.split()]
    await state.update_data(ns=ns_list)
    data = await state.get_data()
    domain = data.get("domain")
    years = data.get("years")
    price = data.get("price", 0.0)
    ns_info = f"NS: {' '.join(ns_list)}\n" if ns_list else "Без NS (по умолчанию)\n"

    await msg.answer(
        f"Подтверждение покупки:\n\n"
        f"Домен: <b>{domain}</b>\n"
        f"Срок: {years} лет\n"
        f"Цена: <b>{price} $</b>\n"
        f"{ns_info}"
        f"Спишется с баланса ⚠️",
        reply_markup=mkp_buy_domain,
        parse_mode="HTML"
    )


async def search_domain(domain) -> dict:
    params = {
        "key": DYNADOT_API_KEY,
        "command": 'search',
        "domain0": domain,
        "show_price": "1",
        "currency": "EUR"
    }
    try:
        r = requests.get(DYNADOT_API_URL, params=params, timeout=18)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}


async def register_domain(ns, domain, years):
    params = {
        "key": DYNADOT_API_KEY,
        "command": 'register',
        "domain": domain,
        "currency": "EUR",
        "duration": str(years)
    }
    if ns:
        for i, ns in enumerate(ns):
            params[f"ns{i}"] = ns
    try:
        r = requests.get(DYNADOT_API_URL, params=params, timeout=18)
        r.raise_for_status()
        return r.json()
    except Exception as e:
        return {"error": str(e)}