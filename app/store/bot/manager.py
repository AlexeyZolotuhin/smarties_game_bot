import datetime
import typing

from app.game.models import GameSession
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
            first_name = upd.callback_query.from_.first_name
            text_msg = upd.callback_query.message.text
            data = upd.callback_query.data
            message_id = upd.callback_query.message.message_id

            if data == "/start":
                await self.start_game(chat_id=chat_id, tg_user_id=tg_user_id, first_name=first_name)
                # await self.tg_client.delete_message(chat_id, message_id)
                text = f"Что ж...начнем)"
                edit_m = await self.tg_client.edit_message_text(chat_id=chat_id, message_id=message_id, text=text)

            game_info: GameSession = await self.app.store.game.get_all_gameinfo(chat_id=chat_id)

            if "Укажите игровое время" in text_msg:
                if game_info.game_master.id_tguser == tg_user_id:
                    if int(data) != self.app.config.game.time_for_game:
                        try:
                            await self.app.store.game.update_gs_duration(chat_id=chat_id, time_for_game=int(data))
                        except IntegrityError as e:
                            pass

                    text = f"Установленое игровое время: {data} минут"
                    edit_m = await self.tg_client.edit_message_text(chat_id=chat_id, message_id=message_id, text=text)

                    text = f"Укажите время на ответ"
                    time_for_answer_btn = [InlineKeyboardButton("10 с", callback_data=10),
                                           InlineKeyboardButton("15 с", callback_data=15),
                                           InlineKeyboardButton("30 с", callback_data=30)]

                    inline = InlineKeyboardMarkup(inline_keyboard=[time_for_answer_btn])
                    answer = await self.tg_client.raw_send_message(chat_id=chat_id, text=text, reply_markup=inline)

                else:
                    war_text = f"Ая-я-яй {first_name}! Настройки должен делать game-master {game_info.game_master.first_name}"
                    await self.tg_client.send_message(chat_id=chat_id, text=war_text)

            elif "Укажите время на ответ" in text_msg:
                if game_info.game_master.id_tguser == tg_user_id:
                    if int(data) != self.app.config.game.time_for_answer:
                        try:
                            await self.app.store.game.update_gs_timeout(chat_id=chat_id, time_for_answer=int(data))
                        except IntegrityError as e:
                            pass

                    text = f"Установленое время на ответ: {data} секунд"
                    edit_m = await self.tg_client.edit_message_text(chat_id=chat_id, message_id=message_id, text=text)

                    text = f"Кто хочет принять участие в игре нажмите: Я хочу.\n" \
                           f"Когда все определятся, пусть {game_info.game_master.first_name} нажмет: Мы готовы"

                    who_play_btn = [InlineKeyboardButton("Я хочу", callback_data="Iwant"),
                                    InlineKeyboardButton("Мы готовы", callback_data="WeReady")]

                    inline = InlineKeyboardMarkup(inline_keyboard=[who_play_btn])
                    answer = await self.tg_client.raw_send_message(chat_id=chat_id, text=text, reply_markup=inline)
                else:
                    war_text = f"Ая-я-яй {first_name}! Настройки должен делать game-master {game_info.game_master.first_name}"
                    await self.tg_client.send_message(chat_id=chat_id, text=war_text)

            elif "Кто хочет принять участие" in text_msg:
                if data == "Iwant":
                    if tg_user_id not in [g.gamer.id_tguser for g in game_info.game_progress]:
                        try:
                            gamer = await self.app.store.game.create_gamer(tg_user_id, first_name)
                        except IntegrityError as e:
                            match e.orig.pgcode:
                                case '23505':
                                    gamer = await self.app.store.game.get_gamer_by_id_tguser(tg_user_id)

                        gp = await self.app.store.game.create_game_progress(gamer.id, game_info.id)
                        text = f"{first_name} добавлен!"
                        answer = await self.tg_client.raw_send_message(chat_id=chat_id, text=text)
                    else:
                        text = f"{first_name} не беспокойтесь, вы уже добавлены в игру!"
                        answer = await self.tg_client.raw_send_message(chat_id=chat_id, text=text)
                if data == "WeReady":
                    if game_info.game_master.id_tguser == tg_user_id:
                        res = await self.app.store.game.update_gp_is_answering(
                            is_answering=True,
                            id=game_info.game_progress[0].id
                        )

                        dl = self.app.config.game.difficulty_levels
                        g_str = [f"{gp.gamer.first_name} - {dl[gp.difficulty_level].color}"
                                 for gp in game_info.game_progress]

                        text = f"Каждому игроку случайным образом назначен один из уровней сложности: \n" \
                               f"1 - Зеленая дорожа: 4 вопроса, 2 права на ошибку \n" \
                               f"2 - Желтая дорожка: 3 вопроса, 1 право на ошибку \n" \
                               f"3 - Красная дорожка: 2 вопроса, ошибаться нельзя \n" \
                               f"Побеждает тот, кто первый ответит на 2 вопроса \n\n" \
                               f"Вопросы будут задаваться в следующем порядке: \n" \
                               + '\n'.join(g_str)

                        go_btn = [InlineKeyboardButton("Поехали!", callback_data="Go")]
                        inline = InlineKeyboardMarkup(inline_keyboard=[go_btn])

                        edit_m = await self.tg_client.edit_message_text(chat_id=chat_id, message_id=message_id,
                                                                        text=text, reply_markup=inline)
                    else:
                        war_text = f"Ая-я-яй {first_name}! Настройки должен делать game-master {game_info.game_master.first_name}"
                        await self.tg_client.send_message(chat_id=chat_id, text=war_text)
            elif "Поехали" in text_msg:
                text



        elif upd.message:
            if upd.message.text == '/start':
                chat_id = upd.message.chat.id
                tg_user_id = upd.message.from_.id
                first_name = upd.message.from_.first_name
                await self.start_game(chat_id=chat_id, tg_user_id=tg_user_id, first_name=first_name)

    async def start_game(self, chat_id: int, tg_user_id: int, first_name: str):
        # проверяем есть ли активная игра в данном чате
        gs_active = await self.app.store.game.get_gs_by_chat_id(chat_id)
        # если есть, то отправляем сообщение в чат
        if gs_active:
            await self.tg_client.send_message(chat_id=chat_id, text="Эй! Игра в самом разгаре, нельзя начать новую")
        # если нет, то создаем игрока в БД, если такой игрок уже есть, то запрашиваем его по tg_id
        # создаем игровую сессию в БД (активную) и процесс игры, указываем пользователя, который нажал
        # старт как game_master игровой сессии
        # и просим game master-а указать некоторые параметры игры
        else:
            try:
                gamer = await self.app.store.game.create_gamer(tg_user_id, first_name)
            except IntegrityError as e:
                match e.orig.pgcode:
                    case '23505':
                        gamer = await self.app.store.game.get_gamer_by_id_tguser(tg_user_id)
            except Exception as e:
                print(e)
            # создание GameSession & GameProgress
            gs = await self.app.store.game.create_game_session(chat_id=chat_id, id_game_master=gamer.id)
            gp = await self.app.store.game.create_game_progress(gamer.id, gs.id)
            # просим указать сколько минут продлиться игра, а также назначенного game-master_а
            text = f"Пользователь {first_name} теперь game-master. Ему предстоит сделать пару настроек." \
                   f" Укажите игровое время"
            time_for_game_btn = [InlineKeyboardButton("3 мин", callback_data=3),
                                 InlineKeyboardButton("5 мин", callback_data=5),
                                 InlineKeyboardButton("10 мин", callback_data=10)]

            inline = InlineKeyboardMarkup(inline_keyboard=[time_for_game_btn])
            answer = await self.tg_client.raw_send_message(chat_id=chat_id, text=text, reply_markup=inline)
