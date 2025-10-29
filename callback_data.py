from aiogram.filters.callback_data import CallbackData


class CallbackDataSimple:
    RECEIVE_ONLY_ME = "RECEIVE_ONLY_ME"
    RECEIVE_ALL_USERS = "RECEIVE_ALL_USERS"

    SEND_IN_ALL = "SEND_IN_ALL"
    SEND_IN_SOME = "SEND_IN_SOME"

    START_SENDING = "START_SENDING"


class RespondCallback(CallbackData, prefix="send"):
    type: str
    user_id: int