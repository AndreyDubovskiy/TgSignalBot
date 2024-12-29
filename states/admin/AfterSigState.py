import markups
from states.template.UserState import UserState
from states.template.Response import Response
import config_controller

class AfterSigState(UserState):
    async def start_msg(self):

        return Response(text="Наступним повідомленням введіть новий текст після сигналів:", buttons=markups.generate_cancel())


    async def next_msg(self, message: str):
        config_controller.AFTER_SIGNAL_TEXT = self.message_obj.html_text
        await config_controller.write_ini()

        return Response(text="Текст замінено!", redirect="/intro")


    async def next_btn_clk(self, data_btn: str):
        if data_btn == "cancel":
            return Response(redirect="/intro")
