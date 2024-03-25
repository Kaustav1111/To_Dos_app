"""Create phone_number column for Users table

Revision ID: f63e28ba4d6b
Revises: 
Create Date: 2024-03-11 19:38:03.089016

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f63e28ba4d6b'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('Users' , sa.Column('phone_number' , sa.String(50) , nullable=True))


def downgrade() -> None:
    op.drop_column('Users' , 'phone_number')
    
