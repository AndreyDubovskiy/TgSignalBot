import asyncio
import datetime

from states.template.UserState import UserState
from states.template.Response import Response
from telebot.async_telebot import AsyncTeleBot
from telebot import types
import markups
import config_controller
from logger.MyLogger import Logger
import utils.AsyncTasks as tasks

from db.controllers.UsersController import UsersController
from db.controllers.SubscribesController import SubscribesController

class PostState(UserState):
    def __init__(self, user_id: str, user_chat_id: str, bot: AsyncTeleBot, user_name, message):
        super().__init__(user_id, user_chat_id, bot, user_name, message)
        self.user_controller = UsersController()
        self.subscribe_controller = SubscribesController()
        self.logger = Logger(filename="PostState")
        self.current_page = 0
        self.max_on_page = 5
        self.edit = None
        self.current_name = None
        self.newname = None
        self.newurls = None
        self.newphotos = None
        self.newvideos = None
        self.newtext = None
    async def start_msg(self):
        if self.user_id in config_controller.list_is_loggin_admins:
            return Response(text="Список постів", buttons=markups.generate_post_menu(self.current_page, self.max_on_page))
        else:
            return Response(text="У вас недостатньо прав!", is_end=True)

    async def next_msg(self, message: str):
        if not (self.user_id in config_controller.list_is_loggin_admins):
            return Response(text="У вас недостатньо прав!", is_end=True)
        if self.edit == "addname":
            self.newname = message
            self.edit = "addpost"
            return Response(text="Відправте пост одним повідомленням (можна з фото або відео, та текстом, але одним повідомленням):")
        elif self.edit == "addpost":
            self.newtext = self.message_obj.html_text
            self.edit = "addurls"
            return Response(
                text="Напишіть посилання, які потрібно додати до поста (якщо не одне посилання, то кожне посилання з нового рядка. Але одним повідомленням):", buttons=markups.generate_cancel())
        elif self.edit == "addurls":
            self.newurls = message.split("\n")
            self.edit = None
            if (await config_controller.add_or_edit_post(self.newname, text=self.newtext, urls=self.newurls, photos=self.newphotos, videos=self.newvideos)):
                return Response(text="Успішно додано!", is_end=True, redirect="/postlist")
            else:
                return Response(text="Помилка!", is_end=True, redirect="/postlist")

        elif self.edit == "tasksend":
            try:
                self.edit = None
                if message.count("-") > 0:
                    day = int(message.split(" ")[0].split("-")[0])
                    month = int(message.split(" ")[0].split("-")[1])
                    year = int(message.split(" ")[0].split("-")[2])
                    hour = int(message.split(" ")[1].split(":")[0])
                    minute = int(message.split(" ")[1].split(":")[1])
                else:
                    day = int(message.split(" ")[0].split(".")[0])
                    month = int(message.split(" ")[0].split(".")[1])
                    year = int(message.split(" ")[0].split(".")[2])
                    hour = int(message.split(" ")[1].split(":")[0])
                    minute = int(message.split(" ")[1].split(":")[1])
                date = datetime.datetime(year=year, month=month, day=day, hour=hour, minute=minute)
                tasks.tasks_controller.add_task(date, {"current_name": self.current_name, "user_id": self.user_id})
                return Response(text="Задача на розсилку додана!", is_end=True, redirect="/postlist")
            except Exception as ex:
                self.edit = "tasksend"
                return Response(text="Помилка! Ви ввели щось не так! Спробуйте знову ввести.\nПриклад 22-12-2024 13:45", buttons=markups.generate_cancel())

    async def next_btn_clk(self, data_btn: str):
        if data_btn == "/cancel":
            if self.current_name == None:
                return Response(is_end=True, redirect="/intro")
            else:
                return Response(is_end=True, redirect="/postlist")
        elif data_btn == "/next":
            if len(config_controller.LIST_POSTS)-((self.current_page+1)*self.max_on_page) > 0:
                self.current_page+=1
            return Response(text="Список постів", buttons=markups.generate_post_menu(self.current_page*self.max_on_page, self.max_on_page))
        elif data_btn =="/prev":
            if self.current_page > 0:
                self.current_page-=1
            return Response(text="Список постів", buttons=markups.generate_post_menu(self.current_page*self.max_on_page, self.max_on_page))
        elif data_btn in config_controller.LIST_POSTS:
            self.current_name = data_btn
            print(config_controller.LIST_POSTS[self.current_name])
            text = ""
            if config_controller.LIST_POSTS[self.current_name]['photos'] != None:
                text+= "\nКількість прикріплених фото: " + str(len(config_controller.LIST_POSTS[self.current_name]['photos'])) + "\n"
            if config_controller.LIST_POSTS[self.current_name]['videos'] != None:
                text+= "\nКількість прикріплених відео: " + str(len(config_controller.LIST_POSTS[self.current_name]['videos'])) + "\n"
            if config_controller.LIST_POSTS[self.current_name]['text'] != None:
                text+="\nТекст поста:\n" + config_controller.LIST_POSTS[self.current_name]['text']
            return Response(text="Назва поста: " + self.current_name + text, buttons=markups.generate_post_semimenu(), is_html=True)
        elif data_btn == "/add":
            self.edit = "addname"
            return Response(text="Напишіть назву поста наступним повідомленням (для себе, користувачам не надсилається):", buttons=markups.generate_cancel())
        elif data_btn == "/delete":
            if (await config_controller.del_post(self.current_name)):
                return Response(text="Успішно видалено!", is_end=True, redirect="/postlist")
            else:
                return Response(text="Помилка!", is_end=True, redirect="/postlist")
        elif data_btn == "/tasksend":
            self.edit = "tasksend"
            return Response(text="Уведіть наступним повідомленням дату розсилки у форматі дд-мм-рррр гг:хв\nНаприклад 22-12-2024 13:45", buttons=markups.generate_cancel())
        elif data_btn == "/send":
            try:
                list_users = await self.user_controller.get_all()
                count = 0
                error = 0
                deleted_count = 0
                len_users = len(list_users)
                SLEEP_AFTER_SEC = 10
                MAX_COUNT = 50

                file_id = None
                list_file_id = []

                await self.bot.send_message(chat_id=self.user_id, text="Розсилка розпочата, очікуйте повідомлення про закінчення")
                info_msg = await self.bot.send_message(chat_id=self.user_id, text="[Статус розсилки]\nРозіслано людям: "+str(count) + " з "+str(len_users-error) +"\nПомилок: "+str(error))
                for user in list_users:
                    if user.tg_id == self.user_id:
                        continue
                    if count % MAX_COUNT == 0 and count != 0:
                        await self.bot.edit_message_text(chat_id=self.user_id, message_id=info_msg.message_id, text="[Статус розсилки]\nРозіслано людям: "+str(count) + " з "+str(len_users-error) +"\nПомилок: "+str(error))
                        await asyncio.sleep(SLEEP_AFTER_SEC)
                    try:
                        chat_id = user.tg_id
                        text_post = config_controller.LIST_POSTS[self.current_name]['text']
                        list_photos = config_controller.LIST_POSTS[self.current_name]['photos']
                        list_videos = config_controller.LIST_POSTS[self.current_name]['videos']
                        list_urls = config_controller.LIST_POSTS[self.current_name]['urls']
                        markup_tpm = types.InlineKeyboardMarkup(row_width=2)
                        current_url = 0
                        for i in list_urls:
                            markup_tpm.add(types.InlineKeyboardButton(text="Показати посилання", url=i))
                            current_url+=1
                        if list_photos and len(list_photos) == 1 and text_post:
                            if file_id == None:
                                with open(list_photos[0], 'rb') as photo_file:
                                    tmp_msg = await self.bot.send_photo(chat_id=chat_id, photo=photo_file, caption=text_post, reply_markup=markup_tpm, parse_mode="HTML")
                                    file_id = tmp_msg.photo[0].file_id
                            else:
                                await self.bot.send_photo(chat_id=chat_id, photo=file_id, caption=text_post, reply_markup=markup_tpm, parse_mode="HTML")
                        elif list_photos and len(list_photos) == 1:
                            if file_id == None:
                                with open(list_photos[0], 'rb') as photo_file:
                                    tmp_msg = await self.bot.send_photo(chat_id=chat_id, photo=photo_file, reply_markup=markup_tpm)
                                    file_id = tmp_msg.photo[0].file_id
                            else:
                                await self.bot.send_photo(chat_id=chat_id, photo=file_id, reply_markup=markup_tpm)
                        elif list_photos and len(list_photos) > 1 and text_post:
                            if len(list_file_id) == 0:
                                media = []
                                for i in list_photos:
                                    with open(i, 'rb') as photo_file:
                                        media.append(types.InputMediaPhoto(media=photo_file))
                                tmp_msg = await self.bot.send_media_group(chat_id=chat_id, media=media)
                                await self.bot.send_message(chat_id=chat_id, text=text_post, reply_markup=markup_tpm, parse_mode="HTML", disable_web_page_preview=True)
                                for i in tmp_msg:
                                    list_file_id.append(i.photo[0].file_id)
                            else:
                                media = []
                                for i in list_file_id:
                                    media.append(types.InputMediaPhoto(media=file_id))
                                await self.bot.send_media_group(chat_id=chat_id,
                                                           media=media)
                                await self.bot.send_message(chat_id=chat_id,
                                                       text=text_post,
                                                       reply_markup=markup_tpm, parse_mode="HTML", disable_web_page_preview=True)

                        elif list_videos and len(list_videos) == 1 and text_post:
                            if file_id == None:
                                with open(list_videos[0], 'rb') as video_file:
                                    tmp_msg = await self.bot.send_video(chat_id=chat_id, video=video_file, caption=text_post, reply_markup=markup_tpm, parse_mode="HTML")
                                    file_id = tmp_msg.video.file_id
                            else:
                                await self.bot.send_video(chat_id=chat_id, video=file_id, caption=text_post, reply_markup=markup_tpm, parse_mode="HTML")
                        elif list_videos and len(list_videos) == 1:
                            if file_id == None:
                                with open(list_videos[0], 'rb') as video_file:
                                    tmp_msg = await self.bot.send_video(chat_id=chat_id, video=video_file, reply_markup=markup_tpm)
                                    file_id = tmp_msg.video.file_id
                            else:
                                await self.bot.send_video(chat_id=chat_id, video=file_id, reply_markup=markup_tpm)
                        elif text_post:
                            await self.bot.send_message(chat_id=chat_id, text=text_post, reply_markup=markup_tpm, parse_mode="HTML", disable_web_page_preview=True)
                        count+=1
                    except Exception as ex:
                        error+=1
                        self.logger.log("ERROR", ex)
                        try:
                            await self.subscribe_controller.delete_by_user_id(id=user.id)
                            await self.user_controller.delete(id=user.id)
                            deleted_count+=1
                            self.logger.log("INFO", "DELETED USER - "+str(user.id))
                        except Exception as ex1:
                            self.logger.log("ERROR", ex1)
                await self.bot.delete_message(chat_id=self.user_id, message_id=info_msg.message_id)
                return Response(text="Розсилка закінчена!\nРозіслано людям: "+str(count)+"\nПомилок: "+str(error), is_end=True, redirect="/postlist")
            except Exception as ex:
                self.logger.log("FATAL ERROR", ex)
                return Response(text="Помилка!", is_end=True, redirect="/postlist")






    async def next_msg_photo_and_video(self, message: types.Message):
        if self.edit == "addpost":
            self.newtext = self.message_obj.html_caption
            if message.photo:
                self.newphotos = []
                i = message.photo[-1]
                file_info = await self.bot.get_file(i.file_id)
                file_path = file_info.file_path
                bytess = await self.bot.download_file(file_path)
                with open(f'post_tmp/{str(config_controller.get_id_post())}_{i.file_id}.jpg', 'wb') as file:
                    file.write(bytess)
                self.newphotos.append(f'post_tmp/{str(config_controller.get_id_post())}_{i.file_id}.jpg')
            if message.video:
                self.newvideos = []
                i = message.video
                file_info = await self.bot.get_file(i.file_id)
                file_path = file_info.file_path
                bytess = await self.bot.download_file(file_path)
                with open(f'post_tmp/{str(config_controller.get_id_post())}_{i.file_id}.mp4', 'wb') as file:
                    file.write(bytess)
                self.newvideos.append(f'post_tmp/{str(config_controller.get_id_post())}_{i.file_id}.mp4')
            self.edit = "addurls"
            return Response(text="Напишіть посилання, які потрібно додати до поста (якщо не одне посилання, то кожне посилання з нового рядка. Але одним повідомленням):", buttons=markups.generate_cancel())