import markups
from states.template.UserState import UserState
from states.template.Response import Response
import config_controller

class IsAfterSigState(UserState):
    async def start_msg(self):
        config_controller.IS_AFTER_SIGNAL = not config_controller.IS_AFTER_SIGNAL
        await config_controller.write_ini()

        if config_controller.IS_AFTER_SIGNAL:
            return Response(text="Текст після сигналів: ВКЛ", redirect="/intro")
        else:
            return Response(text="Текст після сигналів: ВИКЛ", redirect="/intro")
