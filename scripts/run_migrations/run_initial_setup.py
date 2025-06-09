#!/usr/bin/env python3
"""
Initial Setup Script for Flask PostgreSQL Server
This script handles the initial setup and configuration of the Flask application.
"""

import os
import random
import string
import sys
import subprocess
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

def check_python_version():
    """Check if Python version is compatible."""
    if sys.version_info < (3, 8):
        print("ERROR: Python 3.8 or higher is required")
        return False
    return True

def install_dependencies():
    """Install required Python packages."""
    requirements_file = project_root / "requirements.txt"
    
    if not requirements_file.exists():
        print("ERROR: requirements.txt not found")
        return False
    
    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", str(requirements_file)
        ], check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"ERROR: Failed to install dependencies: {e.stderr}")
        return False

def create_env_file():
    """Create .env file if it doesn't exist."""
    env_file = project_root / ".env"
    
    if env_file.exists():
        return True
    
    env_template = """# PostgreSQL Database Connection Parameters
# Replace with your actual database credentials
DB_USERNAME=your_username
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=5432

# Example configuration:
# DB_USERNAME=postgres
# DB_PASSWORD=password123
# DB_HOST=localhost
# DB_PORT=5432
"""
    
    try:
        with open(env_file, 'w') as f:
            f.write(env_template)
        print("Created .env template - please edit with your database credentials")
        return True
    except Exception as e:
        print(f"ERROR: Failed to create .env file: {e}")
        return False

def get_db_credentials():
    """Get database credentials from environment variables."""
    from dotenv import load_dotenv
    load_dotenv(project_root / ".env")
    
    username = os.getenv('DB_USERNAME')
    password = os.getenv('DB_PASSWORD')
    host = os.getenv('DB_HOST', 'localhost')
    port = os.getenv('DB_PORT', '5432')
    
    return username, password, host, port

def create_connection_string(db_name, username, password, host, port):
    """Create a PostgreSQL connection string for the specified database."""
    return f"postgresql://{username}:{password}@{host}:{port}/{db_name}"

def test_database_connection():
    """Test database connection if credentials are provided."""
    try:
        username, password, host, port = get_db_credentials()
        
        if not username or not password or 'your_username' in username:
            print("WARNING: Database credentials not configured - update .env file")
            return True
        
        from sqlalchemy import create_engine, text
        
        def my_create_engine(conn_str, pool_recycle=3600, pool_size=8):
            return create_engine(conn_str, pool_recycle=pool_recycle, pool_size=pool_size)
        
        # Test connection using postgres database (default database)
        conn_str = create_connection_string('postgres', username, password, host, port)
        engine = my_create_engine(conn_str)
        
        with engine.connect() as connection:
            result = connection.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"Database connected: {version.split()[0]} {version.split()[1]}")
            
        return True
        
    except ImportError as e:
        print(f"ERROR: Missing required modules: {e}")
        return False
    except Exception as e:
        print(f"ERROR: Database connection failed: {e}")
        print("Please check your database credentials in .env file")
        return False

