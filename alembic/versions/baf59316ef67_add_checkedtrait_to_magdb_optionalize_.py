"""Add CheckedTrait to MagDB + optionalize all uneeded fields.

Revision ID: baf59316ef67
Revises: c49e9ca7103f
Create Date: 2023-10-14 15:22:03.824322

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import ENUM

# revision identifiers, used by Alembic.
revision = 'baf59316ef67'
down_revision = 'c49e9ca7103f'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.execute(f"ALTER TYPE magdbfiletype ADD VALUE 'photo' BEFORE 'index_page'")

    op.create_table('magazine_supplement',
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.Column('created_by', sa.Integer(), nullable=True),
    sa.Column('updated_by', sa.Integer(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(length=255), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('title')
    )
    op.create_table('magazine_supplement_version',
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.Column('created_by', sa.Integer(), nullable=True),
    sa.Column('updated_by', sa.Integer(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('magazine_supplement_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['magazine_supplement_id'], ['magazine_supplement.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.create_table('magazine_supplement_version_files',
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
    sa.Column('created_by', sa.Integer(), nullable=True),
    sa.Column('updated_by', sa.Integer(), nullable=True),
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('magazine_supplement_version_id', sa.Integer(), nullable=False),
    sa.Column('file_id', sa.Integer(), nullable=False),
    sa.Column('file_type', ENUM('logo', 'scan', 'cover_page', 'index_page', 'photo', name='magdbfiletype', create_type=False), nullable=True),
    sa.ForeignKeyConstraint(['file_id'], ['files.id'], ),
    sa.ForeignKeyConstraint(['magazine_supplement_version_id'], ['magazine_supplement_version.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('id')
    )
    op.add_column('magazine_issue_versions', sa.Column('inserted', sa.Boolean(), server_default='False', nullable=True))
    op.add_column('magazine_issue_versions', sa.Column('manually_checked', sa.Boolean(), server_default='False', nullable=True))
    op.add_column('magazine_issues', sa.Column('inserted', sa.Boolean(), server_default='False', nullable=True))
    op.add_column('magazine_issues', sa.Column('manually_checked', sa.Boolean(), server_default='False', nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.sync_enum_values('public', 'magdbfiletype', ['cover_page', 'index_page', 'logo', 'photo', 'scan'], ['cover_page', 'index_page', 'logo', 'scan'])
    op.alter_column('tags', 'description',
               existing_type=sa.VARCHAR(),
               nullable=True)
    op.drop_column('magazine_issues', 'manually_checked')
    op.drop_column('magazine_issues', 'inserted')
    op.drop_column('magazine_issue_versions', 'manually_checked')
    op.drop_column('magazine_issue_versions', 'inserted')
    op.drop_table('magazine_supplement_version_files')
    op.drop_table('magazine_supplement_version')
    op.drop_table('magazine_supplement')
    # ### end Alembic commands ###
