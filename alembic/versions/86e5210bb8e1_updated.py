"""Updated

Revision ID: 86e5210bb8e1
Revises: 0008f3357b07
Create Date: 2023-05-12 14:18:59.859141

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '86e5210bb8e1'
down_revision = '0008f3357b07'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('AdminCourse', sa.Text(), nullable=True))
    op.drop_column('users', 'AdminCourses')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('AdminCourses', postgresql.JSON(astext_type=sa.Text()), autoincrement=False, nullable=True))
    op.drop_column('users', 'AdminCourse')
    # ### end Alembic commands ###
