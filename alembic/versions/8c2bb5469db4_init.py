"""Init

Revision ID: 8c2bb5469db4
Revises: 
Create Date: 2022-09-18 19:26:29.432426user_pass

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8c2bb5469db4'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('admins',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('login', sa.VARCHAR(length=50), nullable=False),
    sa.Column('password', sa.VARCHAR(length=200), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('login')
    )
    op.create_table('gamers',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_tguser', sa.BIGINT(), nullable=False),
    sa.Column('first_name', sa.VARCHAR(length=50), nullable=False),
    sa.Column('number_of_defeats', sa.Integer(), nullable=False),
    sa.Column('number_of_victories', sa.Integer(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id_tguser')
    )
    op.create_table('themes',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('title', sa.VARCHAR(length=200), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('title')
    )
    op.create_table('game_sessions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('chat_id', sa.BIGINT(), nullable=False),
    sa.Column('id_game_master', sa.Integer(), nullable=False),
    sa.Column('game_start', sa.DateTime(), nullable=True),
    sa.Column('game_end', sa.DateTime(), nullable=True),
    sa.Column('state', sa.VARCHAR(length=15), nullable=True),
    sa.Column('theme_id', sa.Integer(), nullable=True),
    sa.Column('time_for_game', sa.Integer(), nullable=True),
    sa.Column('time_for_answer', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['id_game_master'], ['gamers.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('questions',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('title', sa.VARCHAR(length=200), nullable=False),
    sa.Column('theme_id', sa.BigInteger(), nullable=False),
    sa.ForeignKeyConstraint(['theme_id'], ['themes.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('title')
    )
    op.create_table('answers',
    sa.Column('id', sa.BigInteger(), nullable=False),
    sa.Column('title', sa.VARCHAR(length=250), nullable=False),
    sa.Column('is_correct', sa.BOOLEAN(), nullable=False),
    sa.Column('question_id', sa.BigInteger(), nullable=False),
    sa.ForeignKeyConstraint(['question_id'], ['questions.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('game_progress',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('id_gamer', sa.Integer(), nullable=False),
    sa.Column('difficulty_level', sa.Integer(), nullable=False),
    sa.Column('is_answering', sa.BOOLEAN(), nullable=True),
    sa.Column('id_gamesession', sa.Integer(), nullable=False),
    sa.Column('gamer_status', sa.VARCHAR(length=15), nullable=True),
    sa.Column('number_of_mistakes', sa.Integer(), nullable=True),
    sa.Column('number_of_right_answers', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['id_gamer'], ['gamers.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['id_gamesession'], ['game_sessions.id'], onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('game_progress')
    op.drop_table('answers')
    op.drop_table('questions')
    op.drop_table('game_sessions')
    op.drop_table('themes')
    op.drop_table('gamers')
    op.drop_table('admins')
    # ### end Alembic commands ###
