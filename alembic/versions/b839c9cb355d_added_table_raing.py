"""Added table Raing

Revision ID: b839c9cb355d
Revises: 541e794685b3
Create Date: 2023-05-15 00:44:48.879640

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b839c9cb355d'
down_revision = '541e794685b3'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('UserRating',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email_user', sa.Text(), nullable=False),
    sa.Column('id_course', sa.Integer(), nullable=False),
    sa.Column('answers', sa.Text(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('UserRating')
    # ### end Alembic commands ###
