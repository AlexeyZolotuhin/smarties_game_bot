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
                    reply_btn = [['/start']]
                    markup = ReplyKeyboardMarkup(reply_btn, one_time_keyboard=False, resize_keyboard=True)

                    answer = await self.tg_client.send_message(upd.my_chat_member.chat.id, text=text, reply_markup=markup)

                case "left":
                    print("left from chat")
                    # TODO завершить игровую сессию: изменить статус игровой сессии и проставить статы в игр. прогрессе
        if upd.message.text == '/start':
            chat_id = upd.message.chat.id
            gs_active = await self.app.store.game.get_gs_by_chat_id(chat_id)
            print("eeeeeee")
            if gs_active:
                await self.tg_client.send_message(chat_id=chat_id, text="Эй! Игра в самом разгаре, нельзя начать новую")
            else:
                try:
                    gamer = await self.app.store.game.create_gamer(upd.message.from_.id, upd.message.from_.username)
                except IntegrityError as e:
                    match e.orig.pgcode:
                        case '23505':
                            gamer = await self.app.store.game.get_gamer_by_id_tguser(upd.message.from_.id)

                gs = await self.app.store.game.create_game_session(upd.message.chat.id)
                gp = await self.app.store.game.create_game_progress(gamer.id, gs.id, is_master=True)

                text = f"Укажите игровое время в минутах"
                time_for_game_btn = [InlineKeyboardButton("3 мин", callback_data=3),
                                InlineKeyboardButton("5 мин", callback_data=5),
                                InlineKeyboardButton("10 мин", callback_data=10)]

                inline = InlineKeyboardMarkup(inline_keyboard=[time_for_game_btn])

                # reply_btn = [['/3'], ['/5'], ['/10']]
                # markup = ReplyKeyboardMarkup(reply_btn, one_time_keyboard=False, resize_keyboard=True)

                answer = await self.tg_client.raw_send_message(upd.message.chat.id, text=text, reply_markup=inline)
                print(answer)

