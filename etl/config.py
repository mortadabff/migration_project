# etl/config.py
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    ENV = os.getenv('ENV', 'dev')

    # Oracle (simulé via MySQL)
    ORACLE = {
        'host': os.getenv('ORACLE_HOST', 'localhost'),
        'port': int(os.getenv('ORACLE_PORT', 3307)),
        'user': os.getenv('ORACLE_USER', 'oracle_user'),
        'password': os.getenv('ORACLE_PASSWORD', 'oracle_pass'),
        'database': os.getenv('ORACLE_DB', 'oracle_db'),
    }

    # MySQL source
    MYSQL = {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'port': int(os.getenv('MYSQL_PORT', 3306)),
        'user': os.getenv('MYSQL_USER', 'mysql_user'),
        'password': os.getenv('MYSQL_PASSWORD', 'mysql_pass'),
        'database': os.getenv('MYSQL_DB', 'mysql_db'),
    }

    # PostgreSQL cible
    PG = {
        'host': os.getenv('PG_HOST', 'localhost'),
        'port': int(os.getenv('PG_PORT', 5432)),
        'user': os.getenv('PG_USER', 'etl_user'),
        'password': os.getenv('PG_PASSWORD', 'etl_pass'),
        'database': os.getenv('PG_DB', 'migration_db'),
    }

    ATTACHMENTS_SOURCE = os.getenv('ATTACHMENTS_SOURCE_DIR', './attachments/source')
    ATTACHMENTS_DEST   = os.getenv('ATTACHMENTS_DEST_DIR',   './attachments/migrated')
    LOG_FILE           = os.getenv('LOG_FILE', './logs/migration.log')

    @classmethod
    def pg_url(cls) -> str:
        c = cls.PG
        return f"postgresql+psycopg2://{c['user']}:{c['password']}@{c['host']}:{c['port']}/{c['database']}"

    @classmethod
    def mysql_url(cls, db_conf: dict) -> str:
        c = db_conf
        return f"mysql+mysqlconnector://{c['user']}:{c['password']}@{c['host']}:{c['port']}/{c['database']}"