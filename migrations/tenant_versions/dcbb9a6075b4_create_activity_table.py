"""create activity table

Revision ID: dcbb9a6075b4
Revises: fe3e21032723
Create Date: 2025-06-09 17:49:25.656538

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dcbb9a6075b4'
down_revision: Union[str, None] = 'fe3e21032723'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE TABLE activity (id SERIAL PRIMARY KEY, name VARCHAR(255), activity_type VARCHAR(255), activity_date TIMESTAMP, activity_description TEXT)");


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP TABLE activity");
