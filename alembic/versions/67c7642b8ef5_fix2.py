"""fix2

Revision ID: 67c7642b8ef5
Revises: 195f4992e16e
Create Date: 2024-08-15 19:01:01.595547

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '67c7642b8ef5'
down_revision = '195f4992e16e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('label_printers', 'comment',
               existing_type=sa.VARCHAR(),
               nullable=True)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('label_printers', 'comment',
               existing_type=sa.VARCHAR(),
               nullable=False)
    # ### end Alembic commands ###
