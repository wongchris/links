"""empty message

Revision ID: 31fc159bb67d
Revises: 72c1da9626f7
Create Date: 2018-12-06 11:03:20.449226

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '31fc159bb67d'
down_revision = '72c1da9626f7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('database',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('driver', sa.String(length=30), nullable=True),
    sa.Column('host', sa.String(length=30), nullable=True),
    sa.Column('db_name', sa.String(length=30), nullable=True),
    sa.Column('login', sa.String(length=30), nullable=True),
    sa.Column('password', sa.String(length=30), nullable=True),
    sa.Column('remark', sa.String(length=100), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('database')
    # ### end Alembic commands ###
