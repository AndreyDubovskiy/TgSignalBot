import markups
from states.template.UserState import UserState
from states.template.Response import Response
import config_controller

class ErrorState(UserState):
    async def start_msg(self):
        return Response(text="Помилка! Ви ввели щось невірно...", is_end=True)