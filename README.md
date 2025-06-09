# Flask PostgreSQL Multi-Tenant Boilerplate

🚀 **Production-ready boilerplate** for building multi-tenant Flask applications with PostgreSQL, featuring database-per-tenant isolation, advanced migration management, and checkpoint-based recovery.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![PostgreSQL 12+](https://img.shields.io/badge/postgresql-12+-blue.svg)](https://www.postgresql.org/)

## ✨ Features

- 🏢 **Database-per-tenant architecture** with complete data isolation
- 🔄 **Advanced migration management** with system/tenant separation
- 🛡️ **Checkpoint-based recovery** with automatic rollback on failures
- 📊 **Migration tracking** with hash verification and duplicate prevention
- 🔧 **One-command setup** with automated database initialization
- 📱 **RESTful API** with health monitoring and database listing
- 🔒 **Connection pooling** with configurable pool size and recycling
- 📝 **Comprehensive logging** and error handling
- 🎯 **Production-ready** with best practices built-in

## 🎯 Use Cases

Perfect for building:
- **SaaS applications** with tenant isolation
- **Multi-client platforms** with separate data stores
- **Enterprise applications** requiring data segregation
- **B2B software** with customer-specific databases
- **Compliance-focused systems** needing data isolation

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **PostgreSQL 12+**
- **Git**

### One-Command Setup (Recommended)
Run the automated setup script:
```bash
python scripts/run_migrations/run_initial_setup.py
```

This script will:
- Check Python version compatibility
- Install all required dependencies
- Create a `.env` file template
- Test database connection (if configured)
- Create system databases (auth, constants) and run their migrations
- Create tenant databases and register them in auth.companies
- Verify Flask application setup

### Tenant Migrations
Tenant-specific migrations are stored separately in `migrations/tenant_versions/` and run using:
```bash
python scripts/run_migrations/run_tenant_migrations.py
```

This script will:
- Find all tenant databases from the auth.companies table
- Apply all migrations from tenant_versions/ to each tenant database
- Handle errors gracefully and continue with other tenants

List tenant databases:
```bash
python scripts/run_migrations/run_tenant_migrations.py --list
```

### Alternative Manual Setup

1. **Clone the repository:**
```bash
git clone https://github.com/Avaneesh13/Multi-Tenant-Boilerplate.git
cd flask-postgresql-multi-tenant
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Create a `.env` file** with your database credentials:
```bash
# Copy the example file and configure
cp env.example .env
# Edit .env with your actual database credentials
```

**Required environment variables:**
```bash
DB_USERNAME=your_postgresql_username
DB_PASSWORD=your_postgresql_password
DB_HOST=localhost
DB_PORT=5432
```

See [`env.example`](env.example) for a complete configuration template with all available options.

**Legacy Support**: The old `ADMIN_CONN_STR` format is still supported for backward compatibility.

## Running the Server

```bash
python app.py
```

The server will start on `http://localhost:5000`

## Database Architecture

The system creates a multi-tenant architecture with:

- **System Databases:**
  - `auth` - User and company management
  - `constants` - Shared application constants (currencies, etc.)

- **Tenant Databases:**
  - `db_xxxxxxxxxx` - Individual tenant databases with isolated data
  - Each tenant is registered in `auth.companies` table

## Migration Management

### System Migrations
System migrations (auth, constants databases) are stored in `migrations/versions/` and managed by standard Alembic commands.

**Generate system migration:**
```bash
alembic revision -m "add new system feature" --version-path migrations/versions
```

**Run system migrations:**
```bash
alembic upgrade head  # Automatically excludes tenant migrations
```

### Tenant Migrations
Tenant migrations are stored separately in `migrations/tenant_versions/` and run using a custom script with checkpoint-based recovery.

**Generate tenant migration:**
```bash
alembic revision -m "add tenant feature" --version-path migrations/tenant_versions
```

**Run tenant migrations:**
```bash
python scripts/run_migrations/run_tenant_migrations.py  # Run all migrations with checkpoint recovery
python scripts/run_migrations/run_tenant_migrations.py --list     # List all tenant databases
python scripts/run_migrations/run_tenant_migrations.py --history  # Show migration history
python scripts/run_migrations/run_tenant_migrations.py --help     # Show help
```

**Note:** The system is configured to automatically exclude tenant migrations when running `alembic upgrade head`, ensuring tenant migrations only run on tenant databases via the custom script.

### Checkpoint-Based Recovery System

The tenant migration system includes advanced recovery features for data safety:

**Key Features:**
- **Automatic Checkpoints**: Creates restore points before each migration batch
- **Migration Tracking**: Tracks migrations with hash verification to prevent duplicates  
- **Automatic Rollback**: Failed migrations trigger automatic rollback to last checkpoint
- **Failure Isolation**: Failed migrations on one tenant don't affect others
- **Comprehensive Reporting**: Detailed summary shows successful and failed databases

**Recovery Process:**
1. Initialize migration tracking tables on all tenant databases
2. Create timestamped checkpoint before applying migrations
3. Apply migrations sequentially with content hash verification
4. On failure: automatically rollback to checkpoint and mark migrations as rolled back
5. Continue with remaining tenant databases unaffected
6. Provide detailed summary including list of failed databases

**Example Output:**
```
============================================================
MIGRATION SUMMARY
============================================================
Total tenant databases: 5
Successful migrations: 4
Failed migrations: 1

Successful databases:
  ✓ db_a1b2c3d4e5
  ✓ db_f6g7h8i9j0
  ✓ db_k1l2m3n4o5
  ✓ db_p6q7r8s9t0

Failed databases (rolled back to checkpoint):
  ✗ db_u1v2w3x4y5

Checkpoint name used: pre_migration_20231215_143022
```

The tenant migration script automatically:
- Discovers all tenant databases from `auth.companies`
- Creates migration history tracking tables
- Applies all migrations from `tenant_versions/` to each tenant database
- Creates checkpoints and handles rollbacks on failures
- Provides detailed success/failure reporting

### Recovery from Failed Migrations

**Scenario**: If 1 out of 5 tenant databases fails during migration:

**What happens automatically:**
1. **Failed database**: Automatically rolled back to checkpoint (safe, pre-migration state)
2. **Successful databases**: Keep their applied migrations (no impact)
3. **Detailed report**: Shows exactly which database failed and which succeeded

**Recovery steps:**
1. **Investigate the failure**:
   ```bash
   # Check which database failed from the migration summary
   # Example output showed: db_u1v2w3x4y5 failed
   
   # Inspect the failed database
   python scripts/run_migrations/run_tenant_migrations.py --history
   ```

2. **Fix the underlying issue**:
   - Data corruption or conflicts
   - Schema inconsistencies  
   - Permission problems
   - Resource constraints

3. **Rerun migrations** (safe and automatic):
   ```bash
   # Simply rerun the migration script
   python scripts/run_migrations/run_tenant_migrations.py
   ```

**Smart Recovery Features:**
- ✅ **Automatic Skip**: Already-migrated databases are automatically skipped (hash verification)
- ✅ **Only Failed DBs**: Only attempts migration on databases that need it
- ✅ **New Checkpoints**: Creates fresh checkpoints for the retry
- ✅ **No Duplicates**: Hash verification prevents duplicate migration applications
- ✅ **Safe Retry**: Failed databases start from clean checkpoint state

**Example Recovery Output:**
```
============================================================
MIGRATION SUMMARY
============================================================
Total tenant databases: 5
Successful migrations: 5  # Now all succeed!
Failed migrations: 0

Successful databases:
  ✓ db_a1b2c3d4e5 (skipped - already applied)
  ✓ db_f6g7h8i9j0 (skipped - already applied)  
  ✓ db_k1l2m3n4o5 (skipped - already applied)
  ✓ db_p6q7r8s9t0 (skipped - already applied)
  ✓ db_u1v2w3x4y5 (newly applied after fix)

Checkpoint name used: pre_migration_20231215_151545
```

**Key Benefits:**
- 🔄 **No manual tracking** of which databases succeeded/failed
- 🛡️ **Safe retries** with automatic duplicate prevention  
- ⚡ **Fast recovery** - only processes databases that need it
- 📊 **Clear reporting** shows exactly what happened

## API Endpoints

### GET /
Returns basic server information.

### GET /timestamp
Queries the current timestamp from the PostgreSQL database.

### GET /health
Health check endpoint that tests database connectivity.

### GET /databases
Lists all databases categorized by type (system vs tenant databases).

**Response format:**
```json
{
  "databases": {
    "system": ["auth", "constants"],
    "tenants": ["db_a1b2c3d4e5", "db_f6g7h8i9j0", "db_k1l2m3n4o5"],
    "total_count": 5
  },
  "status": "success"
}
```

## 🏗️ Architecture

### Database Structure
- **System Databases**: `auth` (users, companies), `constants` (shared data)
- **Tenant Databases**: `db_xxxxxxxxxx` (isolated tenant data)
- **Complete Isolation**: Each tenant has a dedicated database

### Migration System
- **System Migrations**: Managed by Alembic in `migrations/versions/`
- **Tenant Migrations**: Separate management in `migrations/tenant_versions/`
- **Checkpoint Recovery**: Automatic rollback on migration failures
- **Hash Verification**: Prevents duplicate migration applications

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

### Quick Contribution Steps
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🌟 Show Your Support

If this boilerplate helped you, please consider:
- ⭐ Starring the repository
- 🐛 Reporting issues
- 💡 Suggesting enhancements
- 🤝 Contributing code
- 📢 Sharing with others

## 📚 Additional Resources

- **[Contributing Guide](CONTRIBUTING.md)** - How to contribute
- **[Issue Templates](.github/ISSUE_TEMPLATE/)** - Report bugs or request features
- **[Discussions](https://github.com/Avaneesh13/Multi-Tenant-Boilerplate/discussions)** - Community support

## 🔧 Advanced Features

- **Multi-Tenant Architecture**: Complete database-per-tenant isolation
- **Advanced Migration Management**: System vs tenant migration separation
- **Checkpoint-Based Recovery**: Automatic rollback on failures
- **Connection Pooling**: Configurable pool size (default: 8)
- **Connection Recycling**: Default 3600 seconds
- **Comprehensive Error Handling**: Graceful failure management
- **Health Monitoring**: Database connectivity and listing endpoints
- **RESTful API Design**: JSON responses with proper HTTP codes
- **Legacy Compatibility**: Supports old connection string formats 