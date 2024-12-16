from db.controllers.UserVsController import UserVsController
import config_controller

uservs_controller = UserVsController()


async def is_whitelist(tg_name: str, tg_id: str = None) -> bool:
    if not config_controller.IS_WHITELIST:
        return True
    if tg_id is not None:
        if tg_id in config_controller.list_is_loggin_admins:
            return True
    tmp = await uservs_controller.get_by(tg_name=tg_name)
    return len(tmp) > 0
