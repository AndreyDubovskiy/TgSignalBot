import markups
from states.template.UserState import UserState
from states.template.Response import Response
import config_controller

class SwitchWhitelistState(UserState):
    async def start_msg(self):
        config_controller.IS_WHITELIST = not config_controller.IS_WHITELIST
        await config_controller.write_ini()
        if config_controller.IS_WHITELIST:
            return Response(text="Білий список: ВКЛ", redirect="/intro")
        else:
            return Response(text="Білий список: ВИКЛ", redirect="/intro")
