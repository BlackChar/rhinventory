"""Add privacy columns to Asset and File

Revision ID: 80b134bde2f5
Revises: 0e3519f2f8dc
Create Date: 2023-12-11 19:57:42.354234

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '80b134bde2f5'
down_revision = '0e3519f2f8dc'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    sa.Enum('private_implicit', 'private', 'unlinked', 'public', name='privacy').create(op.get_bind())
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('assets', sa.Column('privacy', sa.Enum('private_implicit', 'private', 'unlinked', 'public', name='privacy'), nullable=False, default='private_implicit', server_default='private_implicit'))
    op.add_column('files', sa.Column('privacy', sa.Enum('private_implicit', 'private', 'unlinked', 'public', name='privacy'), nullable=False, default='private_implicit', server_default='private_implicit'))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('files', 'privacy')
    op.drop_column('assets', 'privacy')
    # ### end Alembic commands ###