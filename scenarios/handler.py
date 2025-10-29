from aiogram import Dispatcher, Bot

from . import  chats_listener, start, status, make_sending, respond_handler

def load_handlers(dp: Dispatcher, bot: Bot):
    chats_listener.load_handlers(dp, bot)
    start.load_handlers(dp, bot)
    status.load_handlers(dp, bot)
    make_sending.load_handlers(dp, bot)
    respond_handler.load_handler(dp, bot)