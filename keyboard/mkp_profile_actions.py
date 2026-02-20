from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

mkp_profile = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='💰 Пополнить баланс',
                             callback_data='profile.top_up')
    ],
    [
        InlineKeyboardButton(text='🎟️ Реферальная программа',
                             callback_data='user.referals'),
        InlineKeyboardButton(text='💳 Промокоды',
                             callback_data='user.promocode')
    ],
])


async def mkp_user_domains(domains):
    """
    Создаёт inline-клавиатуру со списком доменов пользователя.
    
    Каждая кнопка — название домена + callback с данными домена.
    """
    buttons = []

    if not domains:
        return InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="← Назад", callback_data="user.profile")]
        ])

    for domain in domains:
        callback_data = f"domain:info:{domain.id}"

        text = domain.domain_name

        buttons.append([
            InlineKeyboardButton(text=text, callback_data=callback_data)
        ])

    buttons.append([
        InlineKeyboardButton(text="← Назад в профиль", callback_data="user.profile")
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


async def mkp_domain_actions(domain_id):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Изменить NS-сервера",
                callback_data=f"domain:change_ns:{domain_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="Продлить домен",
                callback_data=f"domain:renew:{domain_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="Удалить / Перенести",
                callback_data=f"domain:delete:{domain_id}"
            )
        ],
        [
            InlineKeyboardButton(
                text="← Назад к списку",
                callback_data="user.domains"
            )
        ]
    ])
    return kb
