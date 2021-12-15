"""update tableau_emolument

Revision ID: b632e71b4788
Revises: 6529461c9152
Create Date: 2021-12-15 15:48:33.590473

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b632e71b4788'
down_revision = '6529461c9152'
branch_labels = None
depends_on = None

def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tableau_emoluments', sa.Column('date_entree', sa.Date(), nullable=True))
    op.add_column('tableau_emoluments', sa.Column('date_sortie', sa.Date(), nullable=True))
    op.add_column('tableau_emoluments', sa.Column('remplace', sa.BigInteger(), nullable=True))
    op.add_column('tableau_emoluments', sa.Column('priorite', sa.Integer(), nullable=True))
    # ### end Alembic commands ###

def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tableau_emoluments', 'priorite')
    op.drop_column('tableau_emoluments', 'remplace')
    op.drop_column('tableau_emoluments', 'date_sortie')
    op.drop_column('tableau_emoluments', 'date_entree')
    # ### end Alembic commands ###
