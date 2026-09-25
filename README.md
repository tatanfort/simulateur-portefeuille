# Simulateur de portefeuille ETF

Application FastAPI + HTML/JS pour construire un portefeuille d'ETF, recalculer
ses rendements réels nets de frais, backtester la meilleure/pire fenêtre glissante,
mesurer ses métriques de risque et sa résilience face à des crises historiques,
suggérer une optimisation de pondération, simuler sa performance sur N années par
Monte Carlo, projeter un plan d'épargne programmée, et enregistrer des portefeuilles
sur un compte utilisateur.

## Lancer l'application en local

```bash
cd backend
pip3 install -r requirements.txt
python3 -m uvicorn app:app --reload --port 8000
```

Puis ouvrir http://localhost:8000 dans le navigateur.

Sans configuration, l'app utilise une base **SQLite locale** (`backend/data/app.db`,
créée automatiquement) et une clé de session générée aléatoirement au démarrage —
suffisant pour développer, mais les comptes ne survivent pas à un redémarrage du
serveur tant que `SECRET_KEY` n'est pas fixée (voir déploiement ci-dessous).

## Fonctionnement

- `GET /api/etfs` — catalogue des ETF disponibles (voir `backend/etfs.py`), avec frais (TER)
- `GET /api/etf-stats` — rendement/volatilité par ETF, calculés en tâche de fond et mis en cache
- `GET /api/resolve-ticker` — valide un ticker saisi manuellement (essaie les suffixes de bourse courants)
- `POST /api/simulate` — calcule tout le rapport (rendements, risque, résilience, backtest, Monte Carlo)
- `POST /api/optimize` — suggère des pondérations (variance minimale / Sharpe maximal), bornées autour de l'allocation actuelle
- `POST /api/auth/signup`, `POST /api/auth/login`, `GET /api/auth/me` — comptes utilisateurs (email + mot de passe, session par jeton JWT)
- `POST /api/auth/verify-email`, `POST /api/auth/resend-verification` — vérification d'adresse email par lien envoyé par mail
- `POST /api/auth/request-password-reset`, `POST /api/auth/reset-password` — mot de passe oublié, par lien envoyé par mail
- `GET/POST/PUT/DELETE /api/portfolios` — portefeuilles enregistrés, propres à chaque compte

Les prix viennent de Yahoo Finance (endpoint public, aucune clé API requise) et sont
mis en cache serveur 6h. Le portefeuille en cours (hors compte) est aussi sauvegardé
automatiquement dans le navigateur (`localStorage`), pour ne rien perdre entre deux
rechargements même sans être connecté.

### Emails (vérification de compte + mot de passe oublié)

L'envoi des emails passe par [Resend](https://resend.com) (API REST simple, palier
gratuit à 3000 emails/mois). Sans configuration, les emails ne partent pas — un
avertissement s'affiche dans les logs serveur, mais le reste de l'app (inscription,
connexion) continue de fonctionner normalement (juste sans vérification réelle).

Pour l'activer :