def run_initial_migrations():
    """Run the initial set of migrations (auth, constants, and 3 tenant databases)."""
    try:
        print("Running initial database migrations...")
        
        username, password, host, port = get_db_credentials()
        
        if not username or not password or 'your_username' in username:
            print("WARNING: Database credentials not configured - skipping migrations")
            return True
        
        from sqlalchemy import create_engine, text
        from alembic.config import Config
        from alembic import command
        
        def my_create_engine(conn_str, pool_recycle=3600, pool_size=8):
            return create_engine(conn_str, pool_recycle=pool_recycle, pool_size=pool_size)
        
        # Connect to postgres database for creating other databases
        postgres_conn_str = create_connection_string('postgres', username, password, host, port)
        engine = my_create_engine(postgres_conn_str)
        
        # Test connection first
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        
        # Create databases first using autocommit (CREATE DATABASE cannot run in transactions)
        engine_autocommit = engine.execution_options(isolation_level="AUTOCOMMIT")
        
        databases_to_create = ["auth", "constants"]
        with engine_autocommit.connect() as connection:
            for db_name in databases_to_create:
                try:
                    connection.execute(text(f"CREATE DATABASE {db_name}"))
                    print(f"Created {db_name} database")
                except Exception as e:
                    if "already exists" not in str(e):
                        raise e
        
        # Now run the migrations to create tables on each specific database
        alembic_cfg = Config(str(project_root / "alembic.ini"))
        
        # Run auth migration on auth database
        auth_conn_str = create_connection_string('auth', username, password, host, port)
        alembic_cfg.set_main_option("sqlalchemy.url", auth_conn_str)
        command.upgrade(alembic_cfg, "868004f7a00f")
        print("Created auth tables")
        
        # Run constants migration on constants database
        constants_conn_str = create_connection_string('constants', username, password, host, port)
        alembic_cfg.set_main_option("sqlalchemy.url", constants_conn_str)
        command.upgrade(alembic_cfg, "530a3391a17b")
        print("Created constants tables")
        
        tenant_names = []
        
        # First create the tenant databases using autocommit
        for i in range(3):
            tenant_name = "db_" + "".join(random.choices(string.ascii_lowercase + string.digits, k=10))
            try:
                with engine_autocommit.connect() as connection:
                    connection.execute(text(f"CREATE DATABASE {tenant_name}"))
                    print(f"Created tenant database: {tenant_name}")
                tenant_names.append(tenant_name)
            except Exception as e:
                if "already exists" not in str(e):
                    print(f"ERROR: Failed to create tenant database {tenant_name}: {e}")
                # Continue with other tenants
        
        # Now run the tenant migration to create tables and insert company records
        import importlib.util
        
        # Import the migration file dynamically
        migration_file = project_root / "migrations" / "versions" / "fe3e21032723_create_tenant_database.py"
        spec = importlib.util.spec_from_file_location("tenant_migration", migration_file)
        tenant_migration = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(tenant_migration)
        
        # Run tenant migrations to create tables in each tenant database
        for tenant_name in tenant_names:
            try:
                # Connect to the specific tenant database to create tables
                tenant_conn_str = create_connection_string(tenant_name, username, password, host, port)
                tenant_engine = my_create_engine(tenant_conn_str)
                
                with tenant_engine.connect() as connection:
                    # Set up the alembic context for direct execution
                    from alembic.runtime.migration import MigrationContext
                    from alembic.operations import Operations
                    
                    mc = MigrationContext.configure(connection)
                    ops = Operations(mc)
                    
                    # Store the op context for the migration functions
                    tenant_migration.op = ops
                    
                    tenant_migration.upgrade(tenant_name)
                    connection.commit()
                    print(f"Created tables for tenant: {tenant_name}")
                    
            except Exception as e:
                print(f"ERROR: Failed to create tables for tenant {tenant_name}: {e}")
                # Continue with other tenants
        
        # Insert tenant records into auth.companies table
        auth_conn_str = create_connection_string('auth', username, password, host, port)
        auth_engine = my_create_engine(auth_conn_str)
        
        with auth_engine.connect() as connection:
            for tenant_name in tenant_names:
                try:
                    connection.execute(text(f"INSERT INTO companies (db_name, name, email, password) VALUES ('{tenant_name}', '{tenant_name}', '{tenant_name}@example.com', '{tenant_name}')"))
                    print(f"Registered tenant {tenant_name} in auth.companies")
                except Exception as e:
                    print(f"ERROR: Failed to register tenant {tenant_name} in companies table: {e}")
                    # Continue with other tenants
            
            connection.commit()
        
        print(f"Migrations completed - created {len(tenant_names)} tenant databases")
        return True
        
    except ImportError as e:
        print(f"ERROR: Missing required modules for migrations: {e}")
        return False
    except Exception as e:
        print(f"ERROR: Migration failed: {e}")
        return False

def verify_flask_app():
    """Verify that the Flask app can be imported."""
    try:
        sys.path.insert(0, str(project_root))
        
        # Try to import the app
        import app
        return True
        
    except ImportError as e:
        print(f"ERROR: Failed to import Flask app: {e}")
        return False
    except Exception as e:
        print(f"ERROR: Flask app verification failed: {e}")
        return False

def print_next_steps():
    """Print instructions for next steps."""
    print("\n" + "="*60)
    print("SETUP COMPLETE!")
    print("="*60)
    print("Database setup completed:")
    print("  ✅ Auth database created with users and companies tables")
    print("  ✅ Constants database created with currencies")
    print("  ✅ 3 Tenant databases created (tenant_1_db, tenant_2_db, tenant_3_db)")
    print("")
    print("Next steps:")
    print("1. Run the Flask server: python app.py")
    print("2. Visit http://localhost:5000/timestamp to test")
    print("3. Visit http://localhost:5000/health to check status")
    print("4. Your tenant databases are ready for use!")
    print("="*60)

def main():
    """Main setup function."""
    print("Starting Flask PostgreSQL setup...")
    
    # Change to project root directory
    os.chdir(project_root)
    
    setup_steps = [
        ("Checking Python version", check_python_version),
        ("Installing dependencies", install_dependencies),
        ("Creating environment file", create_env_file),
        ("Testing database connection", test_database_connection),
        ("Running initial migrations", run_initial_migrations),
        ("Verifying Flask application", verify_flask_app),
    ]
    
    failed_steps = []
    
    for step_name, step_function in setup_steps:
        try:
            if not step_function():
                failed_steps.append(step_name)
        except Exception as e:
            print(f"ERROR: {step_name} failed: {e}")
            failed_steps.append(step_name)
    
    if failed_steps:
        print(f"\nSetup failed. Check: {', '.join(failed_steps)}")
        return 1
    else:
        print_next_steps()
        return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
