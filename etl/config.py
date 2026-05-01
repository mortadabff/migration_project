# etl/config.py
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _is_running_in_docker() -> bool:
    return Path('/.dockerenv').exists()


def _resolve_db_host(env_name: str, docker_host: str) -> str:
    raw_host = os.getenv(env_name, docker_host)
    if _is_running_in_docker():
        return raw_host
    if raw_host == docker_host:
        return 'localhost'
    return raw_host


def _resolve_db_port(env_name: str, docker_host: str, docker_port: int, host_port: int) -> int:
    raw_port = int(os.getenv(env_name, docker_port))
    raw_host = os.getenv(env_name.replace('_PORT', '_HOST'), docker_host)

    if _is_running_in_docker():
        if raw_host == docker_host and raw_port == host_port:
            return docker_port
        return raw_port

    if raw_host == docker_host and raw_port == docker_port:
        return host_port
    return raw_port

class Config:
    ENV = os.getenv('ENV', 'dev')

    # Oracle (simulé via MySQL)
    ORACLE = {
        'host': _resolve_db_host('ORACLE_HOST', 'oracle_sim'),
        'port': _resolve_db_port('ORACLE_PORT', 'oracle_sim', 3306, 3307),
        'user': os.getenv('ORACLE_USER', 'oracle_user'),
        'password': os.getenv('ORACLE_PASSWORD', 'oracle_pass'),
        'database': os.getenv('ORACLE_DB', 'oracle_db'),
    }

    # MySQL source
    MYSQL = {
        'host': _resolve_db_host('MYSQL_HOST', 'mysql_source'),
        'port': _resolve_db_port('MYSQL_PORT', 'mysql_source', 3306, 3306),
        'user': os.getenv('MYSQL_USER', 'mysql_user'),
        'password': os.getenv('MYSQL_PASSWORD', 'mysql_pass'),
        'database': os.getenv('MYSQL_DB', 'mysql_db'),
    }

    # PostgreSQL cible
    PG = {
        'host': _resolve_db_host('PG_HOST', 'postgres_target'),
        'port': _resolve_db_port('PG_PORT', 'postgres_target', 5432, 5433),
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