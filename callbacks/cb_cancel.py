from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from keyboard.mkp_main import mkp_main
from keyboard.mkp_cancel import mkp_menu

cb_cancel_router = Router()


@cb_cancel_router.callback_query(F.data.startswith("actions."))
async def cancel_all(call: CallbackQuery, state: FSMContext):
    action = call.data.split(".")[1]
    if action == "cancel":
        await call.message.edit_text(
            "<b>❌ Успешно отменено</b>", parse_mode="html",
            reply_markup=mkp_menu
        )
        await state.clear()
    elif action == "menu":
        await call.message.edit_text(
            "<b>💻 Меню</b>", parse_mode="html",
            reply_markup=mkp_main
        )
        await state.clear()
