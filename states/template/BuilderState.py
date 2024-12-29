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
from states.admin.SwitchWhitelistState import SwitchWhitelistState
from states.admin.AddUserState import AddUserState
from states.admin.DelUserState import DelUserState
from states.admin.AfterSigState import AfterSigState
from states.admin.IsAfterSigState import IsAfterSigState


class BuilderState:
    def __init__(self, bot: AsyncTeleBot):
        self.bot = bot

    def create_state(self, data_txt: str, user_id: str, user_chat_id: str, bot: AsyncTeleBot, user_name: str = None, message: types.Message = None) -> UserState:
        defoult = ErrorState
        clssses = {
            "/intro": MenuState,
            "/menu": MenuUserState,
            "/passwordadmin": ChangeAdminState,
            "Змінити пароль адміна": ChangeAdminState,
            "/log": LogState,
            "/start": StartState,
            "/subscribes_list": SybscribeState,
            "💰 МОЇ ПІДПИСКИ 💰": SybscribeState,
            "/postlist": PostState,
            "Список постів": PostState,
            "/whitelist": SwitchWhitelistState,
            "Білий список: ВКЛ": SwitchWhitelistState,
            "Білий список: ВИКЛ": SwitchWhitelistState,
            "/add_whitelist": AddUserState,
            "Додати в білий список": AddUserState,
            "/delete_whitelist": DelUserState,
            "Видалити з білого списку": DelUserState,
            "/after_signal": AfterSigState,
            "Змінити текст після сигналу": AfterSigState,
            "/is_after_signal": IsAfterSigState,
            "Текст після сигналу: ВКЛ": IsAfterSigState,
            "Текст після сигналу: ВИКЛ": IsAfterSigState,
        }
        if data_txt in clssses:
            return clssses[data_txt](user_id, user_chat_id, bot, user_name, message)
        else:
            return defoult(user_id, user_chat_id, bot, user_name, message)