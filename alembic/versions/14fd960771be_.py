"""empty message

Revision ID: 14fd960771be
Revises: 
Create Date: 2021-02-21 17:56:17.465666

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '14fd960771be'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('telegram_users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('telegram_id', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('stories',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('author_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['author_id'], ['telegram_users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('messages',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('story_id', sa.Integer(), nullable=True),
    sa.Column('message', sa.Text(), nullable=True),
    sa.Column('parent_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['parent_id'], ['messages.id'], ),
    sa.ForeignKeyConstraint(['story_id'], ['stories.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('messages')
    op.drop_table('stories')
    op.drop_table('telegram_users')
    # ### end Alembic commands ###