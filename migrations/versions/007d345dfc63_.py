"""empty message

Revision ID: 007d345dfc63
Revises: 
Create Date: 2022-07-25 16:03:33.512632

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '007d345dfc63'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('routine',
    sa.Column('routine_id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('title', sa.String(), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('routine_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('routine')
    # ### end Alembic commands ###