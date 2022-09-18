import asyncio
import random
from datetime import datetime, timedelta
import typing

from app.game.models import GameSession, GameProgress, Gamer
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
        # TODO ограничить использование переменных таймера, обработчик то один
        self.game_start = 0
        self.planning_end_time = 0
        self.time_for_game = 0  # app.config.game.time_for_game
        self.time_for_answer = 0  # app.config.game.time_for_answer
        self.waiting_question = dict()

    async def handle_update(self, upd: UpdateObj, timeout: bool = False):
        print(upd)
        if upd.my_chat_member and upd.my_chat_member.new_chat_member.user.id == self.app.config.bot.id:
            status = upd.my_chat_member.new_chat_member.status
            match status:
                case "member":
                    # TODO вывести кнопку старт с чате с информационным сообщением
                    text = f"Привет! Я игровой бот 'Умники и умницы'. Если хотите начать игру нажмите СТАРТ"

                    start_btn = [InlineKeyboardButton("СТАРТ", callback_data="/start")]
                    inline_kb = InlineKeyboardMarkup(inline_keyboard=[start_btn])

                    answer = await self.tg_client.send_message(upd.my_chat_member.chat.id, text=text,
                                                               reply_markup=inline_kb)
                case "left":
                    print("left from chat")
                    # TODO завершить игровую сессию: изменить статус игровой сессии и проставить статы в игр. прогрессе


        if upd.callback_query:

            chat_id = upd.callback_query.message.chat.id
            tg_user_id = upd.callback_query.from_.id
            first_name = upd.callback_query.from_.first_name
            text_msg = upd.callback_query.message.text
            data = upd.callback_query.data
            message_id = upd.callback_query.message.message_id

            if data == "/start":
                await self.start_game(chat_id=chat_id, tg_user_id=tg_user_id, first_name=first_name)
                text = f"Что ж...начнем)"
                edit_m = await self.tg_client.edit_message_text(chat_id=chat_id, message_id=message_id, text=text)

            game_info: GameSession = await self.app.store.game.get_all_gameinfo(chat_id=chat_id)

            if "Укажите игровое время" in text_msg:
                if game_info.game_master.id_tguser == tg_user_id:
                    if int(data) != self.app.config.game.time_for_game:
                        try:
                            await self.app.store.game.update_gs_duration(chat_id=chat_id, time_for_game=int(data))
                            self.time_for_game = int(data)
                        except IntegrityError as e:
                            pass
                    else:
                        self.time_for_game = self.app.config.game.time_for_game

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
                    answer = await self.tg_client.send_message(chat_id=chat_id, text=war_text)

            elif "Укажите время на ответ" in text_msg:
                if game_info.game_master.id_tguser == tg_user_id:
                    if int(data) != self.app.config.game.time_for_answer:
                        try:
                            await self.app.store.game.update_gs_timeout(chat_id=chat_id, time_for_answer=int(data))
                            self.time_for_answer = int(data)
                        except IntegrityError as e:
                            pass
                    else:
                        self.time_for_answer = self.app.config.game.time_for_answer

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
                    answer = await self.tg_client.send_message(chat_id=chat_id, text=war_text)

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
                        queue_answering = sorted(game_info.game_progress,
                                                 key=lambda gp: (gp.difficulty_level, gp.gamer.first_name))
                        try:
                            res = await self.app.store.game.update_gp_is_answering(
                                is_answering=True,
                                id_=queue_answering[0].id
                            )
                        except Exception as e:
                            print(e)

                        dl = self.app.config.game.difficulty_levels
                        g_str = [f"{gp.gamer.first_name} - {dl[gp.difficulty_level].color}"
                                 for gp in queue_answering]

                        text = f"Каждому игроку случайным образом назначен один из уровней сложности: \n" \
                               f"1 - Зеленая дорожа: 4 вопроса, 2 права на ошибку \n" \
                               f"2 - Желтая дорожка: 3 вопроса, 1 право на ошибку \n" \
                               f"3 - Красная дорожка: 2 вопроса, ошибаться нельзя \n" \
                               f"Побеждает тот, кто первый ответит на 2 вопроса \n" \
                               f"Если игровое время закончится - всем засчитывается проигрыш.\n" \
                               f"Истекает время на ответ - засчитывается неверный ответ.\n\n" \
                               f"Вопросы будут задаваться в следующем порядке: \n" \
                               + '\n'.join(g_str)

                        go_btn = [InlineKeyboardButton("Поехали!", callback_data="Go")]
                        inline = InlineKeyboardMarkup(inline_keyboard=[go_btn])

                        edit_m = await self.tg_client.edit_message_text(chat_id=chat_id, message_id=message_id,
                                                                        text=text, reply_markup=inline)

                    else:
                        war_text = f"Ая-я-яй {first_name}! Настройки должен делать game-master {game_info.game_master.first_name}"
                        answer = await self.tg_client.send_message(chat_id=chat_id, text=war_text)

            elif "Каждому игроку случайным образом" in text_msg:
                if game_info.game_master.id_tguser == tg_user_id:
                    if data == "Go":
                        await self.start_game_timer(game_info.id, game_info.time_for_game, game_info.time_for_answer)

                        queue_answering = sorted(game_info.game_progress,
                                                 key=lambda gp: (gp.difficulty_level, gp.gamer.first_name), )

                        dl = self.app.config.game.difficulty_levels
                        g_str = [f"{gp.gamer.first_name} - {dl[gp.difficulty_level].color}"
                                 for gp in queue_answering]

                        text = f"1 - Зеленая дорожа: 4 вопроса, 2 права на ошибку \n" \
                               f"2 - Желтая дорожка: 3 вопроса, 1 право на ошибку \n" \
                               f"3 - Красная дорожка: 2 вопроса, ошибаться нельзя \n" \
                               f"Побеждает тот, кто первый ответит на 2 вопроса \n" \
                               f"Если игровое время закончится - всем засчитывается проигрыш.\n" \
                               f"Истекает время на ответ - засчитывается неверный ответ.\n\n" \
                               f"Вопросы будут задаваться в следующем порядке:\n" \
                               + '\n'.join(g_str)

                        edit_m = await self.tg_client.edit_message_text(chat_id=chat_id, message_id=message_id,
                                                                        text=text)

                    answering_gp = self.get_answering_gp(game_info.game_progress)

                    await self.make_question(chat_id=chat_id,
                                             answering_gp=answering_gp,
                                             time_for_answer=game_info.time_for_answer,
                                             id_gamesession=game_info.id,
                                             game_info=game_info)

                else:
                    war_text = f"Ая-я-яй {first_name}! Настройки должен делать game-master {game_info.game_master.first_name}"
                    answer = await self.tg_client.send_message(chat_id=chat_id, text=war_text)

            elif "Вопрос" in text_msg:
                is_game_stopped = False
                answering_gp = self.get_answering_gp(game_info.game_progress)

                if answering_gp.gamer.id_tguser == tg_user_id:

                    # находим сообщение на которое отвечаем среди ожидающих и удаляем его из списка waiting_questions
                    self.find_waiting_question(chat_id=chat_id, message_id=message_id)

                    if data == "False":

                        # Увеличиваем количество сделанных ошибок у игрока в GP
                        new_number_of_mistakes = answering_gp.number_of_mistakes + 1
                        await self.app.store.game.update_gp_number_of_mistakes(id_=answering_gp.id,
                                                                               number_of_mistakes=new_number_of_mistakes)

                        # TODO верни таблицу Pathway!
                        # TODO Добавь в config возможные статы игроков и игровой сессии
                        # Проверяем не превышено ли количество ошибок сделанных игроком.
                        # Если да, то меняем стат игрока на проигравшего.
                        # Получаем все игровые процессы (игроков) в состоянии проигравших и смотрим, остался
                        # кто еще из игроков в играющем  состоянии, если таких нет, то останавливаем игру без победителя
                        text_failed = ""
                        if new_number_of_mistakes > self.app.config.game.difficulty_levels[
                            answering_gp.difficulty_level].max_mistakes:
                            text_failed = f"Игрок {answering_gp.gamer.first_name} выходит из игры. \n" \
                                          f"Ты слишком часто ошибался, бро"
                            gp = await self.app.store.game.update_gp_gamer_status(id_=answering_gp.id,
                                                                                  gamer_status="Failed")
                            list_failed_gamers = await self.app.store.game.get_gp_by_id_gs(id_gs=game_info.id,
                                                                                           gamer_status="Failed")

                            # проверяем остался ли кто-нибудь кто еще не проиграл
                            if len(game_info.game_progress) == len(list_failed_gamers) and not is_game_stopped:
                                is_game_stopped = True
                                try:
                                    await self.stop_game(state="All_failed", game_info=game_info, )
                                except Exception as e:
                                    print(e)

                        # Передаем флаг отвечающего следующему в очереди
                        queue_answering = sorted(game_info.game_progress,
                                                 key=lambda gp: (gp.difficulty_level, gp.gamer.first_name), )
                        filtered_queue_answering = list(filter(lambda g: g.gamer_status == "Playing", queue_answering))

                        answering_gp = await self.hand_over_answering_flag(current_ans_gp=answering_gp,
                                                                           list_gp=filtered_queue_answering)

                        # Говорим что ответ неверный, редактируя сообщение с вопросом
                        text = text_msg + f"\nОтвет неверный. " + text_failed + \
                               f"\n\nСледующий игрок: {answering_gp.gamer.first_name}" \
                               f"\nКак будете готовы нажмите:"
                        inline = None
                        if not is_game_stopped:
                            continue_btn = [InlineKeyboardButton("Продолжить", callback_data="Continue")]
                            inline = InlineKeyboardMarkup(inline_keyboard=[continue_btn])
                        else:
                            text = text_msg + f"\nОтвет неверный"

                        edit_m = await self.tg_client.edit_message_text(chat_id=chat_id, message_id=message_id,
                                                                        text=text, reply_markup=inline)

                    elif data == "True":
                        # Увеличиваем количество сделанных правильных ответов у игрока в GP
                        new_number_of_right_answers = answering_gp.number_of_right_answers + 1
                        try:
                            await self.app.store.game.update_gp_number_of_rigth_answers(id_=answering_gp.id,
                                                                                        number_of_right_answers=new_number_of_right_answers)
                        except Exception as e:
                            print(e)

                        # Проверяем количество правильных ответов.
                        # Если да, то меняем стат игрока на победителя и вызываем остановку игры
                        if new_number_of_right_answers >= 2:
                            gp = await self.app.store.game.update_gp_gamer_status(id_=answering_gp.id,
                                                                                  gamer_status="Winner")
                            is_game_stopped = True
                            await self.stop_game(state="Ended", game_info=game_info, winner=answering_gp.gamer)

                        # Передаем флаг отвечающего следующему в очереди
                        queue_answering = sorted(game_info.game_progress,
                                                 key=lambda gp: (gp.difficulty_level, gp.gamer.first_name), )
                        filtered_queue_answering = list(filter(lambda g: g.gamer_status == "Playing", queue_answering))

                        answering_gp = await self.hand_over_answering_flag(current_ans_gp=answering_gp,
                                                                           list_gp=filtered_queue_answering)

                        # Говорим что ответ верный, редактируя сообщение с вопросом
                        text = text_msg + f"\nОтвет верный!" \
                                          f"\n\nСледующий игрок: {answering_gp.gamer.first_name}" \
                                          f"\nКак будете готовы нажмите Продолжить"
                        inline = None
                        if not is_game_stopped:
                            continue_btn = [InlineKeyboardButton("Продолжить", callback_data="Continue")]
                            inline = InlineKeyboardMarkup(inline_keyboard=[continue_btn])
                        else:
                            text = text_msg + f"\nОтвет верный!"

                        edit_m = await self.tg_client.edit_message_text(chat_id=chat_id, message_id=message_id,
                                                                        text=text, reply_markup=inline)

                    elif "Continue" in data:
                        text = text_msg + "\n Ок! Идем дальше."
                        edit_m = await self.tg_client.edit_message_text(chat_id=chat_id, message_id=message_id,
                                                                        text=text)
                        if not is_game_stopped:
                            await self.make_question(chat_id=chat_id,
                                                     answering_gp=answering_gp,
                                                     time_for_answer=game_info.time_for_answer,
                                                     id_gamesession=game_info.id,
                                                     game_info=game_info)

                else:
                    war_text = f"Ая-я-яй {first_name}! Сообщение не для вас."
                    answer = await self.tg_client.send_message(chat_id=chat_id, text=war_text)

        elif upd.message:
            chat_id = upd.message.chat.id
            tg_user_id = upd.message.from_.id
            first_name = upd.message.from_.first_name
            text_msg = upd.message.text
            message_id = upd.message.message_id
            title = upd.message.chat.title if upd.message.chat.title else ""

            if upd.message.text == '/start':
                await self.start_game(chat_id=chat_id, tg_user_id=tg_user_id, first_name=first_name)

            game_info: GameSession = await self.app.store.game.get_all_gameinfo(chat_id=chat_id)

            if text_msg == '/stop':
                # получаем gs по chat_id,
                if not game_info:
                    text = f"Нет активной игровой сессии в текущем чате. Для начала игры нажмите СТАРТ"
                    start_btn = [InlineKeyboardButton("СТАРТ", callback_data="/start")]
                    inline_kb = InlineKeyboardMarkup(inline_keyboard=[start_btn])
                    answer = await self.tg_client.send_message(chat_id, text=text,
                                                               reply_markup=inline_kb)
                else:
                    if game_info.game_master.id_tguser == tg_user_id:
                        # Останавливаем активную игру и переводим ее в состояние Interrupted
                        await self.stop_game(game_info=game_info, state="Interrupted")
                    else:
                        text = f"{first_name}, остановить игру может только game-master"
                        answer = await self.tg_client.send_message(chat_id=chat_id, text=text)
            elif text_msg == "/game_inform":
                if game_info:
                    time_for_game = game_info.time_for_game if \
                        game_info.time_for_game is not None \
                        else "время не задано"

                    time_for_answer = game_info.time_for_answer if \
                        game_info.time_for_answer is not None \
                        else "время не задано"

                    game_start = game_info.game_start.strftime('%Y-%m-%d %H:%M:%S') if \
                        game_info.game_start is not None \
                        else "время не задано"

                    state_game = game_info.state

                    gamers_states = "\n".join([f"{gp.gamer.first_name}: "
                                               f"{self.app.config.game.difficulty_levels[gp.difficulty_level].color}; "
                                               f"статус игрока - {gp.gamer_status}; "
                                               f"правильных ответов - {gp.number_of_right_answers}; "
                                               f"ошибок - {gp.number_of_mistakes}" for gp in game_info.game_progress])

                    text = f"Информация об игре {title}: \n" \
                           f"Время отведенное на игру: {time_for_game} мин. \n" \
                           f"Старт игры: {game_start} \n" \
                           f"Время на ответ {time_for_answer} сек.\n\n" \
                           f"Информация по игрокам: \n" \
                           f"{gamers_states}"

                    answer = await self.tg_client.send_message(tg_user_id, text=text)
                else:
                    text = f"Нет активной игровой сессии в текущем чате. Для начала игры нажмите СТАРТ"
                    start_btn = [InlineKeyboardButton("СТАРТ", callback_data="/start")]
                    inline_kb = InlineKeyboardMarkup(inline_keyboard=[start_btn])
                    answer = await self.tg_client.send_message(chat_id, text=text,
                                                               reply_markup=inline_kb)

            elif text_msg == "/general_rating":
                gamers = await self.app.store.game.list_gamers()
                text = "Список игроков пуст"
                if gamers:
                    gamers_rating = [f"{g.first_name}: "
                                     f"побед - {g.number_of_victories};"
                                     f" поражений - {g.number_of_defeats}" for g in gamers]
                    text = f"Рейтинг игроков: \n\n" + "\n".join(gamers_rating)

                answer = await self.tg_client.send_message(tg_user_id, text=text)

    async def start_game(self, chat_id: int, tg_user_id: int, first_name: str):
        # проверяем есть ли активная игра в данном чате
        gs_active = await self.app.store.game.get_gs_by_chat_id(chat_id)
        # если есть, то отправляем сообщение в чат
        if gs_active:
            answer = await self.tg_client.send_message(chat_id=chat_id,
                                                       text="Эй! Игра в самом разгаре, нельзя начать новую")
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
            # выводим командное меню для получения информации

            reply_keyboard = [['/stop'], ['/game_inform'], ['/general_rating']]
            rk_markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
            text_rk = f"Для вас предоставлено командное меню: \n" \
                      f"/stop - прервать игру. Доступно только для game-master.\n" \
                      f"/game_inform - получить информацию о текущей игре. Присылается в личку.\n" \
                      f"/general_rating - получить общий рейтинг. Присылается в личку."

            answer = await self.tg_client.send_message(chat_id, text=text_rk,
                                                       reply_markup=rk_markup)

            # просим указать сколько минут продлиться игра, а также назначенного game-master_а
            text = f"Пользователь {first_name} теперь game-master. Ему предстоит сделать пару настроек." \
                   f" Укажите игровое время"
            time_for_game_btn = [InlineKeyboardButton("3 мин", callback_data=3),
                                 InlineKeyboardButton("5 мин", callback_data=5),
                                 InlineKeyboardButton("10 мин", callback_data=10)]

            inline = InlineKeyboardMarkup(inline_keyboard=[time_for_game_btn])
            answer = await self.tg_client.raw_send_message(chat_id=chat_id, text=text, reply_markup=inline)

    async def stop_game(self, state: str, game_info: GameSession, winner: Gamer = None):
        # TODO здесь завершаем игровую сессию
        print(f"Stop game: {state}")
        text = ""
        match state:
            case "Ended":
                # В данном состоянии есть победитель, остальных считаем проигравшими.
                # Проставляем в бд всем игрокам в состоянии Playing состояние Failed
                rowcount = await self.app.store.game.update_gp_gamer_status_in_gs(id_gs=game_info.id,
                                                                                  gamer_status="Failed", )
                text = f"У нас есть победитель! И это ... барабанная дробь ... {winner.first_name} \n" \
                       f"Поздравим его!\n\n"
            case "All_failed":
                # В данном состоянии нет победителей. Всем засчитываем проигрыш, чтобы неповадно было
                text = f"К сожалению победителя нет. Все превысили свой лимит ошибок.\n\n"
            case "Interrupted":
                # Игру остановили до логического завершения. Все кто в состоянии Playing переводятся в
                # состояние Interrupted - такие игроки считаются не победителями, не проигравшими.
                # Переводим состояние игроков (game_progress) в статус Interrupted
                rowcount = await self.app.store.game.update_gp_gamer_status_in_gs(id_gs=game_info.id,
                                                                                  gamer_status="Interrupted", )
                text = f"Game-master прервал игру. \n\n"
            case "Timeout":
                # Игровое время вышло. Все проиграли
                text = f"Игровое время вышло. \n\n"
                rowcount = await self.app.store.game.update_gp_gamer_status_in_gs(id_gs=game_info.id,
                                                                                  gamer_status="Failed", )

        # Изменяем в таблице Gamers значения побед / поражений
        game_session = await self.app.store.game.get_gs_by_chat_id(game_info.chat_id)
        if state != "Interrupted":
            for gp in game_session.game_progress:
                if gp.gamer_status == "Failed":
                    new_number_of_defeats = gp.gamer.number_of_defeats + 1
                    await self.app.store.game.update_gamer_defeats(id_=gp.gamer.id,
                                                                   number_of_defeats=new_number_of_defeats)
                if gp.gamer_status == "Winner":
                    new_number_of_victories = gp.gamer.number_of_victories + 1
                    await self.app.store.game.update_gamer_victories(id_=gp.gamer.id,
                                                                     number_of_victories=new_number_of_victories)

        # Изменяем состояние игровой сессии в бд и проставляем время завершения игры
        await self.app.store.game.update_gs_state(id_=game_info.id, state=state)
        await self.app.store.game.update_gs_end_time(id_=game_info.id, game_end=datetime.utcnow())

        text_res = [f"\n{gp.gamer.first_name}: {self.app.config.game.difficulty_levels[gp.difficulty_level].color}, " \
                    f"ответил правильно - {gp.number_of_right_answers}; "
                    f"ошибся - {gp.number_of_mistakes}; статус - {gp.gamer_status}" for gp in
                    game_session.game_progress]

        text = text + f"Результаты игры:" + "\n".join(text_res)
        repeat_btn = [InlineKeyboardButton("Повторить", callback_data="/start")]
        inline = InlineKeyboardMarkup(inline_keyboard=[repeat_btn])
        answer = await self.tg_client.raw_send_message(chat_id=game_session.chat_id, text=text, reply_markup=inline)

    def get_answering_gp(self, game_progresses: list[GameProgress]) -> GameProgress:
        answering_gp = None
        for gp in game_progresses:
            if gp.is_answering:
                answering_gp = gp
                break
        return answering_gp

    async def hand_over_answering_flag(self, current_ans_gp: GameProgress, list_gp: list[GameProgress]):
        if len(list_gp) > 1:
            cur_index = list_gp.index(current_ans_gp)
            next_id_gp = -1
            rowcount = 0  # если нашли следующего игрока в очереди, то = 1
            # Ищем следующего в очереди и проставляем флаг отвечающего ему
            for i in range(cur_index, len(list_gp)):
                if i + 1 < len(list_gp):
                    next_id_gp = list_gp[i + 1].id
                    rowcount = await self.app.store.game.update_gp_is_answering(id_=next_id_gp,
                                                                                is_answering=True,
                                                                                )
                else:
                    next_id_gp = list_gp[0].id
                    rowcount = await self.app.store.game.update_gp_is_answering(id_=next_id_gp,
                                                                                is_answering=True,
                                                                                )
                break

            # Сбрасываем флаг текущего отвечающего игрока если установили флаг следующему в очереди
            # В случае если нет таковых (все в состоянии Failed) то возвращаю текущего отвечающего
            # и флаг не сбрасывается
            # if rowcount != 0:
            await self.app.store.game.update_gp_is_answering(id_=current_ans_gp.id, is_answering=False)
            # else:
            #     return current_ans_gp

            return await self.app.store.game.get_gp_by_id(id_=next_id_gp)
        return current_ans_gp

    async def start_game_timer(self, id_session: int, time_for_game: int, time_for_answer: int):
        self.game_start = datetime.utcnow()

        if self.time_for_answer == 0 or self.time_for_game == 0:
            self.time_for_answer = time_for_answer
            self.time_for_game = time_for_game

        self.planning_end_time = self.game_start + timedelta(minutes=time_for_game)
        try:
            rowcount = await self.app.store.game.update_gs_start_time(game_start=self.game_start, id_=id_session)
        except Exception as e:
            print(e)

        asyncio.create_task(self.game_timer(id_session=id_session, time_for_game=time_for_game))

    async def game_timer(self, id_session: int, time_for_game: int):
        await asyncio.sleep(time_for_game * 60)
        game_session = await self.app.store.game.get_gs_by_id(id_=id_session)
        if game_session:
            if game_session.state == "Active" and not game_session.game_end:
                await self.stop_game(state="Timeout", game_info=game_session)

    async def make_question(self, chat_id: int,
                            answering_gp: GameProgress,
                            game_info: GameSession,
                            time_for_answer: int,
                            id_gamesession: int, ):
        answering_gamer = answering_gp.gamer
        questions = await self.app.store.quizzes.list_questions()
        random_q = random.choice(questions)
        answer_btn = [[InlineKeyboardButton(a.title, callback_data=str(a.is_correct))] for a in random_q.answers]
        inline = InlineKeyboardMarkup(inline_keyboard=answer_btn)
        text_msg = f"Вопрос для {answering_gamer.first_name}: \n" \
                   f"{random_q.title}"

        res = await self.tg_client.raw_send_message(chat_id=chat_id, text=text_msg, reply_markup=inline)
        self.add_waiting_questions(chat_id, res["result"]["message_id"])
        mes_id = res["result"]["message_id"]
        # Запускаем таймер ожидания ответа
        await asyncio.sleep(time_for_answer)
        if mes_id in self.waiting_question.get(chat_id, []):
            # Увеличиваем количество сделанных ошибок у игрока в GP
            new_number_of_mistakes = answering_gp.number_of_mistakes + 1
            await self.app.store.game.update_gp_number_of_mistakes(id_=answering_gp.id,
                                                                   number_of_mistakes=new_number_of_mistakes)
            is_game_stopped = False
            if new_number_of_mistakes > self.app.config.game.difficulty_levels[
                answering_gp.difficulty_level].max_mistakes:
                gp = await self.app.store.game.update_gp_gamer_status(id_=answering_gp.id,
                                                                      gamer_status="Failed")

                list_failed_gamers = await self.app.store.game.get_gp_by_id_gs(id_gs=game_info.id,
                                                                               gamer_status="Failed")
                # проверяем остался ли кто-нибудь кто еще не проиграл
                if len(game_info.game_progress) == len(list_failed_gamers):
                    is_game_stopped = True
                    await self.stop_game(state="All_failed", game_info=game_info)

            # Передаем флаг отвечающего следующему в очереди
            queue_answering = sorted(game_info.game_progress,
                                     key=lambda gp: (gp.difficulty_level, gp.gamer.first_name), )
            filtered_queue_answering = list(filter(lambda g: g.gamer_status == "Playing", queue_answering))

            answering_gp = await self.hand_over_answering_flag(current_ans_gp=answering_gp,
                                                               list_gp=filtered_queue_answering)

            # Говорим что ответ неверный, редактируя сообщение с вопросом
            text = text_msg + f"\nВремя вышло. Ответ засчитан как неверный." \
                              f"\n\nСледующий игрок: {answering_gp.gamer.first_name}" \
                              f"\nКак будете готовы нажмите:"
            inline = None
            if not is_game_stopped:
                continue_btn = [InlineKeyboardButton("Продолжить", callback_data="Continue")]
                inline = InlineKeyboardMarkup(inline_keyboard=[continue_btn])
            else:
                text = text_msg + f"\nВремя вышло. Ответ засчитан как неверный."

            edit_m = await self.tg_client.edit_message_text(chat_id=chat_id,
                                                            message_id=mes_id,
                                                            text=text,
                                                            reply_markup=inline)

    def add_waiting_questions(self, chat_id: int, message_id: int):
        if chat_id not in self.waiting_question:
            self.waiting_question[chat_id] = []

        self.waiting_question[chat_id].append(message_id)

    def find_waiting_question(self, chat_id: int, message_id: int) -> bool:
        list_wm = self.waiting_question.get(chat_id, [])
        if message_id in list_wm:
            indx = list_wm.index(message_id)
            del self.waiting_question[chat_id][indx]
            return True
        return False
