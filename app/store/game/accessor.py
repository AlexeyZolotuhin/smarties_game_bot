from app.game.models import Gamer, GamerModel, GameSessionModel, GameSession, GameProgressModel, \
    GameProgress
from app.base.base_accessor import BaseAccessor
from sqlalchemy import String, and_, delete, or_, select, distinct, update, insert
from sqlalchemy.orm import joinedload, join, aliased
from datetime import datetime, timedelta
import random


class GameAccessor(BaseAccessor):

    # these accessors for PathwayModel aren't using.
    # PathModel was replaced by config path (app.web.config.game.difficulty_levels)
    # cause static data and as result need extra queries

    # Accessor for PathwayModel:

    # async def create_pathway(self, color: str, max_questions: int, max_mistakes: int) -> Pathway:
    #     new_pathway = PathwayModel(color=color, max_questions=max_questions, max_mistakes=max_mistakes)
    #     await self.make_add_query(new_pathway)
    #     return Pathway(id=new_pathway.id,
    #                    color=new_pathway.color,
    #                    max_questions=new_pathway.max_questions,
    #                    max_mistakes=new_pathway.max_mistakes)
    #
    # async def list_pathways(self) -> list[Pathway]:
    #     query = select(PathwayModel)
    #     result = (await self.make_get_query(query)).scalars().unique()
    #
    #     if not result:
    #         return []
    #
    #     return [Pathway(id=p.id,
    #                     color=p.color,
    #                     max_questions=p.max_questions,
    #                     max_mistakes=p.max_mistakes)
    #             for p in result]

    # Accessor for GamerModel:
    async def create_gamer(self, id_tguser: int, first_name: str) -> Gamer:
        new_gamer = GamerModel(id_tguser=id_tguser, first_name=first_name)
        await self.make_add_query(new_gamer)
        return Gamer(id=new_gamer.id,
                     id_tguser=new_gamer.id_tguser,
                     number_of_victories=new_gamer.number_of_victories,
                     number_of_defeats=new_gamer.number_of_defeats,
                     first_name=new_gamer.first_name,
                     )

    async def list_gamers(self) -> list[Gamer]:
        query = select(GamerModel).order_by(GamerModel.number_of_victories.desc())
        result = (await self.make_get_query(query)).scalars().unique()

        if not result:
            return []

        return [Gamer(id=gamer.id,
                      id_tguser=gamer.id_tguser,
                      first_name=gamer.first_name,
                      number_of_victories=gamer.number_of_victories,
                      number_of_defeats=gamer.number_of_defeats,
                      )
                for gamer in result]

    async def get_gamer_by_id(self, id_: int) -> Gamer | None:
        query = select(GamerModel).where(GamerModel.id == id_)
        result = (await self.make_get_query(query)).scalars().first()

        if not result:
            return

        return Gamer(id=result.id,
                     id_tguser=result.id_tguser,
                     first_name=result.first_name,
                     number_of_victories=result.number_of_victories,
                     number_of_defeats=result.number_of_defeats,
                     )

    async def get_gamer_by_id_tguser(self, id_tguser: int) -> Gamer | None:
        query = select(GamerModel).where(GamerModel.id_tguser == id_tguser)
        result = (await self.make_get_query(query)).scalars().first()

        if not result:
            return

        return Gamer(id=result.id,
                     id_tguser=result.id_tguser,
                     first_name=result.first_name,
                     number_of_victories=result.number_of_victories,
                     number_of_defeats=result.number_of_defeats,
                     )

    async def update_gamer_victories(self, id_: int, number_of_victories: int) -> int:
        update_query = update(GamerModel) \
            .where(GamerModel.id == id_) \
            .values(number_of_victories=number_of_victories)
        rowcount = await self.make_update_query(update_query)
        return rowcount

    async def update_gamer_defeats(self, id_: int, number_of_defeats: int) -> Gamer:
        update_query = update(GamerModel) \
            .where(GamerModel.id == id_) \
            .values(number_of_defeats=number_of_defeats)
        rowcount = await self.make_update_query(update_query)
        return rowcount

    # Accessor for GameSessionModel (gs):
    async def create_game_session(self, chat_id: int,
                                  id_game_master: int,
                                  theme_id: int = None,
                                  time_for_game: int = None,
                                  time_for_answer: int = None,
                                  ) -> GameSession:
        if not theme_id:
            theme_id = self.app.config.game.theme_id
        if not time_for_game:
            time_for_game = self.app.config.game.time_for_game
        if not time_for_answer:
            time_for_answer = self.app.config.game.time_for_answer

        new_gs = GameSessionModel(chat_id=chat_id,
                                  theme_id=theme_id,
                                  time_for_game=time_for_game,
                                  time_for_answer=time_for_answer,
                                  id_game_master=id_game_master
                                  # game_end = datetime.utcnow() + timedelta(minutes=20)
                                  )
        try:
            await self.make_add_query(new_gs)
        except Exception as e:
            print(e)

        # async with self.app.database.session.begin() as session:
        #     await session.add(new_gs)
        # await session.commit()

        return GameSession(
            id=new_gs.id,
            chat_id=new_gs.chat_id,
            game_start=new_gs.game_start,
            game_end=new_gs.game_end,
            state=new_gs.state,
            theme_id=new_gs.theme_id,
            time_for_game=new_gs.time_for_game,
            time_for_answer=new_gs.time_for_answer,
            id_game_master=new_gs.id_game_master
        )

    async def get_gs_by_id(self, id_: int) -> GameSession | None:
        query = select(GameSessionModel). \
            where(GameSessionModel.id == id_) \
            .options(joinedload(GameSessionModel.game_progress)
                     .options(joinedload(GameProgressModel.gamer)))

        result = (await self.make_get_query(query)).scalars().first()

        if not result:
            return

        return GameSession(
            id=result.id,
            chat_id=result.chat_id,
            game_start=result.game_start,
            game_end=result.game_end,
            state=result.state,
            theme_id=result.theme_id,
            time_for_game=result.time_for_game,
            time_for_answer=result.time_for_answer,
            id_game_master=result.id_game_master,
            game_progress=[
                GameProgress(
                    id_gamer=gp.id_gamer,
                    difficulty_level=gp.difficulty_level,
                    gamer_status=gp.gamer_status,
                    number_of_mistakes=gp.number_of_mistakes,
                    number_of_right_answers=gp.number_of_right_answers,
                    is_answering=gp.is_answering,
                ) for gp in result.game_progress
            ]
        )

    async def get_gs_by_chat_id(self, chat_id: int, state: str = "Active") -> GameSession | None:
        query = select(GameSessionModel).where(
            and_(
                GameSessionModel.chat_id == chat_id,
                GameSessionModel.state == state,
                GameSessionModel.game_end == None,
            )
        ).options(joinedload(GameSessionModel.game_progress).options(joinedload(GameProgressModel.gamer)))

        try:
            result = (await self.make_get_query(query)).scalars().first()
        except Exception as e:
            print(e)

        if not result:
            return

        return GameSession(
            id=result.id,
            chat_id=result.chat_id,
            game_start=result.game_start,
            game_end=result.game_end,
            state=result.state,
            theme_id=result.theme_id,
            time_for_game=result.time_for_game,
            time_for_answer=result.time_for_answer,
            id_game_master=result.id_game_master,
            game_progress=[
                GameProgress(
                    id=gp.id,
                    id_gamer=gp.id_gamer,
                    id_gamesession=gp.id_gamesession,
                    difficulty_level=gp.difficulty_level,
                    gamer_status=gp.gamer_status,
                    number_of_mistakes=gp.number_of_mistakes,
                    number_of_right_answers=gp.number_of_right_answers,
                    is_answering=gp.is_answering,
                    gamer=Gamer(
                        id=gp.gamer.id,
                        id_tguser=gp.gamer.id_tguser,
                        first_name=gp.gamer.first_name,
                        number_of_defeats=gp.gamer.number_of_defeats,
                        number_of_victories=gp.gamer.number_of_victories,
                    )
                ) for gp in result.game_progress
            ]
        )

    async def get_gs_by_id(self, id_: int) -> GameSession | None:
        query = select(GameSessionModel).where(GameSessionModel.id == id_, ) \
            .options(joinedload(GameSessionModel.game_progress).options(joinedload(GameProgressModel.gamer)))

        try:
            result = (await self.make_get_query(query)).scalars().first()
        except Exception as e:
            print(e)

        if not result:
            return

        return GameSession(
            id=result.id,
            chat_id=result.chat_id,
            game_start=result.game_start,
            game_end=result.game_end,
            state=result.state,
            theme_id=result.theme_id,
            time_for_game=result.time_for_game,
            time_for_answer=result.time_for_answer,
            id_game_master=result.id_game_master,
            game_progress=[
                GameProgress(
                    id=gp.id,
                    id_gamer=gp.id_gamer,
                    id_gamesession=gp.id_gamesession,
                    difficulty_level=gp.difficulty_level,
                    gamer_status=gp.gamer_status,
                    number_of_mistakes=gp.number_of_mistakes,
                    number_of_right_answers=gp.number_of_right_answers,
                    is_answering=gp.is_answering,
                    gamer=Gamer(
                        id=gp.gamer.id,
                        id_tguser=gp.gamer.id_tguser,
                        first_name=gp.gamer.first_name,
                        number_of_defeats=gp.gamer.number_of_defeats,
                        number_of_victories=gp.gamer.number_of_victories,
                    )
                ) for gp in result.game_progress
            ]
        )

    async def update_state_gs(self, state: str, id_: int) -> GameSession:
        update_query = update(GameSessionModel) \
            .where(GameSessionModel.id == id_) \
            .values(state=state)
        rowcount = await self.make_update_query(update_query)
        return rowcount

    async def update_gs_timeout(self, chat_id: int, time_for_answer: int) -> int:
        update_query = update(GameSessionModel).where(
            and_(
                GameSessionModel.chat_id == chat_id,
                GameSessionModel.state == 'Active',
                GameSessionModel.game_end == None,
            )).values(time_for_answer=time_for_answer)
        rowcount = await self.make_update_query(update_query)
        return rowcount

    async def update_gs_duration(self, chat_id: int, time_for_game: int):
        update_query = update(GameSessionModel).where(
            and_(
                GameSessionModel.chat_id == chat_id,
                GameSessionModel.state == 'Active',
                GameSessionModel.game_end == None,
            )).values(time_for_game=time_for_game)
        rowcount = await self.make_update_query(update_query)
        return rowcount

    async def update_gs_start_time(self, game_start: datetime, id_: int):
        update_query = update(GameSessionModel).where(GameSessionModel.id == id_).values(game_start=game_start)
        rowcount = await self.make_update_query(update_query)
        return rowcount

    async def update_gs_end_time(self, game_end: datetime, id_: int):
        update_query = update(GameSessionModel).where(GameSessionModel.id == id_).values(game_end=game_end)
        rowcount = await self.make_update_query(update_query)
        return rowcount

    async def update_gs_state(self, state: str, id_: int):
        update_query = update(GameSessionModel).where(GameSessionModel.id == id_).values(state=state)
        rowcount = await self.make_update_query(update_query)
        return rowcount

    async def list_game_sessions(self) -> list[GameSession]:
        query = select(GameSessionModel).options(joinedload(GameSessionModel.game_progress))
        result = (await self.make_get_query(query)).scalars().unique()

        if not result:
            return []

        return [GameSession(
            id=gs.id,
            chat_id=gs.chat_id,
            game_start=gs.game_start,
            game_end=gs.game_end,
            state=gs.state,
            theme_id=gs.theme_id,
            time_for_game=gs.time_for_game,
            time_for_answer=gs.time_for_answer,
            id_game_master=gs.id_game_master,
            game_progress=[
                GameProgress(
                    id=gp.id,
                    id_gamer=gp.id_gamer,
                    id_gamesession=gp.id_gamesession,
                    difficulty_level=gp.difficulty_level,
                    gamer_status=gp.gamer_status,
                    number_of_mistakes=gp.number_of_mistakes,
                    number_of_right_answers=gp.number_of_right_answers,
                    is_answering=gp.is_answering
                ) for gp in gs.game_progress
            ]
        )
            for gs in result
        ]

    # Accessor for GameProgressModel (gp) :
    async def create_game_progress(self, id_gamer: int, id_gamesession: int,
                                   is_answering: bool = False) -> GameProgress:
        random_difficulty_level = random.choice(list(self.app.config.game.difficulty_levels))
        new_gp = GameProgressModel(
            id_gamer=id_gamer,
            difficulty_level=random_difficulty_level,
            id_gamesession=id_gamesession,
            is_answering=is_answering,
        )
        await self.make_add_query(new_gp)
        return GameProgress(
            id=new_gp.id,
            id_gamer=new_gp.id_gamer,
            id_gamesession=new_gp.id_gamesession,
            difficulty_level=new_gp.difficulty_level,
            gamer_status=new_gp.gamer_status,
            number_of_mistakes=new_gp.number_of_mistakes,
            number_of_right_answers=new_gp.number_of_right_answers,
            is_answering=new_gp.is_answering,
        )

    async def update_gp_is_answering(self, id_: int, is_answering: bool):
        update_query = update(GameProgressModel).where(GameProgressModel.id == id_).values(is_answering=is_answering)
        try:
            rowcount = await self.make_update_query(update_query)
        except Exception as e:
            print(e)
        return rowcount

    async def update_gp_number_of_mistakes(self, id_: int, number_of_mistakes: int):
        update_query = update(GameProgressModel).where(GameProgressModel.id == id_).values(
            number_of_mistakes=number_of_mistakes)
        rowcount = await self.make_update_query(update_query)
        return rowcount

    async def update_gp_number_of_rigth_answers(self, id_: int, number_of_right_answers: int):
        update_query = update(GameProgressModel).where(GameProgressModel.id == id_).values(
            number_of_right_answers=number_of_right_answers)
        rowcount = await self.make_update_query(update_query)
        return rowcount

    async def update_gp_gamer_status(self, id_: int, gamer_status: str):
        update_query = update(GameProgressModel).where(GameProgressModel.id == id_).values(
            gamer_status=gamer_status)
        rowcount = await self.make_update_query(update_query)
        return rowcount

    async def update_gp_gamer_status_in_gs(self, id_gs: int, gamer_status: str, filter_gamer_status: str = "Playing"):
        query = update(GameProgressModel).where(
            and_(
                GameProgressModel.id_gamesession == id_gs,
                GameProgressModel.gamer_status == filter_gamer_status
            )
        ).values(gamer_status=gamer_status)
        rowcount = await self.make_update_query(query)
        return rowcount

    async def get_gp_by_id(self, id_: int) -> GameProgress:
        query = select(GameProgressModel).options(joinedload(GameProgressModel.gamer)). \
            where(GameProgressModel.id == id_)
        res = (await self.make_get_query(query)).scalars().first()
        return GameProgress(
            id=res.id,
            id_gamer=res.id_gamer,
            difficulty_level=res.difficulty_level,
            gamer_status=res.gamer_status,
            number_of_mistakes=res.number_of_mistakes,
            number_of_right_answers=res.number_of_right_answers,
            is_answering=res.is_answering,
            id_gamesession=res.id_gamesession,
            gamer=Gamer(
                id=res.gamer.id,
                id_tguser=res.gamer.id_tguser,
                first_name=res.gamer.first_name,
                number_of_defeats=res.gamer.number_of_defeats,
                number_of_victories=res.gamer.number_of_victories,
            )
        )

    async def get_gp_by_id_gs(self, id_gs: int, gamer_status: str = None) -> list[GameProgress]:
        query = select(GameProgressModel).options(joinedload(GameProgressModel.gamer))
        if not gamer_status:
            query = query.where(GameProgressModel.id_gamesession == id_gs)
        else:
            query = query.where(
                and_(
                    GameProgressModel.id_gamesession == id_gs,
                    GameProgressModel.gamer_status == gamer_status, )
            )
        try:
            res = (await self.make_get_query(query)).scalars().unique()
        except Exception as e:
            print(e)
        return [
            GameProgress(
                id=gp.id,
                id_gamer=gp.id_gamer,
                difficulty_level=gp.difficulty_level,
                gamer_status=gp.gamer_status,
                number_of_mistakes=gp.number_of_mistakes,
                number_of_right_answers=gp.number_of_right_answers,
                is_answering=gp.is_answering,
                id_gamesession=gp.id_gamesession,
                gamer=Gamer(
                    id=gp.gamer.id,
                    id_tguser=gp.gamer.id_tguser,
                    first_name=gp.gamer.first_name,
                    number_of_defeats=gp.gamer.number_of_defeats,
                    number_of_victories=gp.gamer.number_of_victories,
                )
            ) for gp in res
        ]

    async def list_game_progresses(self) -> list[GameProgress]:
        query = select(GameProgressModel)
        result = (await self.make_get_query(query)).scalars().unique()

        if not result:
            return []

        return [
            GameProgress(
                id=gp.id,
                id_gamer=gp.id_gamer,
                id_gamesession=gp.id_gamesession,
                difficulty_level=gp.difficulty_level,
                gamer_status=gp.gamer_status,
                number_of_mistakes=gp.number_of_mistakes,
                number_of_right_answers=gp.number_of_right_answers,
                is_answering=gp.is_answering,
            ) for gp in result
        ]

    # Extended Queries
    async def get_all_gameinfo(self, chat_id: int):
        query = select(GameSessionModel, GameProgressModel, GamerModel) \
            .options(joinedload(GameSessionModel.game_master)) \
            .options(joinedload(GameSessionModel.game_progress) \
                     .options(joinedload(GameProgressModel.gamer))) \
            .where(
            and_(
                GameSessionModel.chat_id == chat_id,
                GameSessionModel.game_end == None,
            )
        )
        result = (await self.make_get_query(query)).scalars().first()

        if result is None:
            return

        return GameSession(
            id=result.id,
            chat_id=result.chat_id,
            id_game_master=result.id_game_master,
            game_start=result.game_start,
            game_end=result.game_end,
            state=result.state,
            theme_id=result.theme_id,
            time_for_game=result.time_for_game,
            time_for_answer=result.time_for_answer,
            game_master=Gamer(
                id=result.game_master.id,
                id_tguser=result.game_master.id_tguser,
                first_name=result.game_master.first_name,
                number_of_defeats=result.game_master.number_of_defeats,
                number_of_victories=result.game_master.number_of_victories,
            ),
            game_progress=[
                GameProgress(
                    id=gp.id,
                    id_gamer=gp.id_gamer,
                    id_gamesession=gp.id_gamesession,
                    difficulty_level=gp.difficulty_level,
                    gamer_status=gp.gamer_status,
                    number_of_mistakes=gp.number_of_mistakes,
                    number_of_right_answers=gp.number_of_right_answers,
                    is_answering=gp.is_answering,
                    gamer=Gamer(
                        id=gp.gamer.id,
                        id_tguser=gp.gamer.id_tguser,
                        first_name=gp.gamer.first_name,
                        number_of_defeats=gp.gamer.number_of_defeats,
                        number_of_victories=gp.gamer.number_of_victories,
                    )
                ) for gp in result.game_progress
            ]
        )
