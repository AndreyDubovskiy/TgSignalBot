import asyncio
import datetime
import time
import pickle

import markups
import config_controller
from logger.MyLogger import Logger
from telebot.async_telebot import AsyncTeleBot
from telebot import types

from db.controllers.SubscribesController import SubscribesController
from db.controllers.UsersController import UsersController

bot: AsyncTeleBot = None


class Task:
    def __init__(self, date_time, data):
        self.time = date_time
        self.data = data


class AsyncTasksController:
    def __init__(self):
        self.tasks = []
        self.load()

    def save(self):
        with open('tasks.pickle', 'wb') as f:
            pickle.dump(self.tasks, f)

    def load(self):
        try:
            with open('tasks.pickle', 'rb') as f:
                self.tasks = pickle.load(f)
        except Exception as ex:
            self.tasks = []

    def add_task(self, date_time, data):
        self.tasks.append(Task(date_time, data))
        self.save()

    def get_task_by_time_now(self):
        tmp = []
        time_now = datetime.datetime.now() + datetime.timedelta(hours=3)
        for i in self.tasks:
            if time_now >= i.time:
                tmp.append(i)
                self.tasks.remove(i)
        self.save()
        return tmp


tasks_controller = AsyncTasksController()


async def send(current_name, user_id):
    subscribe_controller = SubscribesController()
    user_controller = UsersController()
    try:
        list_users = await user_controller.get_all()
        count = 0
        error = 0
        deleted_count = 0
        len_users = len(list_users)
        SLEEP_AFTER_SEC = 2
        MAX_COUNT = 50
        file_id = None
        list_file_id = []
        for user in list_users:
            if count % MAX_COUNT == 0 and count != 0:
                await asyncio.sleep(SLEEP_AFTER_SEC)
            try:
                chat_id = user.tg_id
                text_post = config_controller.LIST_POSTS[current_name]['text']
                list_photos = config_controller.LIST_POSTS[current_name]['photos']
                list_videos = config_controller.LIST_POSTS[current_name]['videos']
                list_urls = config_controller.LIST_POSTS[current_name]['urls']
                markup_tpm = types.InlineKeyboardMarkup(row_width=2)
                current_url = 0
                for i in list_urls:
                    markup_tpm.add(types.InlineKeyboardButton(text="Показати посилання",
                                                              url=i))
                    current_url += 1
                if list_photos and len(list_photos) == 1 and text_post:
                    if file_id == None:
                        with open(list_photos[0], 'rb') as photo_file:
                            tmp_msg = await bot.send_photo(chat_id=chat_id,
                                                           photo=photo_file,
                                                           caption=text_post,
                                                           reply_markup=markup_tpm,
                                                           parse_mode="HTML",
                                                           )
                            file_id = tmp_msg.photo[0].file_id
                    else:
                        await bot.send_photo(chat_id=chat_id,
                                             photo=file_id,
                                             caption=text_post,
                                             reply_markup=markup_tpm,
                                             parse_mode="HTML",
                                             )
                elif list_photos and len(list_photos) == 1:
                    if file_id == None:
                        with open(list_photos[0], 'rb') as photo_file:
                            tmp_msg = await bot.send_photo(chat_id=chat_id,
                                                           photo=photo_file,
                                                           reply_markup=markup_tpm)
                            file_id = tmp_msg.photo[0].file_id
                    else:
                        await bot.send_photo(chat_id=chat_id,
                                             photo=file_id,
                                             reply_markup=markup_tpm)
                elif list_photos and len(list_photos) > 1 and text_post:
                    if len(list_file_id) == 0:
                        media = []
                        for i in list_photos:
                            with open(i, 'rb') as photo_file:
                                media.append(types.InputMediaPhoto(media=photo_file))
                        tmp_msg = await bot.send_media_group(chat_id=chat_id,
                                                            media=media)
                        for i in tmp_msg:
                            list_file_id.append(i.photo[0].file_id)
                        await bot.send_message(chat_id=chat_id,
                                               text=text_post,
                                               reply_markup=markup_tpm,
                                               parse_mode="HTML",
                                               disable_web_page_preview=True)
                    else:
                        media = []
                        for i in list_file_id:
                            media.append(types.InputMediaPhoto(media=i))
                        await bot.send_media_group(chat_id=chat_id,
                                                    media=media)
                        await bot.send_message(chat_id=chat_id,
                                               text=text_post,
                                               reply_markup=markup_tpm,
                                               parse_mode="HTML",
                                               disable_web_page_preview=True)
                elif list_videos and len(list_videos) == 1 and text_post:
                    if file_id == None:
                        with open(list_videos[0], 'rb') as video_file:
                            tmp_msg = await bot.send_video(chat_id=chat_id,
                                                 video=video_file,
                                                 caption=text_post,
                                                 reply_markup=markup_tpm,
                                                 parse_mode="HTML")
                            file_id = tmp_msg.video.file_id
                    else:
                        await bot.send_video(chat_id=chat_id,
                                             video=file_id,
                                             caption=text_post,
                                             reply_markup=markup_tpm,
                                             parse_mode="HTML")
                elif list_videos and len(list_videos) == 1:
                    if file_id == None:
                        with open(list_videos[0], 'rb') as video_file:
                            tmp_msg = await bot.send_video(chat_id=chat_id,
                                                 video=video_file,
                                                 reply_markup=markup_tpm)
                            file_id = tmp_msg.video.file_id
                    else:
                        await bot.send_video(chat_id=chat_id,
                                             video=file_id,
                                             reply_markup=markup_tpm)
                elif text_post:
                    await bot.send_message(chat_id=chat_id,
                                           text=text_post,
                                           reply_markup=markup_tpm,
                                           parse_mode="HTML",
                                           disable_web_page_preview=True)
                count += 1
            except Exception as ex:
                error += 1
                try:
                    await subscribe_controller.delete_by_user_id(user.id)
                    await user_controller.delete(user.id)
                    deleted_count += 1
                except Exception as ex1:
                    pass
        await bot.send_message(chat_id=user_id,
                               text="Розсилка закінчена!\nРозіслано людям: " + str(count) + "\nПомилок: " + str(error))
    except Exception as ex:
        pass


async def one_minute():
    while True:
        await asyncio.sleep(60)
        tmp = tasks_controller.get_task_by_time_now()
        if len(tmp) > 0:
            for i in tmp:
                await send(i.data['current_name'], i.data['user_id'])

