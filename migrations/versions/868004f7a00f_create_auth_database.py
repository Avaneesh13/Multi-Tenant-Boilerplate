"""create auth database

Revision ID: 868004f7a00f
Revises: 
Create Date: 2025-06-09 16:34:49.902999

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '868004f7a00f'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE TABLE users (id SERIAL PRIMARY KEY, name VARCHAR(255), email VARCHAR(255), password VARCHAR(255))");
    op.execute("CREATE TABLE companies (id SERIAL PRIMARY KEY, db_name VARCHAR(255), name VARCHAR(255), email VARCHAR(255), password VARCHAR(255))");


def downgrade() -> None:
    op.execute("DROP TABLE users");
    op.execute("DROP TABLE companies");