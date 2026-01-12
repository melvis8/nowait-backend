# Configuration du Frontend pour CORS et API

Le **CORS** (Cross-Origin Resource Sharing) est géré côté **Backend** (ce que nous avons déjà fait). Le Frontend ne peut pas "fixer" les erreurs CORS par lui-même, il doit simplement être configuré pour appeler la bonne URL.

Voici comment configurer votre Frontend pour qu'il se connecte correctement au Backend sans erreur.

## 1. Fichier d'Environnement (.env)

À la racine de votre dossier **Frontend**, créez ou modifiez le fichier `.env` (ou `.env.local`).

### Pour Vite (React / Vue)
```ini
# .env
VITE_API_URL=https://nowait-backend.onrender.com
```

### Pour Create React App
```ini
# .env
REACT_APP_API_URL=https://nowait-backend.onrender.com
```

### Pour Next.js
```ini
# .env.local
NEXT_PUBLIC_API_URL=https://nowait-backend.onrender.com
```

---

## 2. Configuration du Proxy (Développement Local uniquement)

Si vous travaillez en local (`localhost`) mais que vous voulez taper sur le backend en ligne, ou si vous avez des problèmes de cookies/CORS en dev, vous pouvez configurer un proxy.

### Si vous utilisez Vite (`vite.config.ts`)
Modifiez votre fichier `vite.config.ts` pour rediriger les appels API :

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'https://nowait-backend.onrender.com', // L'URL de votre Backend
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
    },
  },
})
```
*Avec cette config, dans votre code frontend, vous ferez des appels à `/api/users` au lieu de `https://.../users`.*

---

## 3. Configuration du Client HTTP (Axios)

Assurez-vous que vous utilisez la variable d'environnement définie à l'étape 1.

Créez un fichier `src/api/axios.js` (ou `.ts`) :

```javascript
import axios from 'axios';

// Utilise la variable d'env, ou fallback sur localhost si elle n'existe pas
const BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const api = axios.create({
    baseURL: BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
    // Important pour l'échange de cookies si nécessaire
    // withCredentials: true 
});

export default api;
```

## Résumé
1. Le Backend autorise désormais les requêtes venant de n'importe quel sous-domaine `onrender.com`.
2. Le Frontend doit juste pointer vers `https://nowait-backend.onrender.com` via ses variables d'environnement.
