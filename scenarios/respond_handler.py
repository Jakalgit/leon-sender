import asyncio
import time

from aiogram import Dispatcher, Bot, Router, types
from aiogram.enums import ParseMode

from callback_data import RespondCallback, CallbackDataSimple
from config import Config
from user_votes import user_votes


def load_handler(dp: Dispatcher, bot: Bot):
    router = Router()

    @router.callback_query(RespondCallback.filter())
    async def handle_respond_callback_query(callback_query: types.CallbackQuery, callback_data: RespondCallback):
        sending_type = callback_data.type
        user_id = callback_data.user_id
        message_id = callback_query.message.message_id

        if message_id not in user_votes:
            user_votes[message_id] = (set(), time.time())

        if user_id in user_votes[message_id][0]:
            return

        user_votes[message_id][0].add(user_id)

        if sending_type == CallbackDataSimple.RECEIVE_ONLY_ME:
            chat_ids = [user_id]
        elif sending_type == CallbackDataSimple.RECEIVE_ALL_USERS:
            chat_ids = Config.USER_IDS
        else:
            chat_ids = []

        text = (f"<b>Отклик от пользователя @{callback_query.from_user.username}</b>\n"
                f"- - - - - - - - - - - -\nТекст рассылки:\n{callback_query.message.text}")

        for chat_id in chat_ids:
            try:
                await bot.send_message(
                    text=text,
                    chat_id=chat_id,
                    parse_mode=ParseMode.HTML
                )
                await asyncio.sleep(0.3)
            except Exception as e:
                print(e)

    dp.include_router(router)