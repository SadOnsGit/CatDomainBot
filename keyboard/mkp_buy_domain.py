from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

mkp_buy_domain = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Купить", callback_data="domain.buy"),
            InlineKeyboardButton(
                text="❌ Отмена", callback_data="cancel.actions"
            ),
        ],
    ]
)
