"""Add last_used to a number of asset attributes

Revision ID: 9f817789cd74
Revises: 2662f6133944
Create Date: 2023-03-28 19:21:51.602684

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9f817789cd74'
down_revision = '2662f6133944'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('media', sa.Column('last_used', sa.DateTime(), nullable=True))
    op.add_column('packagings', sa.Column('last_used', sa.DateTime(), nullable=True))
    op.add_column('platforms', sa.Column('last_used', sa.DateTime(), nullable=True))
    op.add_column('tags', sa.Column('last_used', sa.DateTime(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tags', 'last_used')
    op.drop_column('platforms', 'last_used')
    op.drop_column('packagings', 'last_used')
    op.drop_column('media', 'last_used')
    # ### end Alembic commands ###
