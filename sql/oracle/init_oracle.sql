-- sql/oracle/init_oracle.sql
-- Simule une base Oracle (clients + contrats + pièces jointes)

CREATE DATABASE IF NOT EXISTS oracle_db;
USE oracle_db;

-- Table CLIENTS (nomenclature Oracle style)
CREATE TABLE IF NOT EXISTS CLIENTS_ORA (
    CLIENT_ID     INT PRIMARY KEY AUTO_INCREMENT,
    NOM           VARCHAR(100) NOT NULL,
    PRENOM        VARCHAR(100),
    EMAIL         VARCHAR(200) UNIQUE,
    TELEPHONE     VARCHAR(20),
    DATE_NAISSANCE DATE,
    STATUT        VARCHAR(20) DEFAULT 'ACTIF',  -- ACTIF / INACTIF / ARCHIVE
    CODE_PAYS     VARCHAR(3)  DEFAULT 'FRA',
    DATE_CREATION DATETIME    DEFAULT CURRENT_TIMESTAMP,
    DATE_MAJ      DATETIME    DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Table CONTRATS
CREATE TABLE IF NOT EXISTS CONTRATS_ORA (
    CONTRAT_ID    INT PRIMARY KEY AUTO_INCREMENT,
    CLIENT_ID     INT NOT NULL,
    NUMERO        VARCHAR(50) UNIQUE NOT NULL,
    TYPE_CONTRAT  VARCHAR(30),     -- STANDARD / PREMIUM / VIP
    MONTANT_HT    DECIMAL(12,2),
    TAUX_TVA      DECIMAL(5,2)    DEFAULT 20.00,
    DATE_DEBUT    DATE,
    DATE_FIN      DATE,
    STATUT        VARCHAR(20)     DEFAULT 'EN_COURS',
    DEVISE        VARCHAR(3)      DEFAULT 'EUR',
    FOREIGN KEY (CLIENT_ID) REFERENCES CLIENTS_ORA(CLIENT_ID)
);

-- Table PIECES_JOINTES_ORA
CREATE TABLE IF NOT EXISTS PIECES_JOINTES_ORA (
    PJ_ID         INT PRIMARY KEY AUTO_INCREMENT,
    CONTRAT_ID    INT NOT NULL,
    NOM_FICHIER   VARCHAR(255),
    TYPE_MIME     VARCHAR(100),
    TAILLE_OCTETS INT,
    CHECKSUM_SHA  VARCHAR(64),
    CHEMIN_STOCKAGE VARCHAR(500),
    DATE_UPLOAD   DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (CONTRAT_ID) REFERENCES CONTRATS_ORA(CONTRAT_ID)
);

-- ─────────────────────────────────────────
-- DONNÉES FAKE
-- ─────────────────────────────────────────

INSERT INTO CLIENTS_ORA (NOM, PRENOM, EMAIL, TELEPHONE, DATE_NAISSANCE, STATUT, CODE_PAYS) VALUES
('Martin',    'Sophie',   'sophie.martin@email.fr',    '0612345678', '1985-03-15', 'ACTIF',    'FRA'),
('Dupont',    'Jean',     'jean.dupont@email.fr',      '0623456789', '1972-07-22', 'ACTIF',    'FRA'),
('Leroy',     'Marie',    'marie.leroy@email.fr',      '0634567890', '1990-11-08', 'ACTIF',    'BEL'),
('Bernard',   'Pierre',   'pierre.bernard@email.fr',   '0645678901', '1968-05-30', 'INACTIF',  'FRA'),
('Moreau',    'Claire',   'claire.moreau@email.fr',    '0656789012', '1995-01-14', 'ACTIF',    'FRA'),
('Simon',     'Thomas',   'thomas.simon@email.fr',     '0667890123', '1988-09-25', 'ACTIF',    'CHE'),
('Laurent',   'Emma',     'emma.laurent@email.fr',     '0678901234', '1992-04-03', 'ARCHIVE',  'FRA'),
('Petit',     'Lucas',    'lucas.petit@email.fr',      '0689012345', '1980-12-17', 'ACTIF',    'FRA'),
('Robert',    'Camille',  'camille.robert@email.fr',   '0690123456', '1975-08-09', 'ACTIF',    'FRA'),
('Richard',   'Antoine',  'antoine.richard@email.fr',  '0601234567', '1983-06-21', 'INACTIF',  'LUX');

INSERT INTO CONTRATS_ORA (CLIENT_ID, NUMERO, TYPE_CONTRAT, MONTANT_HT, TAUX_TVA, DATE_DEBUT, DATE_FIN, STATUT) VALUES
(1,  'CTR-ORA-2021-001', 'PREMIUM',  12500.00, 20.00, '2021-01-15', '2024-01-14', 'EN_COURS'),
(2,  'CTR-ORA-2021-002', 'STANDARD',  3200.00, 20.00, '2021-03-01', '2023-02-28', 'TERMINE'),
(3,  'CTR-ORA-2022-001', 'VIP',      45000.00, 20.00, '2022-06-01', '2025-05-31', 'EN_COURS'),
(4,  'CTR-ORA-2020-001', 'STANDARD',  1800.00, 20.00, '2020-09-15', '2022-09-14', 'TERMINE'),
(5,  'CTR-ORA-2022-002', 'PREMIUM',  18750.00, 20.00, '2022-11-01', '2025-10-31', 'EN_COURS'),
(6,  'CTR-ORA-2023-001', 'VIP',      67000.00, 0.00,  '2023-01-01', '2025-12-31', 'EN_COURS'),
(7,  'CTR-ORA-2019-001', 'STANDARD',  2400.00, 20.00, '2019-04-01', '2021-03-31', 'RESILIE'),
(8,  'CTR-ORA-2023-002', 'PREMIUM',  22000.00, 20.00, '2023-07-15', '2026-07-14', 'EN_COURS'),
(9,  'CTR-ORA-2021-003', 'STANDARD',  5500.00, 20.00, '2021-10-01', '2024-09-30', 'EN_COURS'),
(10, 'CTR-ORA-2022-003', 'VIP',      38000.00, 0.00,  '2022-03-01', '2025-02-28', 'EN_COURS');

INSERT INTO PIECES_JOINTES_ORA (CONTRAT_ID, NOM_FICHIER, TYPE_MIME, TAILLE_OCTETS, CHECKSUM_SHA, CHEMIN_STOCKAGE) VALUES
(1, 'contrat_CTR-ORA-2021-001.pdf', 'application/pdf', 245678, 'a3f4b2c1d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2', '/nas/contrats/2021/CTR-ORA-2021-001.pdf'),
(1, 'avenant_01_CTR-ORA-2021-001.pdf', 'application/pdf', 98432, 'b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5', '/nas/contrats/2021/avenant_01.pdf'),
(3, 'contrat_CTR-ORA-2022-001.pdf', 'application/pdf', 312450, 'c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6', '/nas/contrats/2022/CTR-ORA-2022-001.pdf'),
(5, 'contrat_CTR-ORA-2022-002.pdf', 'application/pdf', 189234, 'd6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7', '/nas/contrats/2022/CTR-ORA-2022-002.pdf'),
(8, 'contrat_CTR-ORA-2023-002.pdf', 'application/pdf', 276543, 'e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8', '/nas/contrats/2023/CTR-ORA-2023-002.pdf');