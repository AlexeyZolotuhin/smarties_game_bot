from app.game.models import Gamer, GamerModel, GameSessionModel, GameSession, GameProgressModel, \
    GameProgress
from app.base.base_accessor import BaseAccessor
from sqlalchemy import String, and_, delete, or_, select, distinct, update, insert
from sqlalchemy.orm import joinedload
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
    async def create_gamer(self, id_tguser: int, username: str) -> Gamer:
        new_gamer = GamerModel(id_tguser=id_tguser, username=username)
        await self.make_add_query(new_gamer)
        return Gamer(id=new_gamer.id,
                     id_tguser=new_gamer.id_tguser,
                     username=new_gamer.username,
                     number_of_victories=new_gamer.number_of_victories,
                     number_of_defeats=new_gamer.number_of_defeats,
                     )

    async def list_gamers(self) -> list[Gamer]:
        query = select(GamerModel)
        result = (await self.make_get_query(query)).scalars().unique()

        if not result:
            return []

        return [Gamer(id=gamer.id,
                      id_tguser=gamer.id_tguser,
                      username=gamer.username,
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
                     username=result.username,
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
                     username=result.username,
                     number_of_victories=result.number_of_victories,
                     number_of_defeats=result.number_of_defeats,
                     )

    async def update_gamer_victories(self, id_tguser: int, number_of_victories: int) -> Gamer:
        update_query = update(GamerModel) \
            .where(GamerModel.id_tguser == id_tguser) \
            .values(number_of_victories=number_of_victories)
        await self.make_update_query(update_query)
        return await self.get_gamer_by_id_tguser(id_tguser=id_tguser)

    async def update_gamer_defeats(self, id_tguser: int, number_of_defeats: int) -> Gamer:
        update_query = update(GamerModel) \
            .where(GamerModel.id_tguser == id_tguser) \
            .values(number_of_defeats=number_of_defeats)
        await self.make_update_query(update_query)
        return await self.get_gamer_by_id_tguser(id_tguser=id_tguser)

    # Accessor for GameSessionModel (gs):
    async def create_game_session(self, chat_id: int,
                                  theme_id: int = None,
                                  time_for_game: int = None,
                                  time_for_answer: int = None, ) -> GameSession:
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
                                  )
        await self.make_add_query(new_gs)
        return GameSession(
            id=new_gs.id,
            chat_id=new_gs.chat_id,
            game_start=new_gs.game_start,
            game_end=new_gs.game_end,
            state=new_gs.state,
            theme_id=new_gs.theme_id,
            time_for_game=new_gs.time_for_game,
            time_for_answer=new_gs.time_for_answer,
        )

    async def get_gs_by_id(self, id_: int) -> GameSession | None:
        query = select(GameSessionModel). \
            where(GameSessionModel.id == id_). \
            options(joinedload(GameSessionModel.game_progress))

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
            game_progress=[
                GameProgress(
                    id_gamer=gp.id_gamer,
                    difficulty_level=gp.difficulty_level,
                    gamer_status=gp.gamer_status,
                    number_of_mistakes=gp.number_of_mistakes,
                    number_of_right_answers=gp.number_of_right_answers,
                    is_master=gp.is_master,
                ) for gp in result.game_progress
            ]
        )

    async def get_gs_by_chat_id(self, chat_id: int, state: str = "Active") -> GameSession | None:
        query = select(GameSessionModel).where(
            and_(
                GameSessionModel.chat_id == chat_id,
                GameSessionModel.state == state,
            )
        ).options(joinedload(GameSessionModel.game_progress))

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
            game_progress=[
                GameProgress(
                    id=gp.id,
                    id_gamer=gp.id_gamer,
                    id_gamesession=gp.id_gamesession,
                    difficulty_level=gp.difficulty_level,
                    gamer_status=gp.gamer_status,
                    number_of_mistakes=gp.number_of_mistakes,
                    number_of_right_answers=gp.number_of_right_answers,
                    is_master=gp.is_master,
                ) for gp in result.game_progress
            ]
        )

    async def update_state_gs(self, state: str, id_: int) -> GameSession:
        update_query = update(GameSessionModel) \
            .where(GameSessionModel.id == id_) \
            .values(state=state).options(joinedload(GameSessionModel.game_progress))
        update_gs = (await self.make_update_query(update_query)).scalars().first()
        return GameSession(
            id=update_gs.id,
            chat_id=update_gs.chat_id,
            game_start=update_gs.game_start,
            game_end=update_gs.game_end,
            state=update_gs.state,
            theme_id=update_gs.theme_id,
            time_for_game=update_gs.time_for_game,
            time_for_answer=update_gs.time_for_answer,
            game_progress=[
                GameProgress(
                    id_gamer=gp.id_gamer,
                    difficulty_level=gp.difficulty_level,
                    gamer_status=gp.gamer_status,
                    number_of_mistakes=gp.number_of_mistakes,
                    number_of_right_answers=gp.number_of_right_answers,
                    is_master=gp.is_master,
                ) for gp in update_gs.game_progress
            ]
        )

    async def update_gs_timeout(self, chat_id: int, time_for_answer: int) -> GameSession:
        update_query = update(GameSessionModel).where(
            and_(
                GameSessionModel.chat_id == chat_id,
                GameSessionModel.state == 'Active',
            )).values(time_for_answer=time_for_answer).options(joinedload(GameSessionModel.game_progress))
        await self.make_update_query(update_query)
        return await self.get_gs_by_chat_id(chat_id)

    async def update_gs_duration(self, chat_id: int, time_for_game: int) -> GameSession:
        update_query = update(GameSessionModel).where(
            and_(
                GameSessionModel.chat_id == chat_id,
                GameSessionModel.state == 'Active',
            )).values(time_for_game=time_for_game).options(joinedload(GameSessionModel.game_progress))
        await self.make_update_query(update_query)
        return await self.get_gs_by_chat_id(chat_id)

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
            game_progress=[
                GameProgress(
                    id=gp.id,
                    id_gamer=gp.id_gamer,
                    id_gamesession=gp.id_gamesession,
                    difficulty_level=gp.difficulty_level,
                    gamer_status=gp.gamer_status,
                    number_of_mistakes=gp.number_of_mistakes,
                    number_of_right_answers=gp.number_of_right_answers,
                    is_master=gp.is_master
                ) for gp in gs.game_progress
            ]
        )
            for gs in result
        ]

    # Accessor for GameProgressModel (gp) :
    async def create_game_progress(self, id_gamer: int, id_gamesession: int, is_master: bool = False) -> GameProgress:
        random_difficulty_level = (random.choice(self.app.config.game.difficulty_levels)).level
        new_gp = GameProgressModel(
            id_gamer=id_gamer,
            difficulty_level=random_difficulty_level,
            id_gamesession=id_gamesession,
            is_master=is_master,
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
            is_master=new_gp.is_master,
        )
