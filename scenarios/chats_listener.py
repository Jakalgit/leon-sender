from aiogram import Router, Dispatcher, Bot, F
from aiogram.types import Message, ChatMemberUpdated

from db.database import remove_chat, add_chat


def load_handlers(dp: Dispatcher, _: Bot):
    router = Router()

    @router.my_chat_member()
    async def on_bot_added(update: ChatMemberUpdated):
        chat_id = str(update.chat.id)

        # Бот добавлен в чат
        if update.new_chat_member.status in ("member", "administrator"):
            add_chat(chat_id)
            print(f"Бот добавлен в чат {chat_id}")

        # Бот удалён или забанен
        elif update.new_chat_member.status == "kicked":
            remove_chat(chat_id)
            print(f"Бот удалён из чата {chat_id}")

    dp.include_router(router)