"""empty message

Revision ID: 9d8ed1656506
Revises: fd4d399baef3
Create Date: 2021-05-28 16:02:28.244914

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9d8ed1656506'
down_revision = 'fd4d399baef3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('media',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('uid', sa.Text(), nullable=True),
    sa.Column('file_data', sa.LargeBinary(), nullable=False),
    sa.Column('content_type', sa.Text(), nullable=True),
    sa.Column('parrent_message_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['parrent_message_id'], ['messages.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('messages', sa.Column('content_type', sa.Text(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('messages', 'content_type')
    op.drop_table('media')
    # ### end Alembic commands ###
