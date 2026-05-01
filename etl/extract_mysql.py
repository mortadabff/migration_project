# etl/extract_mysql.py
import pandas as pd
from sqlalchemy import create_engine, text
from loguru import logger
from etl.config import Config


def get_engine():
    return create_engine(Config.mysql_url(Config.MYSQL))


def extract_produits() -> pd.DataFrame:
    logger.info("EXTRACT MYSQL | Produits")
    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql(text("SELECT * FROM produits"), conn)
    logger.info(f"EXTRACT MYSQL | {len(df)} produits extraits")
    return df


def extract_commandes() -> pd.DataFrame:
    logger.info("EXTRACT MYSQL | Commandes")
    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql(text("SELECT * FROM commandes"), conn)
    logger.info(f"EXTRACT MYSQL | {len(df)} commandes extraites")
    return df


def extract_lignes_commande() -> pd.DataFrame:
    logger.info("EXTRACT MYSQL | Lignes commande")
    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql(text("SELECT * FROM lignes_commande"), conn)
    logger.info(f"EXTRACT MYSQL | {len(df)} lignes extraites")
    return df


def extract_mouvements() -> pd.DataFrame:
    logger.info("EXTRACT MYSQL | Mouvements financiers")
    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql(text("SELECT * FROM mouvements_financiers"), conn)
    logger.info(f"EXTRACT MYSQL | {len(df)} mouvements extraits")
    return df


def extract_pj_mysql() -> pd.DataFrame:
    logger.info("EXTRACT MYSQL | Pièces jointes")
    engine = get_engine()
    with engine.connect() as conn:
        df = pd.read_sql(text("SELECT * FROM pieces_jointes_mysql"), conn)
    logger.info(f"EXTRACT MYSQL | {len(df)} PJ extraites")
    return df


def extract_kpi_source() -> dict:
    engine = get_engine()
    with engine.connect() as conn:
        kpis = {
            'mysql_commandes_total': conn.execute(text("SELECT COUNT(*) FROM commandes")).scalar(),
            'mysql_commandes_livrees': conn.execute(text("SELECT COUNT(*) FROM commandes WHERE statut='LIVREE'")).scalar(),
            'mysql_montant_total_ht': float(conn.execute(text("SELECT COALESCE(SUM(montant_ht),0) FROM commandes WHERE statut != 'ANNULEE'")).scalar()),
            'mysql_ca_encaisse': float(conn.execute(text("SELECT COALESCE(SUM(montant),0) FROM mouvements_financiers WHERE type_mouvement='PAIEMENT' AND statut='VALIDE'")).scalar()),
            'mysql_pj_total': conn.execute(text("SELECT COUNT(*) FROM pieces_jointes_mysql")).scalar(),
        }
    return kpis