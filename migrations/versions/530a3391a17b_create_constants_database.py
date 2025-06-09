"""create constants database

Revision ID: 530a3391a17b
Revises: 868004f7a00f
Create Date: 2025-06-09 16:36:24.958521

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '530a3391a17b'
down_revision: Union[str, None] = '868004f7a00f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE TABLE currencies (id SERIAL PRIMARY KEY, name VARCHAR(255), code VARCHAR(255))");
    op.execute("INSERT INTO currencies (name, code) VALUES ('United States Dollar', 'USD'), ('Indian Rupee', 'INR')");


def downgrade() -> None:
    op.execute("DROP TABLE currencies");
