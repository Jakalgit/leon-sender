from aiogram import Dispatcher, Bot, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import Command

from filters import UserFilter
from messages import Messages


def load_handlers(dp: Dispatcher, _: Bot):
    router = Router()

    @router.message(Command('status'), UserFilter())
    async def handle_sending_command(message: types.Message):
        await message.answer(
            text=Messages.STATUS,
            parse_mode=ParseMode.HTML,
        )

    dp.include_router(router)