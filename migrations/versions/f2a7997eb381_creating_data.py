"""creating data

Revision ID: f2a7997eb381
Revises: 
Create Date: 2021-04-27 06:58:19.168126

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f2a7997eb381'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('pasien', sa.Column('tanggal', sa.String(length=100), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('pasien', 'tanggal')
    # ### end Alembic commands ###
