import os
from flask import Flask, jsonify
from sqlalchemy import create_engine, text
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Environment variables
env = os.environ

def my_create_engine(conn_str, pool_recycle=3600, pool_size=8):
    return create_engine(conn_str, pool_recycle=pool_recycle, pool_size=pool_size)

def get_db_credentials():
    """Get database credentials from environment variables."""
    username = env.get('DB_USERNAME')
    password = env.get('DB_PASSWORD')
    host = env.get('DB_HOST', 'localhost')
    port = env.get('DB_PORT', '5432')
    return username, password, host, port

def create_connection_string(db_name, username, password, host, port):
    """Create a PostgreSQL connection string for the specified database."""
    return f"postgresql://{username}:{password}@{host}:{port}/{db_name}"

# Database connection - use postgres database for timestamp queries
username, password, host, port = get_db_credentials()
if username and password:
    POSTGRES_CONN_STR = create_connection_string('postgres', username, password, host, port)
    AUTH_ENGINE = my_create_engine(POSTGRES_CONN_STR)
else:
    # Fallback to old ADMIN_CONN_STR for backward compatibility
    ADMIN_CONN_STR = env.get('ADMIN_CONN_STR')
    if ADMIN_CONN_STR:
        AUTH_ENGINE = my_create_engine(ADMIN_CONN_STR)
    else:
        AUTH_ENGINE = None

@app.route('/')
def home():
    return jsonify({
        'message': 'Flask PostgreSQL Timestamp Server',
        'status': 'running'
    })

@app.route('/timestamp')
def get_timestamp():
    try:
        # Query the current timestamp from the database
        with AUTH_ENGINE.connect() as connection:
            result = connection.execute(text("SELECT NOW() as current_timestamp"))
            timestamp = result.fetchone()[0]
            
            return jsonify({
                'timestamp': timestamp.isoformat(),
                'source': 'postgresql_database',
                'status': 'success'
            })
    except Exception as e:
        logger.error(f"Database error: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve timestamp from database',
            'details': str(e),
            'status': 'error'
        }), 500

@app.route('/health')
def health_check():
    try:
        # Test database connection
        with AUTH_ENGINE.connect() as connection:
            connection.execute(text("SELECT 1"))
            
        return jsonify({
            'status': 'healthy',
            'database': 'connected',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'database': 'disconnected',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }), 503

@app.route('/databases')
def list_databases():
    try:
        with AUTH_ENGINE.connect() as connection:
            # Query all non-template databases
            result = connection.execute(text("""
                SELECT datname 
                FROM pg_database 
                WHERE datistemplate = false 
                AND datname NOT IN ('postgres') 
                ORDER BY datname
            """))
            
            databases = [row[0] for row in result.fetchall()]
            
            # Categorize databases
            system_dbs = []
            tenant_dbs = []
            
            for db_name in databases:
                if db_name in ['auth', 'constants']:
                    system_dbs.append(db_name)
                elif db_name.startswith('db_'):
                    tenant_dbs.append(db_name)
                else:
                    system_dbs.append(db_name)
            
            return jsonify({
                'databases': {
                    'system': system_dbs,
                    'tenants': tenant_dbs,
                    'total_count': len(databases)
                },
                'status': 'success'
            })
            
    except Exception as e:
        logger.error(f"Database listing error: {str(e)}")
        return jsonify({
            'error': 'Failed to retrieve database list',
            'details': str(e),
            'status': 'error'
        }), 500

if __name__ == '__main__':
    # Verify database configuration is available
    if AUTH_ENGINE is None:
        logger.error("Database connection not configured. Please set DB_USERNAME, DB_PASSWORD, DB_HOST, DB_PORT or ADMIN_CONN_STR environment variables")
        exit(1)
    
    logger.info("Starting Flask server...")
    app.run(host='0.0.0.0', port=5000, debug=True) 