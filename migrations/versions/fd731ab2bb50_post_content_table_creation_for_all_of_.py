"""Post content table creation for all of the post

Revision ID: fd731ab2bb50
Revises: 3a48877ed04a
Create Date: 2023-12-14 19:46:42.118995

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'fd731ab2bb50'
down_revision = '3a48877ed04a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('post_content',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('type', sa.VARCHAR(length=255), nullable=False),
    sa.Column('author', sa.VARCHAR(length=255), nullable=False),
    sa.Column('header', sa.VARCHAR(length=255), nullable=False),
    sa.Column('desc', sa.Text(), nullable=False),
    sa.Column('source', sa.Text(), nullable=True),
    sa.Column('date', sa.Text(), nullable=True),
    sa.Column('img', sa.Text(), nullable=True),
    sa.Column('img_credits', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('post_content')
    # ### end Alembic commands ###
