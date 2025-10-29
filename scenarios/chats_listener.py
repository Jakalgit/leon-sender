from aiogram import Router, Dispatcher, Bot, F
from aiogram.types import Message, ChatMemberUpdated

from db.database import remove_chat, add_chat
from logs import logger


def load_handlers(dp: Dispatcher, bot: Bot):
    router = Router()

    @router.my_chat_member()
    async def on_bot_added(update: ChatMemberUpdated):
        chat_id = str(update.chat.id)

        try:
            chat = await bot.get_chat(chat_id)
        except Exception as e:
            return

        # Бот добавлен в чат
        if update.new_chat_member.status in ("member", "administrator"):
            add_chat(chat_id)
            logger.info(msg=f"Бот добавлен в чат {chat_id}")

        # Бот удалён или забанен
        elif update.new_chat_member.status == "kicked":
            remove_chat(chat_id)
            logger.info(msg=f"Бот удалён из чата {chat_id}")

    dp.include_router(router)