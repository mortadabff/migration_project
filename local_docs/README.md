# Workflow complet DEV → RECETTE → PROD

┌─────────────────────────────────────────────────────────────────┐
│  DEV (local)                                                    │
│  docker compose up                                              │
│  → Données fake                                                 │
│  → Tests ETL                                                    │
│  → Tests validation                                             │
│  → git commit + push                                            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  RECETTE (serveur recette)                                      │
│  git pull                                                       │
│  docker build -t migration:recette .                            │
│  docker compose --env-file .env.recette up etl                 │
│  → Données réalistes (subset prod)                              │
│  → Validation métier                                            │
│  → Validation PJ                                                │
│  → Go/NoGo                                                      │
└────────────────────────┬────────────────────────────────────────┘
                         │  ✅ Go
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│  PROD                                                           │
│  docker run -e ENV=prod --env-file .env.prod migration:recette  │
│  → Même image qu'en recette (!)                                 │
│  → Vraies données                                               │
│  → Rapport validation → archivage → décommissionnement          │
└─────────────────────────────────────────────────────────────────┘

# Démarrer en local
### 1. Démarrer toutes les BDs
docker compose up -d oracle_sim mysql_source postgres_target

### 2. Attendre que les healthchecks soient OK (environ 30 secondes)
docker compose ps
#### → Toutes les colonnes "Status" doivent afficher "healthy"

### 3. Lancer le pipeline ETL
docker compose up etl

#### OU en mode interactif (pour débugger)
docker compose run --rm etl bash
#### Puis dans le conteneur :
python main.py

### 4. Voir les logs en temps réel
tail -f logs/migration.log

### 5. Voir le rapport de validation
cat logs/rapport_validation.log

### 6. Se connecter à PostgreSQL pour vérifier
docker exec -it postgres_target psql -U etl_user -d migration_db
#### Dans psql :
SET search_path TO migration;
SELECT * FROM v_kpi_financier;
SELECT * FROM migration_log ORDER BY date_execution;




----------------------
#  Passer de DEV → RECETTE → PROD

### ─── DEV (par défaut) ─────────────────────────────────────────────
docker compose up                          # Utilise .env

### ─── RECETTE ──────────────────────────────────────────────────────
docker compose --env-file .env.recette up etl

### ─── PROD ─────────────────────────────────────────────────────────
docker compose --env-file .env.prod up etl

### OU via variable d'environnement shell
ENV=recette docker compose up etl



