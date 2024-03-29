"""empty message

Revision ID: 72c1da9626f7
Revises: c0f01daef2c9
Create Date: 2018-11-29 11:51:46.397144

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '72c1da9626f7'
down_revision = 'c0f01daef2c9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_user_department', table_name='user')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index('ix_user_department', 'user', ['department'], unique=1)
    # ### end Alembic commands ###
