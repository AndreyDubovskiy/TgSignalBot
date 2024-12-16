import sys
import config_controller
from telebot.async_telebot import AsyncTeleBot
from telebot import types
from states.template.BuilderState import BuilderState
from states.template.UserState import UserState
from states.template.Response import Response
from utils.SenderSignal import SenderSignal
import os


tokkey = os.environ.get('BOT_TOKEN')

bot = AsyncTeleBot(tokkey)

state_list = {}

@bot.message_handler(commands=['off'])
async def off(message):
    await bot.send_message(chat_id=message.chat.id, text="Вимикаю...")
    sys.exit()

@bot.message_handler(commands=['del_log'])
async def off(message):
    tmp = os.listdir("./logger/log")
    for i in tmp:
        os.remove(f"./logger/log/{i}")
    await bot.send_message(chat_id=message.chat.id, text="Deleted logs")


@bot.message_handler(commands=['get_log'])
async def off(message):
    filename = message.text.split("/get_log ")[-1]
    with open("./logger/log/"+filename, "rb") as file:
        await bot.send_document(chat_id=message.chat.id, document=file)

@bot.message_handler(commands=['list_log'])
async def off(message):
    tmp = os.listdir("./logger/log")
    with open("testlog.txt", "w") as file:
        for i in tmp:
            file.write(i+"\n")

    with open("testlog.txt", "rb") as file:
        await bot.send_document(chat_id=message.chat.id, document=file)


@bot.message_handler(commands=['passwordadmin','help', 'passwordmoder', 'helpadmin', 'log', 'textafter', 'start', 'texthelp', 'texthello', 'textcontact','menu'])
async def passwordadmin(message):
    await handle_message(message)

@bot.callback_query_handler(func= lambda call: True)
async def callback(call: types.CallbackQuery):
    user_id = str(call.from_user.id)
    chat_id = str(call.message.chat.id)
    try:
        user_name = str(call.from_user.username)
    except:
        user_name = None
    text = call.data
    id_list = user_id+chat_id
    if state_list.get(id_list, None) != None:
        state: UserState = state_list[id_list]
        res: Response = await state.next_btn_clk(text)
        await chek_response(chat_id, user_id, id_list, res, user_name, call.message)
    else:
        builder = BuilderState(bot)
        if not text.startswith("/geturl"):
            state = builder.create_state(text, user_id, chat_id, bot, user_name, call.message)
        else:
            state = builder.create_state("/geturl", user_id, chat_id, bot, user_name, call.message)
        state_list[id_list] = state
        if not text.startswith("/geturl"):
            state.message_obj = call.message
            res: Response = await state.start_msg()
            await chek_response(chat_id, user_id, id_list, res, user_name, call.message)
        else:
            state.message_obj = call.message
            res: Response = await state.next_btn_clk_message(text, call.message)
            await chek_response(chat_id, user_id, id_list, res, user_name, call.message)
    if not text.startswith("/geturl"):
        await bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)


@bot.message_handler(func=lambda message: True, content_types=['text'])
async def comand(message: types.Message):
    await handle_message(message)
@bot.message_handler(func=lambda message: True, content_types=["photo", "video"])
async def comand(message: types.Message):
    user_id = str(message.from_user.id)
    user_chat_id = str(message.chat.id)
    try:
        user_name = str(message.from_user.username)
    except:
        user_name = None
    id_list = user_id + user_chat_id
    if state_list.get(id_list, None) == None:
        builder = BuilderState(bot)
        state = builder.create_state("photo", user_id, user_chat_id, bot, user_name, message)
        state_list[id_list] = state
        res: Response = await state.start_msg()
        await chek_response(user_chat_id, user_id, id_list, res, user_name, message)
    else:
        state: UserState = state_list[id_list]
        state.message_obj = message
        res: Response = await state.next_msg_photo_and_video(message)
        await chek_response(user_chat_id, user_id, id_list, res, user_name, message)


@bot.message_handler(func=lambda message: True, content_types=["document"])
async def comand(message: types.Message):
    user_id = str(message.from_user.id)
    user_chat_id = str(message.chat.id)
    try:
        user_name = str(message.from_user.username)
    except:
        user_name = None
    id_list = user_id + user_chat_id
    if state_list.get(id_list, None) == None:
        return
    else:
        state: UserState = state_list[id_list]
        state.message_obj = message
        res: Response = await state.next_msg_document(message)
        await chek_response(user_chat_id, user_id, id_list, res, user_name, message)

async def chek_response(user_chat_id, user_id, id_list, res: Response = None, user_name: str = None, message: types.Message = None):
    tmp_state = state_list.get(id_list)
    task_as = None
    if res != None:
        await res.send(user_chat_id, bot)
        if res.is_end:
            state_list.pop(id_list)
        if res.async_end:
            task_as = asyncio.create_task(tmp_state.async_work())
        if res.redirect != None:
            builder = BuilderState(bot)
            state = builder.create_state(res.redirect, user_id, user_chat_id, bot, user_name, message)
            state_list[id_list] = state
            res: Response = await state.start_msg()
            await chek_response(user_chat_id, user_id, id_list, res, user_name, message)
        if res.async_end:
            await task_as
    else:
        state_list.pop(id_list)
async def handle_message(message: types.Message):
    user_id = str(message.from_user.id)
    user_chat_id = str(message.chat.id)
    try:
        user_name = str(message.from_user.username)
    except:
        user_name = None
    id_list = user_id+user_chat_id
    text = message.text
    if state_list.get(id_list, None) == None:
        builder = BuilderState(bot)
        state = builder.create_state(text, user_id, user_chat_id, bot, user_name, message)
        state_list[id_list] = state
        res: Response = await state.start_msg()
        await chek_response(user_chat_id, user_id, id_list, res, user_name, message)
    else:
        state: UserState = state_list[id_list]
        state.message_obj = message
        res: Response = await state.next_msg(text)
        await chek_response(user_chat_id, user_id, id_list, res, user_name, message)

import utils.AsyncTasks as tasks

tasks.bot = bot

import asyncio

sender_signal = SenderSignal(bot=bot)

async def sender_time():
    global sender_signal
    while True:
        await sender_signal.tick()
        await asyncio.sleep(60)

async def start_main():
    task1 = asyncio.create_task(bot.polling(non_stop=True))
    task2 = asyncio.create_task(config_controller.preload_config())
    task4 = asyncio.create_task(config_controller.preload_list_posts())
    task3 = asyncio.create_task(sender_time())
    task5 = asyncio.create_task(tasks.one_minute())
    await task1
    await task2
    await task3
    await task4
    await task5

asyncio.run(start_main())






