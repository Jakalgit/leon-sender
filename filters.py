from aiogram.filters import BaseFilter
from aiogram import types
from aiogram.fsm.context import FSMContext

from config import Config


class UserFilter(BaseFilter):

    def __init__(self):
        pass

    async def __call__(self, obj: types.Update, state: FSMContext):
        if isinstance(obj, types.Message) or isinstance(obj, types.CallbackQuery):
            user_id = obj.from_user.id

            return user_id in Config.USER_IDS