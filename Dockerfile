# Dockerfile
FROM python:3.11-slim

# Dépendances système (pour psycopg2 et mysql connector)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copier et installer les dépendances en premier (cache Docker)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier le code
COPY . .

# Créer les dossiers de runtime
RUN mkdir -p logs attachments/source attachments/migrated

# Point d'entrée
CMD ["python", "main.py"]