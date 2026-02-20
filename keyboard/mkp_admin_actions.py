from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

mkp_adminpanel = InlineKeyboardMarkup(inline_keyboard=[
    [
        InlineKeyboardButton(text='💰 Пополнить баланс пользователю',
                             callback_data='admin.top_up')
    ],
    [
        InlineKeyboardButton(text='🤑 Изменить % маржи',
                             callback_data='admin.percent_buy')
    ],
    [
        InlineKeyboardButton(text='💳 Создать промокод',
                             callback_data='admin.add_promocode')
    ],
    [
        InlineKeyboardButton(text='Отправить 📩 пользователям',
                             callback_data='admin.send_message')
    ]
])