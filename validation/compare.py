# validation/compare.py
"""Rapport de comparaison KPI source vs cible."""
import json
from datetime import datetime
from tabulate import tabulate
from loguru import logger


def generate_report() -> bool:
    with open('logs/kpi_source.json') as f:
        source = json.load(f)
    with open('logs/kpi_target.json') as f:
        target = json.load(f)

    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    # Définition des contrôles : (label, kpi_source, kpi_target, tolérance)
    checks = [
        # Clients
        ("Clients total",          'oracle_clients_total',    'pg_clients_total',        0),
        ("Clients actifs",         'oracle_clients_actifs',   'pg_clients_actifs',       0),
        # Contrats
        ("Contrats total",         'oracle_contrats_total',   'pg_contrats_total',       0),
        ("Contrats en cours",      'oracle_contrats_en_cours','pg_contrats_en_cours',    0),
        ("Montant contrats (€)",   'oracle_montant_contrats', 'pg_montant_contrats',     0.01),
        # Commandes
        ("Commandes total",        'mysql_commandes_total',   'pg_commandes_total',      0),
        ("Commandes livrées",      'mysql_commandes_livrees', 'pg_commandes_livrees',    0),
        ("CA encaissé (€)",        'mysql_ca_encaisse',       'pg_ca_encaisse',          0.01),
        # PJ
        ("PJ total",               'source_pj_total',         'pg_pj_total',             0),
    ]

    rows = []
    errors = []

    for label, key_src, key_tgt, tol in checks:
        val_s = source.get(key_src, 'N/A')
        val_t = target.get(key_tgt, 'N/A')

        if val_s == 'N/A' or val_t == 'N/A':
            statut = "⚠️  N/A"
        else:
            ok = abs(float(val_s) - float(val_t)) <= tol
            statut = "✅ OK" if ok else "❌ KO"
            if not ok:
                errors.append(f"{label}: source={val_s} | cible={val_t}")

        rows.append([label, val_s, val_t, statut])

    # Contrôles qualité PJ
    pj_ok      = target.get('pg_pj_ok', 0)
    pj_manq    = target.get('pg_pj_manquant', 0)
    pj_erreur  = target.get('pg_pj_erreur', 0)
    pj_total   = target.get('pg_pj_total', 0)

    rapport = [
        "",
        "=" * 70,
        f"  RAPPORT DE VALIDATION MIGRATION — {timestamp}",
        "=" * 70,
        "",
        tabulate(rows, headers=["KPI", "Source", "Cible", "Statut"], tablefmt="rounded_grid"),
        "",
        "─── PIÈCES JOINTES ─────────────────────────────────────────────────",
        f"  Total PJ      : {pj_total}",
        f"  ✅ OK         : {pj_ok}",
        f"  ⚠️  Manquantes : {pj_manq}",
        f"  ❌ Erreurs    : {pj_erreur}",
        "",
        "─── QUALITÉ DONNÉES ────────────────────────────────────────────────",
        f"  Clients email NULL   : {target.get('pg_clients_email_null', 'N/A')}",
        f"  Commandes sans client: {target.get('pg_commandes_sans_client', 'N/A')}",
        "",
        "=" * 70,
    ]

    if errors:
        rapport.append(f"  🔴 MIGRATION KO — {len(errors)} ÉCART(S) DÉTECTÉ(S)")
        for e in errors:
            rapport.append(f"     → {e}")
    else:
        rapport.append("  🟢 MIGRATION VALIDÉE — TOUS LES KPIs SONT OK")

    rapport.append("=" * 70)

    rapport_str = "\n".join(rapport)
    print(rapport_str)

    with open('logs/rapport_validation.log', 'w', encoding='utf-8') as f:
        f.write(rapport_str)
    logger.success("Rapport sauvegardé : logs/rapport_validation.log")

    return len(errors) == 0


if __name__ == "__main__":
    success = generate_report()
    exit(0 if success else 1)