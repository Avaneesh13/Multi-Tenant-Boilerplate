#!/usr/bin/env python3
"""
Tenant Migration Runner
This script runs tenant-specific migrations on all tenant databases.
"""

import os
import sys
import importlib.util
from pathlib import Path
import hashlib
from datetime import datetime

# Add the project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

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

def get_tenant_databases():
    """Get list of tenant databases from auth.companies table."""
    from sqlalchemy import create_engine, text
    
    username, password, host, port = get_db_credentials()
    
    def my_create_engine(conn_str, pool_recycle=3600, pool_size=8):
        return create_engine(conn_str, pool_recycle=pool_recycle, pool_size=pool_size)
    
    # Connect to auth database to get tenant list
    auth_conn_str = create_connection_string('auth', username, password, host, port)
    auth_engine = my_create_engine(auth_conn_str)
    
    with auth_engine.connect() as connection:
        result = connection.execute(text("SELECT db_name FROM companies ORDER BY db_name"))
        tenant_dbs = [row[0] for row in result.fetchall()]
    
    return tenant_dbs

def get_tenant_migration_files():
    """Get all migration files from tenant_versions directory."""
    tenant_migrations_dir = project_root / "migrations" / "tenant_versions"
    
    if not tenant_migrations_dir.exists():
        print(f"Tenant migrations directory not found: {tenant_migrations_dir}")
        return []
    
    migration_files = []
    for file_path in tenant_migrations_dir.glob("*.py"):
        if file_path.name != "__init__.py":
            migration_files.append(file_path)
    
    # Sort by filename to ensure proper order
    migration_files.sort()
    return migration_files

def create_migration_tracking_table(tenant_db):
    """Create migration tracking table in tenant database if it doesn't exist."""
    from sqlalchemy import create_engine, text
    
    username, password, host, port = get_db_credentials()
    
    def my_create_engine(conn_str, pool_recycle=3600, pool_size=8):
        return create_engine(conn_str, pool_recycle=pool_recycle, pool_size=pool_size)
    
    tenant_conn_str = create_connection_string(tenant_db, username, password, host, port)
    tenant_engine = my_create_engine(tenant_conn_str)
    
    with tenant_engine.connect() as connection:
        # Create migration tracking table
        connection.execute(text("""
            CREATE TABLE IF NOT EXISTS migration_history (
                id SERIAL PRIMARY KEY,
                migration_file VARCHAR(255) NOT NULL,
                migration_hash VARCHAR(64) NOT NULL,
                applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status VARCHAR(20) DEFAULT 'applied',
                checkpoint_data TEXT
            )
        """))
        connection.commit()

def get_migration_hash(migration_file):
    """Calculate hash of migration file content for tracking."""
    with open(migration_file, 'r') as f:
        content = f.read()
    return hashlib.sha256(content.encode()).hexdigest()

def get_applied_migrations(tenant_db):
    """Get list of applied migrations for a tenant database."""
    from sqlalchemy import create_engine, text
    
    username, password, host, port = get_db_credentials()
    
    def my_create_engine(conn_str, pool_recycle=3600, pool_size=8):
        return create_engine(conn_str, pool_recycle=pool_recycle, pool_size=pool_size)
    
    tenant_conn_str = create_connection_string(tenant_db, username, password, host, port)
    tenant_engine = my_create_engine(tenant_conn_str)
    
    try:
        with tenant_engine.connect() as connection:
            result = connection.execute(text("""
                SELECT migration_file, migration_hash, applied_at 
                FROM migration_history 
                WHERE status = 'applied'
                ORDER BY applied_at
            """))
            return [(row[0], row[1], row[2]) for row in result.fetchall()]
    except Exception:
        # Migration history table doesn't exist yet
        return []

