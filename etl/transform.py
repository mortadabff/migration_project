# etl/transform.py
import pandas as pd
from loguru import logger


# ── Mapping des statuts ────────────────────────────────────────────────────────
STATUT_CLIENT_MAP = {
    'ACTIF': 'ACTIVE', 'actif': 'ACTIVE',
    'INACTIF': 'INACTIVE', 'inactif': 'INACTIVE',
    'ARCHIVE': 'ARCHIVED', 'archive': 'ARCHIVED',
}

STATUT_CONTRAT_MAP = {
    'EN_COURS': 'EN_COURS',
    'TERMINE': 'TERMINE',
    'RESILIE': 'RESILIE',
}

STATUT_COMMANDE_MAP = {
    'EN_ATTENTE': 'EN_ATTENTE',
    'VALIDEE': 'VALIDEE',
    'EN_COURS': 'EN_COURS',
    'LIVREE': 'LIVREE',
    'ANNULEE': 'ANNULEE',
    'LITIGIEUX': 'LITIGIEUX',
}


def transform_clients(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("TRANSFORM | Clients Oracle")
    df = df.copy()

    # Renommer colonnes (Oracle UPPERCASE → snake_case)
    df.columns = [c.lower() for c in df.columns]
    rename_map = {
        'client_id': 'source_id',
        'date_creation': 'date_creation_source',
        'date_maj': 'date_maj_source',
    }
    df = df.rename(columns=rename_map)

    # Normalisation
    df['email'] = df['email'].str.lower().str.strip()
    df['nom'] = df['nom'].str.strip().str.title()
    df['prenom'] = df['prenom'].str.strip().str.title()
    df['statut'] = df['statut'].map(STATUT_CLIENT_MAP).fillna('UNKNOWN')
    df['source_systeme'] = 'ORACLE'

    # Supprimer doublons email
    avant = len(df)
    df = df.drop_duplicates(subset='email', keep='first')
    if avant != len(df):
        logger.warning(f"TRANSFORM | {avant - len(df)} doublons email supprimés (clients Oracle)")

    cols_cibles = ['source_id', 'source_systeme', 'nom', 'prenom', 'email',
                   'telephone', 'date_naissance', 'statut', 'code_pays', 'date_creation_source']
    return df[cols_cibles]


def transform_contrats(df: pd.DataFrame, clients_pg: pd.DataFrame) -> pd.DataFrame:
    """Transforme les contrats et résout le FK client_id vers la table cible."""
    logger.info("TRANSFORM | Contrats Oracle")
    df = df.copy()
    df.columns = [c.lower() for c in df.columns]
    df = df.rename(columns={'contrat_id': 'source_id'})

    df['statut'] = df['statut'].map(STATUT_CONTRAT_MAP).fillna(df['statut'])

    # Résolution FK : client_id Oracle → client_id PostgreSQL
    fk_map = clients_pg.set_index('source_id')['id'].to_dict()
    df['client_id'] = df['client_id'].map(fk_map)
    df['taux_tva'] = df['taux_tva'].fillna(20.0)

    cols_cibles = ['source_id', 'client_id', 'numero', 'type_contrat',
                   'montant_ht', 'taux_tva', 'date_debut', 'date_fin', 'statut', 'devise']
    return df[cols_cibles]


def transform_produits(df: pd.DataFrame) -> pd.DataFrame:
    logger.info("TRANSFORM | Produits MySQL")
    df = df.copy()
    df = df.rename(columns={'id': 'source_id'})
    df['actif'] = df['actif'].astype(bool)
    cols_cibles = ['source_id', 'reference', 'designation', 'categorie', 'prix_unitaire', 'unite', 'actif']
    return df[cols_cibles]


def transform_commandes(df: pd.DataFrame, clients_pg: pd.DataFrame, contrats_pg: pd.DataFrame) -> pd.DataFrame:
    logger.info("TRANSFORM | Commandes MySQL")
    df = df.copy()
    df = df.rename(columns={'id': 'source_id'})
    df['statut'] = df['statut'].map(STATUT_COMMANDE_MAP).fillna(df['statut'])

    # Résolution FK client
    fk_clients = clients_pg.set_index('source_id')['id'].to_dict()
    df['client_id'] = df['client_id_ext'].map(fk_clients)

    # Résolution FK contrat via numéro
    fk_contrats = contrats_pg.set_index('numero')['id'].to_dict()
    df['contrat_id'] = df['contrat_ref'].map(fk_contrats)

    cols_cibles = ['source_id', 'numero', 'client_id', 'contrat_id',
                   'date_commande', 'date_livraison', 'statut',
                   'montant_ht', 'montant_ttc', 'devise', 'commentaire']
    return df[cols_cibles]


def transform_mouvements(df: pd.DataFrame, commandes_pg: pd.DataFrame) -> pd.DataFrame:
    logger.info("TRANSFORM | Mouvements financiers MySQL")
    df = df.copy()
    df = df.rename(columns={'id': 'source_id'})

    fk_cmd = commandes_pg.set_index('source_id')['id'].to_dict()
    df['commande_id'] = df['commande_id'].map(fk_cmd)

    cols_cibles = ['source_id', 'commande_id', 'type_mouvement', 'reference',
                   'montant', 'devise', 'date_mouvement', 'statut',
                   'mode_paiement', 'date_valeur', 'commentaire']
    return df[cols_cibles]