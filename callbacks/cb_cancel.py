from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

cb_cancel_router = Router()


@cb_cancel_router.callback_query(F.data.startswith("cancel."))
async def cancel_all(call: CallbackQuery, state: FSMContext):
    if call.data == "cancel.actions":
        await call.message.edit_text(
            "<b>❌ Успешно отменено</b>", parse_mode="html"
        )
        await state.clear()
