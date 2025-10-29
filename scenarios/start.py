from aiogram import Router, types, Dispatcher, Bot
from aiogram.enums import ParseMode
from aiogram.filters import Command

from filters import UserFilter
from messages import Messages


def load_handlers(dp: Dispatcher, _: Bot):
    router = Router()

    @router.message(Command('start'), UserFilter())
    async def start(message: types.Message):
        await message.answer(
            text=Messages.START_MESSAGE,
            parse_mode=ParseMode.HTML
        )

    dp.include_router(router)