from telebot.async_telebot import AsyncTeleBot
from telebot import types
from states.template.UserState import UserState
from states.admin.MenuState import MenuState
from states.admin.ChangeAdminState import ChangeAdminState
from states.admin.LogState import LogState
from states.user.SubscribeState import SybscribeState
from states.user.ErrorState import ErrorState
from states.user.StartState import StartState
from states.user.MenuUserState import MenuUserState
from states.admin.PostState import PostState

class BuilderState:
    def __init__(self, bot: AsyncTeleBot):
        self.bot = bot

    def create_state(self, data_txt: str, user_id: str, user_chat_id: str, bot: AsyncTeleBot, user_name: str = None, message: types.Message = None) -> UserState:
        defoult = ErrorState
        clssses = {
            "/intro": MenuState,
            "/menu": MenuUserState,
            "/passwordadmin": ChangeAdminState,
            "/log": LogState,
            "/start": StartState,
            "/subscribes_list": SybscribeState,
            "/postlist": PostState
        }
        if data_txt in clssses:
            return clssses[data_txt](user_id, user_chat_id, bot, user_name, message)
        else:
            return defoult(user_id, user_chat_id, bot, user_name, message)