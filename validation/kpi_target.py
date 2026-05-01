# validation/kpi_target.py
"""Calcule les KPIs APRÈS migration dans PostgreSQL."""
import json
from sqlalchemy import create_engine, text
from loguru import logger
from etl.config import Config


def compute_target_kpis() -> dict:
    logger.info("KPI TARGET | Calcul des KPIs post-migration")
    engine = create_engine(Config.pg_url())

    with engine.connect() as conn:
        def q(sql): return conn.execute(text(sql)).scalar() or 0

        kpis = {
            # Clients
            'pg_clients_total':        q("SELECT COUNT(*) FROM migration.clients"),
            'pg_clients_actifs':       q("SELECT COUNT(*) FROM migration.clients WHERE statut='ACTIVE'"),
            'pg_clients_oracle':       q("SELECT COUNT(*) FROM migration.clients WHERE source_systeme='ORACLE'"),

            # Contrats
            'pg_contrats_total':       q("SELECT COUNT(*) FROM migration.contrats"),
            'pg_contrats_en_cours':    q("SELECT COUNT(*) FROM migration.contrats WHERE statut='EN_COURS'"),
            'pg_montant_contrats':     float(q("SELECT COALESCE(SUM(montant_ht),0) FROM migration.contrats WHERE statut='EN_COURS'")),

            # Commandes
            'pg_commandes_total':      q("SELECT COUNT(*) FROM migration.commandes"),
            'pg_commandes_livrees':    q("SELECT COUNT(*) FROM migration.commandes WHERE statut='LIVREE'"),
            'pg_montant_cmd_ht':       float(q("SELECT COALESCE(SUM(montant_ht),0) FROM migration.commandes WHERE statut!='ANNULEE'")),

            # Financier
            'pg_ca_encaisse':          float(q("SELECT COALESCE(SUM(montant),0) FROM migration.mouvements_financiers WHERE type_mouvement='PAIEMENT' AND statut='VALIDE'")),

            # Pièces jointes
            'pg_pj_total':             q("SELECT COUNT(*) FROM migration.pieces_jointes"),
            'pg_pj_ok':                q("SELECT COUNT(*) FROM migration.pieces_jointes WHERE statut_migration='OK'"),
            'pg_pj_manquant':          q("SELECT COUNT(*) FROM migration.pieces_jointes WHERE statut_migration='MANQUANT'"),
            'pg_pj_erreur':            q("SELECT COUNT(*) FROM migration.pieces_jointes WHERE statut_migration='ERREUR'"),

            # Qualité
            'pg_clients_email_null':   q("SELECT COUNT(*) FROM migration.clients WHERE email IS NULL"),
            'pg_commandes_sans_client':q("SELECT COUNT(*) FROM migration.commandes WHERE client_id IS NULL"),
        }

    with open('logs/kpi_target.json', 'w') as f:
        json.dump(kpis, f, indent=2)

    return kpis


if __name__ == "__main__":
    compute_target_kpis()