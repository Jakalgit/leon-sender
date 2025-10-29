import asyncio
import re

from aiogram import Dispatcher, Bot, Router, types, F
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from callback_data import CallbackDataSimple, RespondCallback
from db.database import get_chats
from filters import UserFilter
from messages import Messages
from states import States


def load_handlers(dp: Dispatcher, bot: Bot):
    router = Router()

    @router.message(Command('sending'), UserFilter())
    async def handle_sending_command(message: types.Message, state: FSMContext):
        inline_keyboard = [
                    [InlineKeyboardButton(text="Получу только я", callback_data=CallbackDataSimple.RECEIVE_ONLY_ME)],
                    [InlineKeyboardButton(text="Получат все пользователи", callback_data=CallbackDataSimple.RECEIVE_ALL_USERS)],
                ]
        await message.answer(
            text=Messages.START_SENDING_MESSAGE,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
        )

        await state.clear()

    async def handle_after_select_receive_type(callback_query: types.CallbackQuery):
        await callback_query.message.delete_reply_markup()
        await callback_query.message.answer(
            text=Messages.AVAILABLE_CHATS,
            parse_mode=ParseMode.HTML
        )
        try:
            chats = get_chats()
            for c in chats:
                chat = await bot.get_chat(int(c['chat_id']))
                text = f"<b>[<code>{chat.id}</code>] {chat.title}</b>"
                await bot.send_message(
                    chat_id=callback_query.message.chat.id,
                    text=text,
                    parse_mode=ParseMode.HTML
                )
                await asyncio.sleep(0.3)
        except TelegramBadRequest as e:
            await callback_query.message.reply(f"Не удалось получить информацию о чате: {e}")
            return
        except Exception as e:
            await callback_query.message.reply(f"Ошибка: {e}")
            return

        inline_keyboard = [
            [InlineKeyboardButton(text="Отправить во все", callback_data=CallbackDataSimple.SEND_IN_ALL)],
            [InlineKeyboardButton(text="Выбрать из списка", callback_data=CallbackDataSimple.SEND_IN_SOME)],
        ]

        await callback_query.message.answer(
            text=Messages.SELECT_CHATS_FOR_SENDING,
            parse_mode=ParseMode.HTML,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
        )

    @router.callback_query(F.data == CallbackDataSimple.RECEIVE_ONLY_ME)
    async def handle_receive_only_me(callback_query: types.CallbackQuery, state: FSMContext):
        await state.update_data(sending_type=CallbackDataSimple.RECEIVE_ONLY_ME)
        await handle_after_select_receive_type(callback_query)

    @router.callback_query(F.data == CallbackDataSimple.RECEIVE_ALL_USERS)
    async def handle_receive_only_me(callback_query: types.CallbackQuery, state: FSMContext):
        await state.update_data(sending_type=CallbackDataSimple.RECEIVE_ALL_USERS)
        await handle_after_select_receive_type(callback_query)

    @router.callback_query(F.data == CallbackDataSimple.SEND_IN_SOME)
    async def handle_send_in_some(callback_query: types.CallbackQuery, state: FSMContext):
        await callback_query.message.delete_reply_markup()
        await callback_query.message.answer(
            text=Messages.INPUT_CHAT_IDS,
            parse_mode=ParseMode.HTML
        )
        await state.set_state(States.sending_ids)

    @router.callback_query(F.data == CallbackDataSimple.SEND_IN_ALL)
    async def handle_send_in_all(callback_query: types.CallbackQuery, state: FSMContext):
        await callback_query.message.delete_reply_markup()
        await callback_query.message.answer(text=Messages.INPUT_SENDING_MESSAGE)
        await state.set_state(States.sending_message)

    @router.message(States.sending_ids)
    async def handle_ids_message(message: types.Message, state: FSMContext):
        pattern = r'^-?\d+(?:, -?\d+)*$'
        if not bool(re.match(pattern, message.text)):
            await message.reply(text=Messages.ERROR_IDS_FORMAT)
            await state.set_state(States.sending_ids)
            return

        await state.update_data(sending_ids=message.text)
        await message.answer(text=Messages.INPUT_SENDING_MESSAGE)
        await state.set_state(States.sending_message)

    @router.message(States.sending_message)
    async def handle_sending_message(message: types.Message, state: FSMContext):
        text = message.text

        if len(text) < 30:
            await message.reply(text=Messages.ERROR_MESSAGE_LENGTH)
            await state.set_state(States.sending_message)
            return

        await state.update_data(sending_message=text)
        data = await state.get_data()

        sending_type = data.get("sending_type", CallbackDataSimple.RECEIVE_ALL_USERS)
        sending_ids = data.get("sending_ids", None)
        sending_type_map = {
            CallbackDataSimple.RECEIVE_ALL_USERS: "всем пользователям",
            CallbackDataSimple.RECEIVE_ONLY_ME: "только мне"
        }
        result_text = (f"<b>Тип отклика:</b> {sending_type_map[sending_type]}\n"
                       f"<b>Чаты:</b> {sending_ids if sending_ids is not None else "во все чаты"}\n"
                       f"<b>Сообщение:</b> {message.text}\n"
                       f"Если нужно что-то изменить, то заполните рассылку заново /sending")

        inline_keyboard = [[InlineKeyboardButton(text="Начать рассылку", callback_data=CallbackDataSimple.START_SENDING)]]
        await state.update_data(sending_message=message.text)

        await message.answer(
            text=result_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_keyboard),
            parse_mode=ParseMode.HTML
        )

    @router.callback_query(F.data == CallbackDataSimple.START_SENDING)
    async def handle_start_sending(callback_query: types.CallbackQuery, state: FSMContext):
        await callback_query.message.delete_reply_markup()

        data = await state.get_data()
        sending_ids = data.get("sending_ids", None)
        sending_message: str | None = data.get("sending_message", None)
        sending_type = data.get("sending_type", None)

        if not sending_message or not sending_type:
            await callback_query.message.answer(text="Ошибка сценария, попробуйте заново")
            return

        if sending_ids is None:
            chats = get_chats()
            ids = [int(chat["chat_id"]) for chat in chats]
        else:
            ids = [int(x) for x in re.findall(r'-?\d+', sending_ids)]

        await send_request_in_chats(ids, sending_message, callback_query, sending_type)

    async def send_request_in_chats(ids: list[int], message: str, callback_query: types.CallbackQuery, sending_type):
        inline_keyboard = [
            [
                InlineKeyboardButton(
                    text="Мне интересно",
                    callback_data=RespondCallback(type=sending_type, user_id=callback_query.from_user.id).pack()
                )
            ],
        ]
        for idt in ids:
            try:
                await bot.send_message(
                    text=message,
                    chat_id=idt,
                    reply_markup=InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
                )
                await asyncio.sleep(0.3)
            except Exception as e:
                await callback_query.message.reply(f"Ошибка: {e}")


    dp.include_router(router)