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