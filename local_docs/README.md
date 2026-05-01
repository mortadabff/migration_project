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





-----
-----

# ÉTAPE 10 — Commandes utiles du quotidien

### Rebuild l'image après modification du code
docker compose build etl

### Rebuild sans cache (dépendances changées)
docker compose build --no-cache etl

### Logs d'un conteneur
docker compose logs -f etl
docker compose logs -f postgres_target

### Redémarrer uniquement l'ETL (sans recréer les BDs)
docker compose restart etl

### Arrêter tout proprement
docker compose down

### Tout effacer (volumes inclus = données BDs supprimées)
docker compose down -v

### Exécuter une commande dans le conteneur ETL
docker compose exec etl python -c "from validation.compare import generate_report; generate_report()"

### Voir les KPIs directement dans PostgreSQL
docker compose exec postgres_target psql -U etl_user -d migration_db \
  -c "SET search_path TO migration; SELECT * FROM v_kpi_financier;"

### Inspecter le contenu d'une table
docker compose exec postgres_target psql -U etl_user -d migration_db \
  -c "SET search_path TO migration; SELECT * FROM clients LIMIT 10;"

### Vérifier les logs de migration
docker compose exec postgres_target psql -U etl_user -d migration_db \
  -c "SET search_path TO migration; SELECT * FROM migration_log ORDER BY date_execution DESC;"