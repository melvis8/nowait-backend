# Guide de Déploiement

## 1. Base de Données (PostgreSQL)

Pour déployer la base de données en ligne, nous recommandons des services gratuits et performants comme **Neon.tech** ou **Supabase**.

### Option A: Neon.tech (Recommandé)
1. Créez un compte sur [Neon.tech](https://neon.tech).
2. Créez un nouveau projet.
3. Copiez la chaîne de connexion (Connection String). Elle ressemble à : `postgres://user:password@ep-xyz.aws.neon.tech/neondb?sslmode=require`.
4. Assurez-vous d'utiliser `postgresql+asyncpg://...` pour le driver async Python.

### Option B: Render (PostgreSQL)
1. Créez un compte sur [Render](https://render.com).
2. Créez une nouvelle "PostgreSQL Service".
3. Copiez l'URL de connexion interne ou externe selon le besoin.

## 2. Variables d'Environnement

Un fichier `env_vars.txt` a été généré avec toutes les variables nécessaires.
Pour le déploiement :
1. Copiez le contenu de `env_vars.txt`.
2. Ajoutez ces variables dans les paramètres de votre hébergeur (Environment Variables).
3. Modifiez `DATABASE_URL` avec celle de votre base de données en ligne.
4. Mettez `DEBUG=False` pour la production.
5. Changez `SECRET_KEY` pour une chaîne aléatoire sécurisée.

## 3. Déploiement du Backend (Render/Railway)

### Sur Render :
1. Connectez votre dépôt GitHub.
2. Choisissez "Web Service".
3. Runtime: **Python 3**.
4. Build Command: `pip install -r requirements.txt`.
5. Start Command: `uvicorn main:app --host 0.0.0.0 --port 10000` (ou le port assigné par Render).
6. Ajoutez les variables d'environnement.

## 4. Notes sur la Migration

Comme ce projet utilise `SQLAlchemy` sans `Alembic` pour le moment, les nouvelles colonnes (`age`, `priority_score`, etc.) ne seront pas ajoutées automatiquement si la base de données contient déjà les tables.

**Solution :**
*   **Pour une nouvelle base de données** : Tout fonctionnera automatiquement au démarrage grâce à `init_db.py`.
*   **Pour une base existante** : Vous devrez soit supprimer les tables existantes (perte de données) pour qu'elles soient recréées, soit exécuter manuellement des commandes SQL `ALTER TABLE` pour ajouter les colonnes manquantes.
