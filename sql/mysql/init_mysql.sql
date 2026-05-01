-- sql/mysql/init_mysql.sql
-- Base MySQL : commandes + produits + mouvements financiers

CREATE DATABASE IF NOT EXISTS mysql_db;
USE mysql_db;

CREATE TABLE IF NOT EXISTS produits (
    id          INT PRIMARY KEY AUTO_INCREMENT,
    reference   VARCHAR(50) UNIQUE NOT NULL,
    designation VARCHAR(200) NOT NULL,
    categorie   VARCHAR(50),
    prix_unitaire DECIMAL(10,2),
    unite       VARCHAR(20) DEFAULT 'unité',
    actif       TINYINT(1)  DEFAULT 1,
    date_creation DATETIME  DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS commandes (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    numero          VARCHAR(50) UNIQUE NOT NULL,
    client_id_ext   INT NOT NULL,        -- FK vers Oracle (client)
    contrat_ref     VARCHAR(50),         -- Référence contrat Oracle
    date_commande   DATE NOT NULL,
    date_livraison  DATE,
    statut          VARCHAR(20) DEFAULT 'EN_ATTENTE',
    -- EN_ATTENTE / VALIDEE / EN_COURS / LIVREE / ANNULEE / LITIGIEUX
    montant_ht      DECIMAL(12,2),
    montant_ttc     DECIMAL(12,2),
    devise          VARCHAR(3) DEFAULT 'EUR',
    commentaire     TEXT,
    cree_par        VARCHAR(100),
    date_creation   DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS lignes_commande (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    commande_id     INT NOT NULL,
    produit_id      INT NOT NULL,
    quantite        DECIMAL(10,3),
    prix_unitaire   DECIMAL(10,2),
    remise_pct      DECIMAL(5,2) DEFAULT 0.00,
    montant_ht      DECIMAL(12,2),
    FOREIGN KEY (commande_id) REFERENCES commandes(id),
    FOREIGN KEY (produit_id)  REFERENCES produits(id)
);

CREATE TABLE IF NOT EXISTS mouvements_financiers (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    commande_id     INT,
    type_mouvement  VARCHAR(30),  -- FACTURE / PAIEMENT / AVOIR / RELANCE
    reference       VARCHAR(100),
    montant         DECIMAL(12,2),
    devise          VARCHAR(3) DEFAULT 'EUR',
    date_mouvement  DATE,
    statut          VARCHAR(20),  -- EN_ATTENTE / VALIDE / REJETE / REMBOURSE
    mode_paiement   VARCHAR(30),  -- VIREMENT / CHEQUE / CB / PRELEVEMENT
    date_valeur     DATE,
    commentaire     TEXT,
    FOREIGN KEY (commande_id) REFERENCES commandes(id)
);

CREATE TABLE IF NOT EXISTS pieces_jointes_mysql (
    id              INT PRIMARY KEY AUTO_INCREMENT,
    commande_id     INT NOT NULL,
    nom_fichier     VARCHAR(255),
    type_mime       VARCHAR(100),
    taille_octets   INT,
    checksum_sha    VARCHAR(64),
    chemin_source   VARCHAR(500),
    date_upload     DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (commande_id) REFERENCES commandes(id)
);

-- ─────────────────────────────────────────
-- DONNÉES FAKE
-- ─────────────────────────────────────────

INSERT INTO produits (reference, designation, categorie, prix_unitaire, unite) VALUES
('PROD-001', 'Licence logiciel ERP annuelle',     'LOGICIEL',  2400.00, 'licence/an'),
('PROD-002', 'Module CRM additionnel',             'LOGICIEL',   800.00, 'module'),
('PROD-003', 'Formation utilisateurs (journée)',   'SERVICE',   1200.00, 'jour'),
('PROD-004', 'Support technique premium',          'SERVICE',    350.00, 'mois'),
('PROD-005', 'Audit infrastructure SI',            'CONSULTING', 1800.00, 'jour'),
('PROD-006', 'Serveur application (hébergement)',  'INFRA',      450.00, 'mois'),
('PROD-007', 'Sauvegarde données (100 Go)',        'INFRA',       80.00, 'mois'),
('PROD-008', 'Développement spécifique',           'CONSULTING', 1500.00, 'jour');

INSERT INTO commandes (numero, client_id_ext, contrat_ref, date_commande, date_livraison, statut, montant_ht, montant_ttc, cree_par) VALUES
('CMD-2022-001', 1, 'CTR-ORA-2021-001', '2022-01-10', '2022-01-31', 'LIVREE',    3600.00,  4320.00, 'commercial_a'),
('CMD-2022-002', 3, 'CTR-ORA-2022-001', '2022-06-15', '2022-07-15', 'LIVREE',   14400.00, 17280.00, 'commercial_b'),
('CMD-2022-003', 5, 'CTR-ORA-2022-002', '2022-11-05', '2022-12-01', 'LIVREE',    6250.00,  7500.00, 'commercial_a'),
('CMD-2023-001', 6, 'CTR-ORA-2023-001', '2023-01-20', '2023-02-10', 'LIVREE',   22400.00, 22400.00, 'commercial_c'),
('CMD-2023-002', 8, 'CTR-ORA-2023-002', '2023-08-01', '2023-09-01', 'EN_COURS',  8800.00, 10560.00, 'commercial_b'),
('CMD-2023-003', 2, 'CTR-ORA-2021-002', '2023-03-15', '2023-04-15', 'ANNULEE',   1600.00,  1920.00, 'commercial_a'),
('CMD-2023-004', 9, 'CTR-ORA-2021-003', '2023-10-01', '2023-11-01', 'LIVREE',    4200.00,  5040.00, 'commercial_c'),
('CMD-2024-001', 1, 'CTR-ORA-2021-001', '2024-01-05', '2024-01-31', 'VALIDEE',   2400.00,  2880.00, 'commercial_a'),
('CMD-2024-002', 10,'CTR-ORA-2022-003', '2024-02-10', NULL,          'LITIGIEUX', 7600.00,  7600.00, 'commercial_b'),
('CMD-2024-003', 5, 'CTR-ORA-2022-002', '2024-03-01', '2024-04-01', 'EN_COURS',  3750.00,  4500.00, 'commercial_c');

INSERT INTO lignes_commande (commande_id, produit_id, quantite, prix_unitaire, remise_pct, montant_ht) VALUES
(1, 1, 1.000, 2400.00, 0.00, 2400.00),
(1, 4, 3.000,  350.00, 0.00, 1050.00),
(2, 1, 3.000, 2400.00, 0.00, 7200.00),
(2, 3, 6.000, 1200.00, 0.00, 7200.00),
(3, 1, 2.000, 2400.00, 0.00, 4800.00),
(3, 2, 1.000,  800.00, 0.00,  800.00),
(3, 4, 2.000,  350.00, 5.00,  665.00),
(4, 5, 8.000, 1800.00, 0.00, 14400.00),
(4, 6, 4.000,  450.00, 0.00,  1800.00),
(4, 7, 4.000,   80.00, 0.00,   320.00);

INSERT INTO mouvements_financiers (commande_id, type_mouvement, reference, montant, date_mouvement, statut, mode_paiement, date_valeur) VALUES
(1, 'FACTURE',  'FAC-2022-001',  4320.00, '2022-01-31', 'VALIDE',    NULL,         '2022-01-31'),
(1, 'PAIEMENT', 'PAY-2022-001',  4320.00, '2022-02-15', 'VALIDE',    'VIREMENT',   '2022-02-15'),
(2, 'FACTURE',  'FAC-2022-002', 17280.00, '2022-07-15', 'VALIDE',    NULL,         '2022-07-15'),
(2, 'PAIEMENT', 'PAY-2022-002', 17280.00, '2022-08-10', 'VALIDE',    'VIREMENT',   '2022-08-10'),
(3, 'FACTURE',  'FAC-2022-003',  7500.00, '2022-12-01', 'VALIDE',    NULL,         '2022-12-01'),
(3, 'PAIEMENT', 'PAY-2022-003',  7500.00, '2023-01-05', 'VALIDE',    'PRELEVEMENT','2023-01-05'),
(4, 'FACTURE',  'FAC-2023-001', 22400.00, '2023-02-10', 'VALIDE',    NULL,         '2023-02-10'),
(4, 'PAIEMENT', 'PAY-2023-001', 22400.00, '2023-03-01', 'VALIDE',    'VIREMENT',   '2023-03-01'),
(5, 'FACTURE',  'FAC-2023-002', 10560.00, '2023-09-01', 'EN_ATTENTE',NULL,         '2023-09-01'),
(7, 'FACTURE',  'FAC-2023-003',  5040.00, '2023-11-01', 'VALIDE',    NULL,         '2023-11-01'),
(7, 'PAIEMENT', 'PAY-2023-003',  5040.00, '2023-11-20', 'VALIDE',    'CHEQUE',     '2023-11-25'),
(9, 'FACTURE',  'FAC-2024-001',  7600.00, '2024-02-28', 'REJETE',    NULL,         '2024-02-28');

INSERT INTO pieces_jointes_mysql (commande_id, nom_fichier, type_mime, taille_octets, checksum_sha, chemin_source) VALUES
(1, 'bon_commande_CMD-2022-001.pdf',  'application/pdf', 134567, 'f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2', '/nas/commandes/2022/CMD-2022-001/'),
(2, 'bon_commande_CMD-2022-002.pdf',  'application/pdf', 189234, 'a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3', '/nas/commandes/2022/CMD-2022-002/'),
(2, 'PV_livraison_CMD-2022-002.pdf',  'application/pdf',  87654, 'b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4', '/nas/commandes/2022/CMD-2022-002/'),
(4, 'rapport_audit_CMD-2023-001.pdf', 'application/pdf', 456789, 'c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5', '/nas/commandes/2023/CMD-2023-001/'),
(5, 'bon_commande_CMD-2023-002.pdf',  'application/pdf', 201345, 'd5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6', '/nas/commandes/2023/CMD-2023-002/');