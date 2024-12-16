import markups
from states.template.UserState import UserState
from states.template.Response import Response
from db.controllers.UserVsController import UserVsController
import config_controller

class AddUserState(UserState):
    async def start_msg(self):
        self.uservs_controller = UserVsController()
        return Response(text="Введіть нікнейм користувача, якому хочете дозволити доступ:\n\n"
                             "Можете ввести зразу декілька нікнеймів, кожен з нового рядка", buttons=markups.generate_cancel())

    async def next_msg(self, message: str):
        list_users = message.replace("@", "").split("\n")
        for user in list_users:
            tmp = await self.uservs_controller.get_by(tg_name=user)
            if len(tmp) == 0:
                await self.uservs_controller.create(tg_name=user)
        return Response(text=f"Додано {len(list_users)} користувачів", redirect="/intro")

    async def next_btn_clk(self, data_btn: str):
        if data_btn == "/cancel":
            return Response(redirect="/intro")