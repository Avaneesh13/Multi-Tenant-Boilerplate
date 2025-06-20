from logging.config import fileConfig
import os

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = None

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def include_object(object, name, type_, reflected, compare_to):
    """Filter out tenant migrations when running system upgrades."""
    # Only exclude during upgrade operations, not during revision generation
    if type_ == "table" and hasattr(context, '_current_rev'):
        # Check if we're in a tenant migration file
        script_dir = context.script_directory
        if script_dir:
            current_head = script_dir.get_current_head()
            if current_head and 'tenant_versions' in str(script_dir.get_revision(current_head).path):
                return False
    return True

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    
    # Filter version locations to exclude tenant_versions during upgrades
    version_locations = config.get_main_option("version_locations")
    if version_locations and not os.getenv('ALEMBIC_ALLOW_TENANT_MIGRATIONS'):
        # Only include system migrations (migrations/versions)
        filtered_locations = []
        for location in version_locations.split(':'):
            if 'tenant_versions' not in location:
                filtered_locations.append(location)
        if filtered_locations:
            config.set_main_option("version_locations", ':'.join(filtered_locations))
    
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Filter version locations to exclude tenant_versions during upgrades
    version_locations = config.get_main_option("version_locations")
    if version_locations and not os.getenv('ALEMBIC_ALLOW_TENANT_MIGRATIONS'):
        # Only include system migrations (migrations/versions)
        filtered_locations = []
        for location in version_locations.split(':'):
            if 'tenant_versions' not in location:
                filtered_locations.append(location)
        if filtered_locations:
            config.set_main_option("version_locations", ':'.join(filtered_locations))
    
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
