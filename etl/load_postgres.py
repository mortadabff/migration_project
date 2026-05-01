# etl/load_postgres.py
import pandas as pd
from sqlalchemy import create_engine, text
from loguru import logger
from etl.config import Config


def get_engine():
    return create_engine(Config.pg_url())


def truncate_all_tables():
    """Vide toutes les tables cibles dans l'ordre (respect des FK)."""
    engine = get_engine()
    tables = [
        'migration.pieces_jointes',
        'migration.mouvements_financiers',
        'migration.lignes_commande',
        'migration.commandes',
        'migration.produits',
        'migration.contrats',
        'migration.clients',
        'migration.migration_log',
    ]
    with engine.connect() as conn:
        for table in tables:
            conn.execute(text(f"TRUNCATE TABLE {table} RESTART IDENTITY CASCADE"))
        conn.commit()
    logger.info("LOAD | Toutes les tables vidées")


def load_table(df: pd.DataFrame, table: str, schema: str = 'migration') -> int:
    """Charge un DataFrame dans une table PostgreSQL."""
    logger.info(f"LOAD | {schema}.{table} : {len(df)} lignes")
    engine = get_engine()
    df.to_sql(table, engine, schema=schema, if_exists='append', index=False,
              method='multi', chunksize=500)
    logger.success(f"LOAD | ✅ {len(df)} lignes → {schema}.{table}")
    return len(df)


def fetch_table(table: str, schema: str = 'migration') -> pd.DataFrame:
    """Relit une table PostgreSQL (pour résoudre les FK)."""
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql(text(f"SELECT * FROM {schema}.{table}"), conn)


def log_migration(etape: str, table_source: str, nb_source: int,
                  nb_charge: int, nb_erreurs: int = 0,
                  statut: str = 'OK', message: str = ''):
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(text("""
            INSERT INTO migration.migration_log
            (etape, table_source, nb_lignes_source, nb_lignes_chargees, nb_erreurs, statut, message)
            VALUES (:etape, :ts, :ns, :nc, :ne, :st, :msg)
        """), dict(etape=etape, ts=table_source, ns=nb_source, nc=nb_charge,
                   ne=nb_erreurs, st=statut, msg=message))
        conn.commit()