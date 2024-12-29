import pickle
import os
from db.controllers.ConfigsController import ConfigsController
controller = ConfigsController()
PASSWORD_ADMIN = "admin"
IS_WHITELIST = False

TOKEN_BOT = os.environ.get('BOT_TOKEN')


AFTER_SIGNAL_TEXT = "TestText"
IS_AFTER_SIGNAL = False

LIST_POSTS = {}
# {"name":{"text": str,
#          "urls": [str],
#          "photos": [str],
#           "videos": [str]
#          }}


list_is_loggin_admins = []

async def preload_config():
    resp = await controller.get_config(name="config")
    if resp.binary_data != None:
        await read_ini()
    else:
        await write_ini()
async def write_ini():
    config = {}
    config["PASSWORD_ADMIN"] = PASSWORD_ADMIN
    config["IS_WHITELIST"] = IS_WHITELIST
    config["AFTER_SIGNAL_TEXT"] = AFTER_SIGNAL_TEXT
    config["IS_AFTER_SIGNAL"] = IS_AFTER_SIGNAL
    await controller.set_config(name="config",
                          binary_data=pickle.dumps(config))


async def read_ini():
    global PASSWORD_ADMIN, IS_WHITELIST, AFTER_SIGNAL_TEXT, IS_AFTER_SIGNAL
    config = pickle.loads((await controller.get_config(name="config")).binary_data)
    PASSWORD_ADMIN = str(config["PASSWORD_ADMIN"])
    try:
        IS_WHITELIST = bool(config["IS_WHITELIST"])
    except Exception as ex:
        IS_WHITELIST = False
    try:
        AFTER_SIGNAL_TEXT = str(config["AFTER_SIGNAL_TEXT"])
    except Exception as ex:
        AFTER_SIGNAL_TEXT = "TestText"
    try:
        IS_AFTER_SIGNAL = bool(config["IS_AFTER_SIGNAL"])
    except Exception as ex:
        IS_AFTER_SIGNAL = False

async def preload_list_posts():
    resp = await controller.get_config(name="list_posts")
    if resp.binary_data != None:
        await read_list_posts()
    else:
        await write_list_posts()

async def write_list_posts():
    await controller.set_config(name="list_posts",
                          binary_data=pickle.dumps(LIST_POSTS))

async def read_list_posts():
    global LIST_POSTS
    LIST_POSTS = pickle.loads((await controller.get_config(name="list_posts")).binary_data)

def log(chat_id, password):
    global list_is_loggin_admins
    if password == PASSWORD_ADMIN and (not chat_id in list_is_loggin_admins):
        list_is_loggin_admins.append(chat_id)
        return True
    elif chat_id in list_is_loggin_admins:
        return True
    return False

async def change_password_admin(chat_id, password):
    global PASSWORD_ADMIN, list_is_loggin_admins
    if chat_id in list_is_loggin_admins:
        PASSWORD_ADMIN = password
        await write_ini()
        list_is_loggin_admins = []
        return True
    else:
        return False


async def del_post(key):
    global LIST_POSTS
    if LIST_POSTS.get(key, None) != None:
        if LIST_POSTS[key]['photos'] != None:
            for i in LIST_POSTS[key]['photos']:
                try:
                    os.remove(i)
                except Exception as ex:
                    pass
        if LIST_POSTS[key]['videos'] != None:
            for i in LIST_POSTS[key]['videos']:
                try:
                    os.remove(i)
                except Exception as ex:
                    pass
        LIST_POSTS.__delitem__(key)
        await write_list_posts()
        return True
    else:
        return False

def is_id_post(id:int):
    for i in LIST_POSTS:
        if LIST_POSTS[i]['id'] == id:
            return False
    return True

def get_id_post():
    id = 0
    while(not is_id_post(id)):
        id+=1
    return id


async def add_or_edit_post(key: str, text: str = None, urls: list = None, photos: list = None, videos: list = None):
    global LIST_POSTS
    try:
        v_key = key
        v_text = text
        v_urls = urls
        v_photos = photos
        v_videos = videos
        id = get_id_post()
        LIST_POSTS[v_key] = {'text': v_text,
                                 'urls': v_urls,
                             'photos': v_photos,
                             'videos': v_videos,
                             'id': id}
        await write_list_posts()
        return True
    except Exception as ex:
        print(ex)
        return False