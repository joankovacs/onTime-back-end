"""empty message

Revision ID: ac489152aae9
Revises: 
Create Date: 2022-07-27 18:21:59.873005

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ac489152aae9'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('routine',
    sa.Column('routine_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('destination', sa.String(), nullable=True),
    sa.Column('complete_time', sa.DateTime(), nullable=True),
    sa.Column('start_time', sa.DateTime(), nullable=True),
    sa.Column('total_time', sa.Integer(), nullable=True),
    sa.Column('saved', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('routine_id')
    )
    op.create_table('task',
    sa.Column('task_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('time', sa.Integer(), nullable=True),
    sa.Column('routine_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['routine_id'], ['routine.routine_id'], ),
    sa.PrimaryKeyConstraint('task_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('task')
    op.drop_table('routine')
    # ### end Alembic commands ###
