from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

mkp_cancel = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="❌ Отмена", callback_data="cancel.actions"
            )
        ]
    ]
)
