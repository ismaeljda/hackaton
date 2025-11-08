# Instructions d'installation - Projet Hackaton

## Prérequis

- **Docker Desktop** installé et en cours d'exécution
- **Git** (pour cloner le projet)

## Installation rapide (Recommandée)

### Étape 1 : Cloner le projet
```bash
git clone <url-du-repo>
cd hackaton
```

### Étape 2 : Lancer avec Docker
```bash
docker-compose up --build
```

C'est tout ! L'application sera accessible sur :
- **Frontend** : http://localhost
- **Backend API** : http://localhost:5000

---

## Installation manuelle (Si Docker ne fonctionne pas)

### Prérequis supplémentaires
- **Node.js** (version 18 ou supérieure)
- **Python** (version 3.11)
- **npm** (installé avec Node.js)

### Étape 1 : Cloner le projet
```bash
git clone <url-du-repo>
cd hackaton
```

### Étape 2 : Configurer le Backend
```bash
cd backend
python -m venv venv

# Sur Windows
venv\Scripts\activate

# Sur Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
python app.py
```

Le backend sera accessible sur http://localhost:5000

### Étape 3 : Configurer le Frontend (dans un nouveau terminal)
```bash
cd frontend

# Installer npm si besoin
npm install -g npm@latest

# Option 1 : Utiliser npm (pas besoin de pnpm)
npm install
npm run dev
```

Le frontend sera accessible sur http://localhost:5173

---

## Problèmes courants et solutions

### Problème : "pnpm command not found"
**Solution 1** : Utiliser npm à la place
```bash
cd frontend
rm -rf node_modules pnpm-lock.yaml
npm install
npm run dev
```

**Solution 2** : Installer pnpm
```bash
npm install -g pnpm
```

### Problème : "Docker n'est pas installé"
**Solution** : Télécharger Docker Desktop
- **Windows/Mac** : https://www.docker.com/products/docker-desktop
- **Linux** : Suivre les instructions pour votre distribution

### Problème : "Port 80 déjà utilisé"
**Solution 1** : Arrêter le service qui utilise le port 80
- Fermer Skype, IIS, ou autres services web

**Solution 2** : Modifier le port dans docker-compose.yml
```yaml
frontend:
  ports:
    - "8080:80"  # Utiliser le port 8080 au lieu de 80
```
Puis accéder via http://localhost:8080

### Problème : "Port 5000 déjà utilisé"
**Solution** : Modifier le port du backend dans docker-compose.yml
```yaml
backend:
  ports:
    - "5001:5000"  # Utiliser le port 5001
```

### Problème : Le frontend ne compile pas (erreurs TypeScript)
**Solution** : Les corrections ont déjà été appliquées. Si problème persiste :
```bash
cd frontend
rm -rf node_modules pnpm-lock.yaml package-lock.json
npm install
npm run build
```

---

## Commandes utiles Docker

### Voir les conteneurs en cours
```bash
docker ps
```

### Arrêter tous les conteneurs
```bash
docker-compose down
```

### Reconstruire et redémarrer
```bash
docker-compose down
docker-compose up --build
```

### Voir les logs
```bash
# Tous les logs
docker-compose logs

# Seulement frontend
docker-compose logs frontend

# Seulement backend
docker-compose logs backend
```

### Nettoyer Docker (si problèmes)
```bash
docker-compose down
docker system prune -a
docker-compose up --build
```

---

## Support

Si vous rencontrez d'autres problèmes, vérifiez :
1. Docker Desktop est bien lancé
2. Aucun autre service n'utilise les ports 80 et 5000
3. Vous êtes bien dans le dossier `hackaton` avant de lancer les commandes
