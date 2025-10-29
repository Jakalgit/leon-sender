from aiogram.fsm.state import StatesGroup, State


class States(StatesGroup):
    sending_ids = State()
    sending_message = State()