def create_checkpoint(tenant_db, checkpoint_name):
    """Create a checkpoint before running migrations."""
    from sqlalchemy import create_engine, text
    
    username, password, host, port = get_db_credentials()
    
    def my_create_engine(conn_str, pool_recycle=3600, pool_size=8):
        return create_engine(conn_str, pool_recycle=pool_recycle, pool_size=pool_size)
    
    tenant_conn_str = create_connection_string(tenant_db, username, password, host, port)
    tenant_engine = my_create_engine(tenant_conn_str)
    
    with tenant_engine.connect() as connection:
        # Get current database schema info for checkpoint
        result = connection.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name
        """))
        tables = [row[0] for row in result.fetchall()]
        
        checkpoint_data = {
            'timestamp': datetime.now().isoformat(),
            'tables': tables,
            'checkpoint_name': checkpoint_name
        }
        
        # Store checkpoint in migration history
        connection.execute(text("""
            INSERT INTO migration_history (migration_file, migration_hash, status, checkpoint_data)
            VALUES (:checkpoint_name, 'checkpoint', 'checkpoint', :data)
        """), {
            'checkpoint_name': checkpoint_name,
            'data': str(checkpoint_data)
        })
        connection.commit()
        return checkpoint_data

def rollback_to_checkpoint(tenant_db, checkpoint_name):
    """Rollback to a specific checkpoint."""
    from sqlalchemy import create_engine, text
    
    username, password, host, port = get_db_credentials()
    
    def my_create_engine(conn_str, pool_recycle=3600, pool_size=8):
        return create_engine(conn_str, pool_recycle=pool_recycle, pool_size=pool_size)
    
    tenant_conn_str = create_connection_string(tenant_db, username, password, host, port)
    tenant_engine = my_create_engine(tenant_conn_str)
    
    with tenant_engine.connect() as connection:
        # Get checkpoint data
        result = connection.execute(text("""
            SELECT checkpoint_data 
            FROM migration_history 
            WHERE migration_file = :checkpoint_name AND status = 'checkpoint'
            ORDER BY applied_at DESC 
            LIMIT 1
        """), {'checkpoint_name': checkpoint_name})
        
        checkpoint_row = result.fetchone()
        if not checkpoint_row:
            print(f"No checkpoint '{checkpoint_name}' found for {tenant_db}")
            return False
        
        # Mark failed migrations since checkpoint
        connection.execute(text("""
            UPDATE migration_history 
            SET status = 'rolled_back' 
            WHERE applied_at > (
                SELECT applied_at FROM migration_history 
                WHERE migration_file = :checkpoint_name AND status = 'checkpoint'
                ORDER BY applied_at DESC LIMIT 1
            ) AND status = 'applied'
        """), {'checkpoint_name': checkpoint_name})
        
        connection.commit()
        print(f"Rolled back {tenant_db} to checkpoint: {checkpoint_name}")
        return True

def record_migration_success(tenant_db, migration_file, migration_hash):
    """Record successful migration in tracking table."""
    from sqlalchemy import create_engine, text
    
    username, password, host, port = get_db_credentials()
    
    def my_create_engine(conn_str, pool_recycle=3600, pool_size=8):
        return create_engine(conn_str, pool_recycle=pool_recycle, pool_size=pool_size)
    
    tenant_conn_str = create_connection_string(tenant_db, username, password, host, port)
    tenant_engine = my_create_engine(tenant_conn_str)
    
    with tenant_engine.connect() as connection:
        connection.execute(text("""
            INSERT INTO migration_history (migration_file, migration_hash, status)
            VALUES (:file, :hash, 'applied')
        """), {
            'file': migration_file.name,
            'hash': migration_hash
        })
        connection.commit()

def run_tenant_migration(tenant_db, migration_file):
    """Run a specific migration on a tenant database with checkpoint support."""
    from sqlalchemy import create_engine
    from alembic.runtime.migration import MigrationContext
    from alembic.operations import Operations
    
    username, password, host, port = get_db_credentials()
    
    def my_create_engine(conn_str, pool_recycle=3600, pool_size=8):
        return create_engine(conn_str, pool_recycle=pool_recycle, pool_size=pool_size)
    
    migration_hash = get_migration_hash(migration_file)
    applied_migrations = get_applied_migrations(tenant_db)
    
    # Check if migration already applied with same hash
    for applied_file, applied_hash, applied_at in applied_migrations:
        if applied_file == migration_file.name and applied_hash == migration_hash:
            print(f"Skipped {migration_file.name} on {tenant_db} (already applied)")
            return True
    
    # Import the migration file dynamically
    spec = importlib.util.spec_from_file_location("tenant_migration", migration_file)
    tenant_migration = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tenant_migration)
    
    # Connect to the tenant database
    tenant_conn_str = create_connection_string(tenant_db, username, password, host, port)
    tenant_engine = my_create_engine(tenant_conn_str)
    
    try:
        with tenant_engine.connect() as connection:
            # Set up the alembic context for direct execution
            mc = MigrationContext.configure(connection)
            ops = Operations(mc)
            
            # Store the op context for the migration functions
            tenant_migration.op = ops
            
            # Run the migration
            if hasattr(tenant_migration, 'upgrade'):
                tenant_migration.upgrade()
                connection.commit()
                
                # Record successful migration
                record_migration_success(tenant_db, migration_file, migration_hash)
                print(f"Applied {migration_file.name} to {tenant_db}")
                return True
            else:
                print(f"No upgrade function found in {migration_file.name}")
                return False
                
    except Exception as e:
        print(f"ERROR: Failed to apply {migration_file.name} to {tenant_db}: {e}")
        return False

def run_all_tenant_migrations():
    """Run all tenant migrations on all tenant databases with checkpoint recovery."""
    try:
        print("Running tenant migrations with checkpoint recovery...")
        
        # Check credentials
        username, password, host, port = get_db_credentials()
        if not username or not password:
            print("ERROR: Database credentials not configured")
            return False
        
        # Get tenant databases
        tenant_dbs = get_tenant_databases()
        if not tenant_dbs:
            print("No tenant databases found")
            return True
        
        print(f"Found {len(tenant_dbs)} tenant databases: {', '.join(tenant_dbs)}")
        
        # Get migration files
        migration_files = get_tenant_migration_files()
        if not migration_files:
            print("No tenant migration files found")
            return True
        
        print(f"Found {len(migration_files)} migration files")
        
        # Initialize tracking tables on all tenant databases
        print("\nInitializing migration tracking...")
        for tenant_db in tenant_dbs:
            try:
                create_migration_tracking_table(tenant_db)
            except Exception as e:
                print(f"WARNING: Could not initialize tracking for {tenant_db}: {e}")
        
        # Track results
        successful_dbs = []
        failed_dbs = []
        skipped_dbs = []
        
        # Create checkpoint name based on current timestamp
        checkpoint_name = f"pre_migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Run migrations
        for migration_file in migration_files:
            print(f"\nRunning migration: {migration_file.name}")
            
            for tenant_db in tenant_dbs:
                if tenant_db in failed_dbs:
                    print(f"Skipped {tenant_db} (already failed)")
                    continue
                
                try:
                    # Create checkpoint before applying migration
                    create_checkpoint(tenant_db, checkpoint_name)
                    
                    # Apply migration
                    success = run_tenant_migration(tenant_db, migration_file)
                    
                    if success:
                        if tenant_db not in successful_dbs:
                            successful_dbs.append(tenant_db)
                    else:
                        # Migration failed, rollback to checkpoint
                        print(f"Rolling back {tenant_db} to checkpoint...")
                        rollback_to_checkpoint(tenant_db, checkpoint_name)
                        if tenant_db not in failed_dbs:
                            failed_dbs.append(tenant_db)
                            
                except Exception as e:
                    print(f"ERROR: Failed to apply {migration_file.name} to {tenant_db}: {e}")
                    try:
                        # Try to rollback to checkpoint
                        rollback_to_checkpoint(tenant_db, checkpoint_name)
                    except Exception as rollback_error:
                        print(f"ERROR: Could not rollback {tenant_db}: {rollback_error}")
                    
                    if tenant_db not in failed_dbs:
                        failed_dbs.append(tenant_db)
        
        # Print summary
        print(f"\n{'='*60}")
        print("MIGRATION SUMMARY")
        print(f"{'='*60}")
        print(f"Total tenant databases: {len(tenant_dbs)}")
        print(f"Successful migrations: {len(successful_dbs)}")
        print(f"Failed migrations: {len(failed_dbs)}")
        
        if successful_dbs:
            print(f"\nSuccessful databases:")
            for db in successful_dbs:
                print(f"  ✓ {db}")
        
        if failed_dbs:
            print(f"\nFailed databases (rolled back to checkpoint):")
            for db in failed_dbs:
                print(f"  ✗ {db}")
        
        print(f"\nCheckpoint name used: {checkpoint_name}")
        print(f"\nTenant migrations completed!")
        
        return len(failed_dbs) == 0
        
    except Exception as e:
        print(f"ERROR: Tenant migration failed: {e}")
        return False

def show_migration_history():
    """Show migration history for all tenant databases."""
    try:
        tenant_dbs = get_tenant_databases()
        if not tenant_dbs:
            print("No tenant databases found")
            return
        
        print("Migration History")
        print("=" * 60)
        
        for tenant_db in tenant_dbs:
            print(f"\n{tenant_db}:")
            try:
                applied_migrations = get_applied_migrations(tenant_db)
                if applied_migrations:
                    for migration_file, migration_hash, applied_at in applied_migrations:
                        print(f"  ✓ {migration_file} ({applied_at})")
                else:
                    print("  No migrations applied")
            except Exception as e:
                print(f"  ERROR: Could not read history: {e}")
    except Exception as e:
        print(f"ERROR: Could not show migration history: {e}")

def main():
    """Main function."""
    print("Tenant Migration Runner")
    print("=" * 50)
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "--list":
            # List tenant databases
            try:
                tenant_dbs = get_tenant_databases()
                print(f"Tenant databases ({len(tenant_dbs)}):")
                for db in tenant_dbs:
                    print(f"  - {db}")
            except Exception as e:
                print(f"ERROR: Could not list tenant databases: {e}")
            return
        elif sys.argv[1] == "--history":
            # Show migration history
            show_migration_history()
            return
        elif sys.argv[1] == "--help":
            print("Usage:")
            print("  python run_tenant_migrations.py           # Run all tenant migrations")
            print("  python run_tenant_migrations.py --list    # List all tenant databases")
            print("  python run_tenant_migrations.py --history # Show migration history")
            print("  python run_tenant_migrations.py --help    # Show this help")
            return
    
    # Run migrations
    success = run_all_tenant_migrations()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main() 