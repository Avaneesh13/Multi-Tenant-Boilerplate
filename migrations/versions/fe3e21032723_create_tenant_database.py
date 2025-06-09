"""create tenant database

Revision ID: fe3e21032723
Revises: 530a3391a17b
Create Date: 2025-06-09 16:38:26.940639

"""
import random
import string
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'fe3e21032723'
down_revision: Union[str, None] = '530a3391a17b'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade(tenant_name: str = None) -> str:
    if not tenant_name:
        tenant_name = "db_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=10))

    op.execute(f"CREATE TABLE leads (id SERIAL PRIMARY KEY, name VARCHAR(255), email VARCHAR(255), phone VARCHAR(255))");

    return tenant_name

def downgrade(tenant_name: str) -> None:
    op.execute(f"DROP TABLE leads");
