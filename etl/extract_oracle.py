# etl/extract_oracle.py
import pandas as pd
from sqlalchemy import create_engine, text
from loguru import logger
from etl.config import Config


def get_engine():
    url = Config.mysql_url(Config.ORACLE)  # Oracle simulé via MySQL
    return create_engine(url)


def extract_clients() -> pd.DataFrame:
    logger.info("EXTRACT ORACLE | Clients")
    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql(text("SELECT * FROM CLIENTS_ORA"), conn)
    logger.info(f"EXTRACT ORACLE | {len(df)} clients extraits")
    return df


def extract_contrats() -> pd.DataFrame:
    logger.info("EXTRACT ORACLE | Contrats")
    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql(text("SELECT * FROM CONTRATS_ORA"), conn)
    logger.info(f"EXTRACT ORACLE | {len(df)} contrats extraits")
    return df


def extract_pj_oracle() -> pd.DataFrame:
    logger.info("EXTRACT ORACLE | Pièces jointes")
    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql(text("SELECT * FROM PIECES_JOINTES_ORA"), conn)
    logger.info(f"EXTRACT ORACLE | {len(df)} PJ extraites")
    return df


def extract_kpi_source() -> dict:
    """KPIs de référence côté Oracle (à comparer après migration)."""
    engine = get_engine()
    with engine.connect() as conn:
        kpis = {
            'oracle_clients_total': conn.execute(text("SELECT COUNT(*) FROM CLIENTS_ORA")).scalar(),
            'oracle_clients_actifs': conn.execute(text("SELECT COUNT(*) FROM CLIENTS_ORA WHERE STATUT='ACTIF'")).scalar(),
            'oracle_contrats_total': conn.execute(text("SELECT COUNT(*) FROM CONTRATS_ORA")).scalar(),
            'oracle_contrats_en_cours': conn.execute(text("SELECT COUNT(*) FROM CONTRATS_ORA WHERE STATUT='EN_COURS'")).scalar(),
            'oracle_montant_contrats': float(conn.execute(text("SELECT COALESCE(SUM(MONTANT_HT),0) FROM CONTRATS_ORA WHERE STATUT='EN_COURS'")).scalar()),
            'oracle_pj_total': conn.execute(text("SELECT COUNT(*) FROM PIECES_JOINTES_ORA")).scalar(),
        }
    return kpis