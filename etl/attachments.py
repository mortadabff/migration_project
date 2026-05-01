# etl/attachments.py
"""
Gestion des pièces jointes lors de la migration.
En vrai : copie depuis NAS source → NAS cible.
En DEV : simulation avec création de fichiers fake.
"""
import os
import shutil
import hashlib
from pathlib import Path
from loguru import logger
from etl.config import Config


def create_fake_attachments(pj_df, source_dir: str):
    """Crée de vrais fichiers fake pour tester la migration des PJ."""
    os.makedirs(source_dir, exist_ok=True)
    for _, row in pj_df.iterrows():
        nom = row.get('NOM_FICHIER') or row.get('nom_fichier', 'unknown.pdf')
        filepath = os.path.join(source_dir, nom)
        if not os.path.exists(filepath):
            with open(filepath, 'wb') as f:
                # Fake PDF : contenu aléatoire simulant un vrai fichier
                contenu = f"FAKE PDF - {nom} - MIGRATION TEST\n" * 100
                f.write(contenu.encode())
    logger.info(f"ATTACHMENTS | {len(pj_df)} fichiers fake créés dans {source_dir}")


def compute_sha256(filepath: str) -> str:
    sha256 = hashlib.sha256()
    with open(filepath, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            sha256.update(chunk)
    return sha256.hexdigest()


def migrate_attachment(nom_fichier: str, source_dir: str, dest_dir: str) -> dict:
    """
    Copie un fichier PJ de source → destination et vérifie l'intégrité.
    Retourne : {'statut': 'OK'|'ERREUR'|'MANQUANT', 'checksum_migre': str}
    """
    source_path = os.path.join(source_dir, nom_fichier)
    dest_path   = os.path.join(dest_dir, nom_fichier)

    os.makedirs(dest_dir, exist_ok=True)

    if not os.path.exists(source_path):
        logger.warning(f"ATTACHMENTS | MANQUANT : {nom_fichier}")
        return {'statut': 'MANQUANT', 'checksum_migre': None, 'chemin_migre': None}

    try:
        shutil.copy2(source_path, dest_path)
        checksum_source = compute_sha256(source_path)
        checksum_dest   = compute_sha256(dest_path)

        if checksum_source != checksum_dest:
            logger.error(f"ATTACHMENTS | ❌ Checksum mismatch : {nom_fichier}")
            return {'statut': 'ERREUR', 'checksum_migre': checksum_dest, 'chemin_migre': dest_path}

        logger.success(f"ATTACHMENTS | ✅ {nom_fichier} (SHA256 vérifié)")
        return {'statut': 'OK', 'checksum_migre': checksum_dest, 'chemin_migre': dest_path}

    except Exception as e:
        logger.error(f"ATTACHMENTS | Erreur {nom_fichier} : {e}")
        return {'statut': 'ERREUR', 'checksum_migre': None, 'chemin_migre': None}


def migrate_all_attachments(pj_df, source_systeme: str) -> list:
    """Migre toutes les PJ d'un système source."""
    source_dir = Config.ATTACHMENTS_SOURCE
    dest_dir   = Config.ATTACHMENTS_DEST
    results = []

    col_nom = 'NOM_FICHIER' if 'NOM_FICHIER' in pj_df.columns else 'nom_fichier'
    col_id  = 'PJ_ID' if 'PJ_ID' in pj_df.columns else 'id'

    for _, row in pj_df.iterrows():
        nom_fichier = row[col_nom]
        result = migrate_attachment(nom_fichier, source_dir, dest_dir)
        results.append({
            'source_id':          row[col_id],
            'source_systeme':     source_systeme,
            'nom_fichier':        nom_fichier,
            'statut_migration':   result['statut'],
            'checksum_sha_migre': result['checksum_migre'],
            'chemin_migre':       result['chemin_migre'],
        })

    ok    = sum(1 for r in results if r['statut_migration'] == 'OK')
    manq  = sum(1 for r in results if r['statut_migration'] == 'MANQUANT')
    errs  = sum(1 for r in results if r['statut_migration'] == 'ERREUR')
    logger.info(f"ATTACHMENTS | {source_systeme} → OK:{ok} MANQUANT:{manq} ERREUR:{errs}")
    return results