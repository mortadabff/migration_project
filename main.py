# main.py
"""Pipeline ETL complet : Oracle + MySQL → PostgreSQL"""
import sys
from loguru import logger
from etl.config import Config

# Configuration des logs
logger.remove()
logger.add(sys.stdout, level="INFO", colorize=True,
           format="<green>{time:HH:mm:ss}</green> | <level>{level:<8}</level> | {message}")
logger.add(Config.LOG_FILE, level="DEBUG", rotation="10 MB",
           format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")


def run():
    logger.info(f"🚀 DÉMARRAGE MIGRATION — ENV={Config.ENV}")

    # ─── ÉTAPE 0 : KPIs SOURCE (référence) ────────────────────────────────────
    logger.info("─── ÉTAPE 0 : Calcul KPIs source ───")
    from validation.kpi_source import compute_source_kpis
    kpis_src = compute_source_kpis()

    # ─── ÉTAPE 1 : EXTRACT ────────────────────────────────────────────────────
    logger.info("─── ÉTAPE 1 : Extraction ───")
    from etl.extract_oracle import extract_clients, extract_contrats, extract_pj_oracle
    from etl.extract_mysql import (extract_produits, extract_commandes,
                                    extract_lignes_commande, extract_mouvements,
                                    extract_pj_mysql)

    df_clients_raw  = extract_clients()
    df_contrats_raw = extract_contrats()
    df_pj_ora_raw   = extract_pj_oracle()
    df_produits_raw = extract_produits()
    df_cmd_raw      = extract_commandes()
    df_lignes_raw   = extract_lignes_commande()
    df_mvt_raw      = extract_mouvements()
    df_pj_mys_raw   = extract_pj_mysql()

    # ─── ÉTAPE 2 : TRANSFORM ──────────────────────────────────────────────────
    logger.info("─── ÉTAPE 2 : Transformation ───")
    from etl.transform import (transform_clients, transform_contrats,
                                transform_produits, transform_commandes,
                                transform_mouvements)

    df_clients_t  = transform_clients(df_clients_raw)
    df_produits_t = transform_produits(df_produits_raw)

    # ─── ÉTAPE 3 : LOAD ───────────────────────────────────────────────────────
    logger.info("─── ÉTAPE 3 : Chargement PostgreSQL ───")
    from etl.load_postgres import truncate_all_tables, load_table, fetch_table, log_migration

    truncate_all_tables()

    # Clients (d'abord, pour résoudre FK)
    load_table(df_clients_t, 'clients')
    clients_pg = fetch_table('clients')

    # Contrats (besoin de clients_pg pour FK)
    df_contrats_t = transform_contrats(df_contrats_raw, clients_pg)
    load_table(df_contrats_t, 'contrats')
    contrats_pg = fetch_table('contrats')

    # Produits
    load_table(df_produits_t, 'produits')
    produits_pg = fetch_table('produits')

    # Commandes
    df_cmd_t = transform_commandes(df_cmd_raw, clients_pg, contrats_pg)
    load_table(df_cmd_t, 'commandes')
    commandes_pg = fetch_table('commandes')

    # Lignes commande
    import pandas as pd
    df_lignes_t = df_lignes_raw.rename(columns={'id': 'source_id'})
    fk_cmd = commandes_pg.set_index('source_id')['id'].to_dict()
    fk_prod = produits_pg.set_index('source_id')['id'].to_dict()
    df_lignes_t['commande_id'] = df_lignes_t['commande_id'].map(fk_cmd)
    df_lignes_t['produit_id']  = df_lignes_t['produit_id'].map(fk_prod)
    load_table(df_lignes_t[['commande_id','produit_id','quantite','prix_unitaire','remise_pct','montant_ht']], 'lignes_commande')

    # Mouvements financiers
    df_mvt_t = transform_mouvements(df_mvt_raw, commandes_pg)
    load_table(df_mvt_t, 'mouvements_financiers')

    # ─── ÉTAPE 4 : PIÈCES JOINTES ─────────────────────────────────────────────
    logger.info("─── ÉTAPE 4 : Migration pièces jointes ───")
    from etl.attachments import create_fake_attachments, migrate_all_attachments

    # Créer des fichiers fake pour DEV
    create_fake_attachments(df_pj_ora_raw, Config.ATTACHMENTS_SOURCE)
    create_fake_attachments(df_pj_mys_raw, Config.ATTACHMENTS_SOURCE)

    pj_results = []
    pj_results += migrate_all_attachments(df_pj_ora_raw, 'ORACLE')
    pj_results += migrate_all_attachments(df_pj_mys_raw, 'MYSQL')

    # Charger les résultats PJ dans PostgreSQL
    if pj_results:
        df_pj_pg = pd.DataFrame(pj_results)
        # Ajouter colonnes manquantes
        for col in ['type_mime', 'taille_octets', 'checksum_sha_source', 'chemin_source',
                    'entite_type', 'entite_id']:
            if col not in df_pj_pg.columns:
                df_pj_pg[col] = None
        load_table(df_pj_pg, 'pieces_jointes')

    # ─── ÉTAPE 5 : VALIDATION KPI ─────────────────────────────────────────────
    logger.info("─── ÉTAPE 5 : Validation KPIs ───")
    from validation.kpi_target import compute_target_kpis
    from validation.compare import generate_report

    compute_target_kpis()
    success = generate_report()

    if success:
        logger.success("🟢 MIGRATION TERMINÉE ET VALIDÉE")
    else:
        logger.error("🔴 MIGRATION TERMINÉE AVEC DES ÉCARTS — Vérifier le rapport")
        sys.exit(1)


if __name__ == "__main__":
    run()