1. Créer un compte sur [resend.com](https://resend.com) (gratuit)
2. "Domains" → "Add Domain" → entrer votre nom de domaine (ex: `sortino.fr`) →
   Resend affiche 2-3 enregistrements DNS (TXT/MX pour SPF/DKIM) à ajouter dans la
   zone DNS OVH du domaine (même écran "Zone DNS" que pour le domaine custom Render)
3. Une fois le domaine vérifié (peut prendre quelques minutes à quelques heures),
   "API Keys" → créer une clé
4. Dans les variables d'environnement du serveur (Render : onglet "Environment"),
   ajouter :
   - `RESEND_API_KEY` = la clé copiée à l'étape 3
   - `EMAIL_FROM` = l'adresse d'expédition, ex `Simulateur ETF <no-reply@sortino.fr>`
     (le domaine doit correspondre à celui vérifié dans Resend)
   - `APP_BASE_URL` = l'URL publique de l'app (ex `https://sortino.fr`), utilisée
     pour construire les liens de vérification/réinitialisation dans les emails

## Déploiement — le plus simple : Neon (base de données) + Render (hébergement)

Les deux ont un vrai palier gratuit, sans carte bancaire, et se pilotent entièrement
depuis leur interface web (aucune ligne de commande de déploiement à connaître).

### 1. Mettre le code sur GitHub

Le dossier est déjà un dépôt Git local. Créez un dépôt vide sur
[github.com/new](https://github.com/new) (sans README ni licence), puis :

```bash
git remote add origin https://github.com/<votre-compte>/<nom-du-repo>.git
git branch -M main
git push -u origin main
```

### 2. Créer la base de données (Neon)

1. Aller sur [neon.tech](https://neon.tech) → créer un compte gratuit → "New Project"
2. Une fois le projet créé, copier la **Connection string** affichée
   (commence par `postgresql://...`)

### 3. Déployer le serveur (Render)

1. Aller sur [render.com](https://render.com) → créer un compte gratuit
2. "New +" → "Web Service" → connecter votre dépôt GitHub
3. Configurer :
   - **Root Directory** : `backend`
   - **Runtime** : Python 3
   - **Build Command** : `pip install -r requirements.txt && playwright install --with-deps chromium`
   - **Start Command** : `uvicorn app:app --host 0.0.0.0 --port $PORT`
   - **Instance Type** : Free (voir l'avertissement ci-dessous)
4. Dans l'onglet "Environment", ajouter deux variables :
   - `DATABASE_URL` = la connection string Neon copiée à l'étape 2
   - `SECRET_KEY` = une valeur aléatoire longue (ex: générez-en une avec
     `python3 -c "import secrets; print(secrets.token_hex(32))"` sur votre machine)
5. "Create Web Service" — Render construit et déploie automatiquement. Au premier
   démarrage, l'application crée elle-même les tables nécessaires dans la base Neon.

Render vous donne une URL du type `https://<nom>.onrender.com` — c'est votre site,
utilisable immédiatement, avec comptes et portefeuilles persistants.

**À savoir sur l'export PDF et le palier gratuit** : le bouton "Exporter en PDF"
génère le fichier côté serveur avec un vrai moteur de navigateur (Playwright +
Chromium), pour un rendu fidèle et un vrai téléchargement de fichier plutôt que la
boîte de dialogue d'impression du navigateur. Cela ajoute environ 300 Mo à l'image
construite par Render et consomme de la RAM au moment de générer un PDF (un
processus Chromium headless). Le palier **Free** de Render (512 Mo de RAM) peut
suffire pour un usage personnel occasionnel, mais s'avérer juste ou instable en cas
de pic d'usage ou lors du build initial — si le build échoue par manque de mémoire ou
que l'export PDF échoue en production, passez à l'instance payante la moins chère
(**Starter**, ~7 $/mois) qui lève ces limites.

**À savoir sur le palier gratuit Render** : le service s'endort après ~15 minutes
sans trafic et met quelques secondes à se réveiller au prochain visiteur (normal,
sans impact sur les données). Pour un usage plus soutenu, l'instance payante la
moins chère supprime cette latence.

### Mises à jour

Chaque `git push` sur la branche `main` redéploie automatiquement sur Render — aucune
autre action nécessaire.

### Alternative tout-en-un

Si vous préférez ne gérer qu'un seul service : Render propose aussi une base
PostgreSQL managée directement dans son interface ("New +" → "PostgreSQL", palier
gratuit limité à 30 jours puis payant), ce qui évite de passer par Neon mais coûte
plus vite. Railway.app fonctionne aussi très bien avec le même code (bouton "Deploy
from GitHub repo" + plugin PostgreSQL en un clic), sur un modèle à crédit d'usage
plutôt que gratuit sans limite.
