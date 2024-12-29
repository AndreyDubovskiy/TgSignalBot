import markups
from states.template.UserState import UserState
from states.template.Response import Response
import config_controller

class StartState(UserState):
    async def start_msg(self):
        return Response(text="Вітаю у боті!\n"
                             "/menu - для доступу до функцій\n"
                             "Або ж кнопки, які з'явилися знизу", buttons=markups.generate_markup_menu_user(), is_end=True)