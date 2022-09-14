import datetime
import typing

from app.store.tg_api.api import TgClient
from app.store.tg_api.dataclasses import UpdateObj
from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.exc import IntegrityError

if typing.TYPE_CHECKING:
    from app.web.app import Application


class BotManager:
    def __init__(self, app: "Application"):
        self.app = app
        self.tg_client = TgClient(app.config.bot.access_token)

    async def handle_update(self, upd: UpdateObj):
        print(upd)
        if upd.my_chat_member and upd.my_chat_member.new_chat_member.user.id == self.app.config.bot.id:
            status = upd.my_chat_member.new_chat_member.status
            match status:
                case "member":
                    # TODO вывести кнопку старт с чате с информационным сообщением
                    # reply_keyboard = [['/start']]
                    # markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=False, resize_keyboard=True)
                    # ib = [InlineKeyboardButton("Yes", callback_data="cb_yes"), InlineKeyboardButton("No", callback_data="cb_no")]

                    # start_bt = [InlineKeyboardButton("СТАРТ", callback_data="/start")]
                    # inline = InlineKeyboardMarkup(inline_keyboard=[start_bt])

                    text = f"Привет! Я игровой бот 'Умники и умницы'. Если хотите начать игру нажмите СТАРТ"

                    start_btn = [InlineKeyboardButton("СТАРТ", callback_data="/start")]
                    inline_kb = InlineKeyboardMarkup(inline_keyboard=[start_btn])

                    # text = f"Привет! Я игровой бот 'Умники и умницы'. Если хотите начать игру нажмите СТАРТ"
                    # reply_btn = [['/start']]
                    # markup = ReplyKeyboardMarkup(reply_btn, one_time_keyboard=False, resize_keyboard=True)

                    answer = await self.tg_client.send_message(upd.my_chat_member.chat.id, text=text,
                                                               reply_markup=inline_kb)
                case "left":
                    print("left from chat")
                    # TODO завершить игровую сессию: изменить статус игровой сессии и проставить статы в игр. прогрессе
        if upd.callback_query is not None:
            chat_id = upd.callback_query.message.chat.id
            tg_user_id = upd.callback_query.from_.id
            user_name = upd.callback_query.from_.username
            text_msg = upd.callback_query.message.text
            data = upd.callback_query.data


            if data == "/start":
                await self.start_game(chat_id=chat_id, tg_user_id=tg_user_id, user_name=user_name)
                await self.tg_client.delete_message(chat_id, upd.callback_query.message.message_id)

            if "Укажите игровое время" in text_msg:

                if int(data) != self.app.config.game.time_for_game:
                    try:
                        await self.app.store.game.update_gs_duration(chat_id=chat_id, time_for_game=int(data))
                    except IntegrityError as e:
                        pass

                text = f" Укажите время на ответ"
                time_for_answer_btn = [InlineKeyboardButton("10 с", callback_data=10),
                                       InlineKeyboardButton("15 с", callback_data=15),
                                       InlineKeyboardButton("30 с", callback_data=30)]

                inline = InlineKeyboardMarkup(inline_keyboard=[time_for_answer_btn])
                answer = await self.tg_client.raw_send_message(chat_id=chat_id, text=text, reply_markup=inline)




        if upd.message.text == '/start':
            chat_id = upd.message.chat.id
            tg_user_id = upd.message.from_.id
            user_name = upd.message.from_.username
            await self.start_game(chat_id=chat_id, tg_user_id=tg_user_id, user_name=user_name)



    async def start_game(self, chat_id: int, tg_user_id: int, user_name: str):
        # проверяем есть ли активная игра в данном чате
        gs_active = await self.app.store.game.get_gs_by_chat_id(chat_id)
        # если есть, то отправляем сообщение в чат
        if gs_active:
            await self.tg_client.send_message(chat_id=chat_id, text="Эй! Игра в самом разгаре, нельзя начать новую")
        # если нет, то создаем игрока в БД, если такой игрок уже есть, то запрашиваем его по tg_id
        # создаем игровую сессию в БД (активную) и процесс игры, указываем пользователя, который нажал
        # старт как game_master (is_master) игрового процесса в этой игровой сессии
        # и просим game master-а указать некоторые параметры игры
        else:
            try:
                gamer = await self.app.store.game.create_gamer(tg_user_id, user_name)
            except IntegrityError as e:
                match e.orig.pgcode:
                    case '23505':
                        gamer = await self.app.store.game.get_gamer_by_id_tguser(tg_user_id)
            # создание GameSession & GameProgress
            gs = await self.app.store.game.create_game_session(chat_id=chat_id)
            gp = await self.app.store.game.create_game_progress(gamer.id, gs.id, is_master=True)
            # просим указать сколько минут продлиться игра, а также назначенного game-master_а
            text = f"Пользователь {user_name} теперь game-master. Ему предстоит сделать пару настроек." \
                   f" Укажите игровое время"
            time_for_game_btn = [InlineKeyboardButton("3 мин", callback_data=3),
                                 InlineKeyboardButton("5 мин", callback_data=5),
                                 InlineKeyboardButton("10 мин", callback_data=10)]

            inline = InlineKeyboardMarkup(inline_keyboard=[time_for_game_btn])
            answer = await self.tg_client.raw_send_message(chat_id=chat_id, text=text, reply_markup=inline)
