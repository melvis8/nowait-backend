# Guide de Déploiement du Frontend

Ce guide explique comment déployer votre application Frontend (probablement React/Vite ou Next.js) et la connecter à votre Backend déployé.

## 1. Préparation pour la Production

Avant de déployer, vous devez vous assurer que votre frontend pointe vers l'URL **publique** de votre backend (celui que vous venez de déployer sur Render), et non plus vers `localhost`.

### A. Variables d'Environnement
Dans votre projet Frontend, localisez votre fichier de configuration d'API (souvent dans `.env`, `src/config.ts`, ou `src/api/axios.js`).

Vous devrez définir l'URL de l'API via une variable d'environnement.
*   **Pour Vite (React/Vue)** : Créez ou modifiez le fichier `.env.production` à la racine du projet frontend.
    ```env
    VITE_API_URL=https://votre-backend-sur-render.onrender.com
    ```
*   **Pour Next.js** :
    ```env
    NEXT_PUBLIC_API_URL=https://votre-backend-sur-render.onrender.com
    ```
*   **Pour Create React App** :
    ```env
    REACT_APP_API_URL=https://votre-backend-sur-render.onrender.com
    ```

**Important**: Assurez-vous que votre code utilise cette variable pour faire ses requêtes (ex: `axios.defaults.baseURL = import.meta.env.VITE_API_URL`).

## 2. Options de Déploiement

Nous recommandons **Vercel** ou **Netlify** pour le frontend, car ils sont optimisés pour les applications statiques/SPA. **Render** fonctionne aussi très bien.

### Option A : Vercel (Recommandé - Très rapide)
1.  Poussez votre code frontend sur GitHub.
2.  Allez sur [Vercel](https://vercel.com) et connectez-vous avec GitHub.
3.  Cliquez sur **"Add New..."** -> **"Project"**.
4.  Sélectionnez le dépôt de votre Frontend.
5.  **Configure Project** :
    *   **Framework Preset** : Vercel détecte généralement Vite, Next.js ou Create React App automatiquement.
    *   **Build Command** : `npm run build` (ou `yarn build`).
    *   **Output Directory** : `dist` (pour Vite) ou `build` (pour CRA).
6.  **Environment Variables** :
    *   Ajoutez `VITE_API_URL` (ou le nom correspondant à votre projet) avec l'URL de votre backend déployé.
7.  Cliquez sur **Deploy**.

### Option B : Netlify
1.  Allez sur [Netlify](https://www.netlify.com).
2.  Cliquez sur **"Add new site"** -> **"Import an existing project"**.
3.  Connectez GitHub et choisissez votre dépôt Frontend.
4.  Netlify détectera les paramètres de build (Build command: `npm run build`, Publish directory: `dist`).
5.  Cliquez sur **"Site settings"** -> **"Environment variables"** et ajoutez votre variable d'API (ex: `VITE_API_URL`).
6.  Déployez.

### Option C : Render (Static Site)
1.  Sur votre Dashboard Render.
2.  Cliquez sur **"New +"** -> **"Static Site"**.
3.  Connectez le dépôt Frontend.
4.  **Build Command** : `npm run build`.
5.  **Publish Directory** : `dist` (ou `build`).
6.  Allez dans **"Environment"** et ajoutez votre variable `VITE_API_URL`.
7.  Create Static Site.

## 3. Configuration Finale (CORS)

Une fois le frontend déployé, vous aurez une URL publique (ex: `https://mon-app-frontend.vercel.app`).

1.  Retournez sur votre **Backend** (dans le code `main.py`).
2.  Ajoutez cette nouvelle URL Frontend à la liste `origins` dans `main.py` :
    ```python
    origins = [
        "http://localhost:4000",
        "https://frontent-queue-management-app.onrender.com", 
        "https://mon-app-frontend.vercel.app",  # <--- AJOUTER CETTE LIGNE
        # ...
    ]
    ```
3.  Redéployez le Backend pour que la modification soit prise en compte.

Si vous ne faites pas cette étape, vous aurez des erreurs **CORS** dans la console du navigateur et les requêtes échoueront.
