# validation/kpi_source.py
"""Calcule et sauvegarde les KPIs AVANT migration (référence)."""
import json
from loguru import logger
from etl.extract_oracle import extract_kpi_source as oracle_kpis
from etl.extract_mysql import extract_kpi_source as mysql_kpis


def compute_source_kpis() -> dict:
    logger.info("KPI SOURCE | Calcul des KPIs de référence")
    ora = oracle_kpis()
    mys = mysql_kpis()
    all_kpis = {**ora, **mys}
    all_kpis['source_pj_total'] = int(ora.get('oracle_pj_total', 0)) + int(mys.get('mysql_pj_total', 0))
    logger.info(f"KPI SOURCE | {json.dumps(all_kpis, indent=2)}")

    # Sauvegarder pour comparaison ultérieure
    with open('logs/kpi_source.json', 'w') as f:
        json.dump(all_kpis, f, indent=2)

    return all_kpis


if __name__ == "__main__":
    compute_source_kpis()