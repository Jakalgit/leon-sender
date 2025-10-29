import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

import scenarios
from config import Config
from user_votes import cleanup_old_votes

bot = Bot(token=Config.BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

async def start_bot():
    await bot.delete_webhook(drop_pending_updates=True)

    scenarios.handler.load_handlers(dp, bot)

    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())


async def main():
    await asyncio.gather(
        cleanup_old_votes(),
        start_bot()
    )


if __name__ == '__main__':
    asyncio.run(main())