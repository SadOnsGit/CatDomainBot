from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

mkp_cancel = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="❌ Отмена", callback_data="actions.cancel"
            )
        ]
    ]
)



mkp_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="💻 Меню", callback_data="actions.menu"
            )
        ]
    ]
)