from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

mkp_main = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🔎 Поиск домена", callback_data="domain.search"
            )
        ],
        [
            InlineKeyboardButton(
                text="👁 Мои домены", callback_data="user.domains"
            ),
            InlineKeyboardButton(
                text="🐱 Мой Профиль", callback_data="user.profile"
            ),
        ],
    ]
)
