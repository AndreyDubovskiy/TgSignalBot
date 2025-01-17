from telebot import types
import db.database as db
import config_controller
from typing import List


def generate_yes_no():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton(text="✅Так✅", callback_data="/yes"))
    markup.add(types.InlineKeyboardButton(text="❌Відмінити❌", callback_data="/cancel"))
    return markup

def generate_ready_exit():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton(text="✅Готово✅", callback_data="/yes_ready"))
    markup.add(types.InlineKeyboardButton(text="❌Відмінити❌", callback_data="/cancel"))
    return markup

def generate_delete_cancel():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton(text="🗑Видалити🗑", callback_data="/delete"))
    markup.add(types.InlineKeyboardButton(text="❌Відмінити❌", callback_data="/cancel"))
    return markup

def generate_list_acc(accs, page = False):
    markup = types.InlineKeyboardMarkup(row_width=2)
    for i in accs:
        markup.add(types.InlineKeyboardButton(text=i.name+"["+i.phone+"]", callback_data=i.phone))
    if page:
        markup.add(types.InlineKeyboardButton(text="➡️️", callback_data="/next"))
        markup.add(types.InlineKeyboardButton(text="⬅️", callback_data="/back"))
    markup.add(types.InlineKeyboardButton(text="❇️Додати❇️", callback_data="/add"))
    markup.add(types.InlineKeyboardButton(text="❌Відмінити❌", callback_data="/cancel"))
    return markup

def generate_list_subscribes(ar, page = False):
    markup = types.InlineKeyboardMarkup(row_width=2)
    for i in ar:
        markup.add(types.InlineKeyboardButton(text=i.symbol+"["+i.timeframe+"]", callback_data=str(i.id)))
    if page:
        markup.add(types.InlineKeyboardButton(text="➡️️", callback_data="/next"))
        markup.add(types.InlineKeyboardButton(text="⬅️", callback_data="/back"))
    markup.add(types.InlineKeyboardButton(text="❇️Додати❇️", callback_data="/add"))
    markup.add(types.InlineKeyboardButton(text="❌Відмінити❌", callback_data="/cancel"))
    return markup


def generate_cancel():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton(text="❌Відмінити❌", callback_data="/cancel"))
    return markup

def generate_timeframe():
    markup = types.InlineKeyboardMarkup(row_width=2)

    markup.add(types.InlineKeyboardButton(text="1m", callback_data="1m"))
    markup.add(types.InlineKeyboardButton(text="5m", callback_data="5m"))
    markup.add(types.InlineKeyboardButton(text="15m", callback_data="15m"))
    markup.add(types.InlineKeyboardButton(text="30m", callback_data="30m"))
    markup.add(types.InlineKeyboardButton(text="60m", callback_data="60m"))
    markup.add(types.InlineKeyboardButton(text="4h", callback_data="4h"))
    markup.add(types.InlineKeyboardButton(text="1d", callback_data="1d"))
    markup.add(types.InlineKeyboardButton(text="1W", callback_data="1W"))
    markup.add(types.InlineKeyboardButton(text="1M", callback_data="1M"))
    markup.add(types.InlineKeyboardButton(text="❌Відмінити❌", callback_data="/cancel"))

    return markup

def generate_semi_menu_subscribe():
    markup = types.InlineKeyboardMarkup(row_width=2)


    markup.add(types.InlineKeyboardButton(text="🗑Видалити🗑", callback_data="/delete"))
    markup.add(types.InlineKeyboardButton(text="❌Відмінити❌", callback_data="/cancel"))

    return markup

def generate_markup_menu_old():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton(text="💰 МОЇ ПІДПИСКИ 💰", callback_data="/subscribes_list"))
    markup.add(types.InlineKeyboardButton(text="Список постів", callback_data="/postlist"))
    if config_controller.IS_AFTER_SIGNAL:
        markup.add(types.InlineKeyboardButton(text="Текст після сигналу: ВКЛ", callback_data="/is_after_signal"))
        markup.add(types.InlineKeyboardButton(text="Змінити текст після сигналу", callback_data="/after_signal"))
    else:
        markup.add(types.InlineKeyboardButton(text="Текст після сигналу: ВИКЛ", callback_data="/is_after_signal"))
    if config_controller.IS_WHITELIST:
        markup.add(types.InlineKeyboardButton(text="Білий список: ВКЛ", callback_data="/whitelist"))
        markup.add(types.InlineKeyboardButton(text="Додати в білий список", callback_data="/add_whitelist"))
        markup.add(types.InlineKeyboardButton(text="Видалити з білого списку", callback_data="/delete_whitelist"))
    else:
        markup.add(types.InlineKeyboardButton(text="Білий список: ВИКЛ", callback_data="/whitelist"))


    markup.add(types.InlineKeyboardButton(text="Змінити пароль адміна", callback_data="/passwordadmin"))

    return markup

def generate_markup_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton(text="💰 МОЇ ПІДПИСКИ 💰"))
    markup.add(types.KeyboardButton(text="Список постів"))
    if config_controller.IS_AFTER_SIGNAL:
        markup.add(types.KeyboardButton(text="Текст після сигналу: ВКЛ"))
        markup.add(types.KeyboardButton(text="Змінити текст після сигналу"))
    else:
        markup.add(types.KeyboardButton(text="Текст після сигналу: ВИКЛ"))
    if config_controller.IS_WHITELIST:
        markup.add(types.KeyboardButton(text="Білий список: ВКЛ"))
        markup.add(types.KeyboardButton(text="Додати в білий список"))
        markup.add(types.KeyboardButton(text="Видалити з білого списку"))
    else:
        markup.add(types.KeyboardButton(text="Білий список: ВИКЛ"))


    markup.add(types.KeyboardButton(text="Змінити пароль адміна"))

    return markup

def generate_markup_menu_user():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)

    markup.add(types.KeyboardButton(text="💰 МОЇ ПІДПИСКИ 💰"))

    return markup

def generate_post_menu(offset: int=0, max:int = 5):
    if offset > len(config_controller.LIST_POSTS):
        offset = 0
    current_elem = 0
    markup = types.InlineKeyboardMarkup(row_width=2)
    for i in config_controller.LIST_POSTS:
        current_elem+=1
        if current_elem > offset and current_elem-offset <= max:
            markup.add(types.InlineKeyboardButton(text=i, callback_data=i))
        else:
            pass
    if len(config_controller.LIST_POSTS) >= max:
        markup.add(types.InlineKeyboardButton(text="➡️", callback_data="/next"))
        markup.add(types.InlineKeyboardButton(text="⬅️", callback_data="/prev"))
    markup.add(types.InlineKeyboardButton(text="❇️Додати❇️", callback_data="/add"))
    markup.add(types.InlineKeyboardButton(text="❌Відмінити❌", callback_data="/cancel"))
    return markup

def generate_post_semimenu():
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(types.InlineKeyboardButton(text="🗑Видалити🗑", callback_data="/delete"))
    markup.add(types.InlineKeyboardButton(text="Розіслати", callback_data="/send"))
    markup.add(types.InlineKeyboardButton(text="Запланувати розсилку", callback_data="/tasksend"))
    markup.add(types.InlineKeyboardButton(text="❌Відмінити❌", callback_data="/cancel"))
    return markup
