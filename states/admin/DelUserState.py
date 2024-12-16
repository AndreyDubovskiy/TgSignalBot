import markups
from states.template.UserState import UserState
from states.template.Response import Response
from db.controllers.UserVsController import UserVsController
from db.controllers.UsersController import UsersController
from db.controllers.SubscribesController import SubscribesController
import config_controller

class DelUserState(UserState):
    async def start_msg(self):
        self.uservs_controller = UserVsController()
        self.users_controller = UsersController()
        self.subscribe_controller = SubscribesController()
        return Response(text="Введіть нікнейм користувача, якому хочете забрати доступ:\n\n"
                             "Можете ввести зразу декілька нікнеймів, кожен з нового рядка", buttons=markups.generate_cancel())

    async def next_msg(self, message: str):
        list_users = message.replace("@", "").split("\n")
        none_users = []
        count_del = 0
        for user in list_users:
            try:
                tmp = await self.uservs_controller.get_by(tg_name=user)
                if len(tmp) == 0:
                    none_users.append(user)
                else:
                    user_name_tmp = tmp[0].tg_name
                    await self.uservs_controller.delete(tmp[0].id)
                    count_del += 1

                    users = await self.users_controller.get_by(tg_name=user_name_tmp)
                    if len(users) > 0:
                        u = users[0]
                        await self.subscribe_controller.delete_by_user_id(u.id)


            except Exception as ex:
                none_users.append(user)
        return Response(text=f"Видалено {count_del} користувачів\n"
                             f"Не знайдено {len(none_users)} користувачів"f"", redirect="/intro")

    async def next_btn_clk(self, data_btn: str):
        if data_btn == "/cancel":
            return Response(redirect="/intro")