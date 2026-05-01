-- sql/postgres/init_postgres.sql
-- Tables cibles unifiées (fusion Oracle + MySQL)

CREATE SCHEMA IF NOT EXISTS migration;
SET search_path TO migration;

-- ─── CLIENTS (fusion Oracle) ──────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS clients (
    id                  SERIAL PRIMARY KEY,
    source_id           INTEGER NOT NULL,          -- ID dans la source
    source_systeme      VARCHAR(20) NOT NULL,      -- 'ORACLE' | 'MYSQL'
    nom                 VARCHAR(100) NOT NULL,
    prenom              VARCHAR(100),
    email               VARCHAR(200) UNIQUE,
    telephone           VARCHAR(20),
    date_naissance      DATE,
    statut              VARCHAR(20),               -- ACTIVE | INACTIVE | ARCHIVED
    code_pays           VARCHAR(3),
    date_creation_source TIMESTAMP,
    date_migration      TIMESTAMP DEFAULT NOW(),
    UNIQUE (source_id, source_systeme)
);

-- ─── CONTRATS ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS contrats (
    id                  SERIAL PRIMARY KEY,
    source_id           INTEGER NOT NULL,
    client_id           INTEGER REFERENCES clients(id),
    numero              VARCHAR(50) UNIQUE NOT NULL,
    type_contrat        VARCHAR(30),
    montant_ht          NUMERIC(12,2),
    taux_tva            NUMERIC(5,2),
    montant_ttc         NUMERIC(12,2) GENERATED ALWAYS AS (montant_ht * (1 + taux_tva/100)) STORED,
    date_debut          DATE,
    date_fin            DATE,
    statut              VARCHAR(20),               -- EN_COURS | TERMINE | RESILIE
    devise              VARCHAR(3) DEFAULT 'EUR',
    date_migration      TIMESTAMP DEFAULT NOW()
);

-- ─── PRODUITS ─────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS produits (
    id                  SERIAL PRIMARY KEY,
    source_id           INTEGER NOT NULL,
    reference           VARCHAR(50) UNIQUE,
    designation         VARCHAR(200),
    categorie           VARCHAR(50),
    prix_unitaire       NUMERIC(10,2),
    unite               VARCHAR(20),
    actif               BOOLEAN DEFAULT TRUE,
    date_migration      TIMESTAMP DEFAULT NOW()
);

-- ─── COMMANDES ────────────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS commandes (
    id                  SERIAL PRIMARY KEY,
    source_id           INTEGER NOT NULL,
    numero              VARCHAR(50) UNIQUE,
    client_id           INTEGER REFERENCES clients(id),
    contrat_id          INTEGER REFERENCES contrats(id),
    date_commande       DATE,
    date_livraison      DATE,
    statut              VARCHAR(20),
    montant_ht          NUMERIC(12,2),
    montant_ttc         NUMERIC(12,2),
    devise              VARCHAR(3) DEFAULT 'EUR',
    commentaire         TEXT,
    date_migration      TIMESTAMP DEFAULT NOW()
);

-- ─── LIGNES COMMANDE ──────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS lignes_commande (
    id                  SERIAL PRIMARY KEY,
    commande_id         INTEGER REFERENCES commandes(id),
    produit_id          INTEGER REFERENCES produits(id),
    quantite            NUMERIC(10,3),
    prix_unitaire       NUMERIC(10,2),
    remise_pct          NUMERIC(5,2) DEFAULT 0,
    montant_ht          NUMERIC(12,2)
);

-- ─── MOUVEMENTS FINANCIERS ────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS mouvements_financiers (
    id                  SERIAL PRIMARY KEY,
    source_id           INTEGER NOT NULL,
    commande_id         INTEGER REFERENCES commandes(id),
    type_mouvement      VARCHAR(30),
    reference           VARCHAR(100),
    montant             NUMERIC(12,2),
    devise              VARCHAR(3) DEFAULT 'EUR',
    date_mouvement      DATE,
    statut              VARCHAR(20),
    mode_paiement       VARCHAR(30),
    date_valeur         DATE,
    commentaire         TEXT,
    date_migration      TIMESTAMP DEFAULT NOW()
);

-- ─── PIÈCES JOINTES ───────────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS pieces_jointes (
    id                  SERIAL PRIMARY KEY,
    source_id           INTEGER NOT NULL,
    source_systeme      VARCHAR(20),               -- 'ORACLE' | 'MYSQL'
    entite_type         VARCHAR(30),               -- 'contrat' | 'commande'
    entite_id           INTEGER,                   -- ID de l'entité cible
    nom_fichier         VARCHAR(255),
    type_mime           VARCHAR(100),
    taille_octets       INTEGER,
    checksum_sha_source VARCHAR(64),               -- Checksum original
    checksum_sha_migre  VARCHAR(64),               -- Checksum après copie (validation)
    chemin_source       VARCHAR(500),
    chemin_migre        VARCHAR(500),
    statut_migration    VARCHAR(20) DEFAULT 'EN_ATTENTE',  -- EN_ATTENTE | OK | ERREUR | MANQUANT
    date_migration      TIMESTAMP DEFAULT NOW()
);

-- ─── TABLE DE LOG MIGRATION ───────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS migration_log (
    id                  SERIAL PRIMARY KEY,
    etape               VARCHAR(50),              -- extract | transform | load | validate
    table_source        VARCHAR(100),
    nb_lignes_source    INTEGER,
    nb_lignes_chargees  INTEGER,
    nb_erreurs          INTEGER DEFAULT 0,
    statut              VARCHAR(20),              -- OK | ERREUR | AVERTISSEMENT
    message             TEXT,
    date_execution      TIMESTAMP DEFAULT NOW()
);

-- ─── VUE KPI FINANCIER ────────────────────────────────────────────────────────
CREATE OR REPLACE VIEW v_kpi_financier AS
SELECT
    (SELECT COUNT(*) FROM clients)                                          AS total_clients,
    (SELECT COUNT(*) FROM clients WHERE statut = 'ACTIVE')                 AS clients_actifs,
    (SELECT COUNT(*) FROM contrats)                                         AS total_contrats,
    (SELECT COUNT(*) FROM contrats WHERE statut = 'EN_COURS')              AS contrats_en_cours,
    (SELECT COALESCE(SUM(montant_ht), 0) FROM contrats WHERE statut = 'EN_COURS') AS ca_contrats_actifs,
    (SELECT COUNT(*) FROM commandes)                                        AS total_commandes,
    (SELECT COUNT(*) FROM commandes WHERE statut = 'LIVREE')               AS commandes_livrees,
    (SELECT COALESCE(SUM(montant_ttc), 0) FROM mouvements_financiers WHERE type_mouvement = 'PAIEMENT' AND statut = 'VALIDE') AS ca_encaisse,
    (SELECT COALESCE(SUM(montant), 0) FROM mouvements_financiers WHERE type_mouvement = 'FACTURE' AND statut = 'EN_ATTENTE') AS ca_en_attente,
    (SELECT COUNT(*) FROM pieces_jointes)                                   AS total_pj,
    (SELECT COUNT(*) FROM pieces_jointes WHERE statut_migration = 'OK')    AS pj_migrees_ok;