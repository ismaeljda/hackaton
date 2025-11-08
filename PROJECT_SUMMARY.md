# 🌍 Agent de Voyage Intelligent - Résumé Projet

## 📋 Vue d'ensemble

Application de planification de voyage avec agent conversationnel vocal utilisant ElevenLabs AI.
L'agent comprend les demandes vocales/texte, cherche des hôtels/vols, et affiche tout sur une carte interactive.

## 🏗️ Architecture

```
hackaton/
├── frontend/          # React + TypeScript + Vite + Leaflet
│   ├── src/
│   │   ├── components/
│   │   │   ├── ChatAgent.tsx      # Interface chat + micro + audio
│   │   │   └── MapView.tsx        # Carte Leaflet interactive
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── Dockerfile                  # Build avec pnpm + nginx
│   ├── nginx.conf                  # Proxy /api -> backend
│   ├── vite.config.ts              # Port 4173, proxy dev
│   └── package.json                # Deps: react, leaflet, axios
│
├── backend/           # Python Flask + ElevenLabs Agent
│   ├── app.py         # API Flask (TODO)
│   ├── Dockerfile     # Python 3.11
│   └── requirements.txt
│
├── docker-compose.yml # Orchestration complète
└── README.md
```

## 🎯 Fonctionnalités Frontend

### ChatAgent.tsx
- **Input texte** : Zone de saisie + bouton Envoyer
- **Input vocal** : Bouton micro 🎤 avec Web Speech API (reconnaissance fr-FR)
- **Output texte** : Affichage conversation (bulles user/agent)
- **Output audio** : Lecture automatique des réponses vocales (ElevenLabs TTS)
- **Actions** : Dispatch d'événements custom pour contrôler la carte

### MapView.tsx
- **Carte interactive** : React-Leaflet + OpenStreetMap
- **Markers dynamiques** : Affichage hôtels/POI reçus du backend
- **Zoom automatique** : Selon les actions de l'agent
- **Listener d'événements** : Écoute `agent:actions` pour maj en temps réel

## 📡 Contrat API

### Endpoint: `POST /api/converse`

**Request:**
```json
{
  "message": "Prépare un voyage à Lisbonne pour 4 jours"
}
```

**Response:**
```json
{
  "text": "Voici votre itinéraire pour Lisbonne : Jour 1...",
  "audioUrl": "https://backend-url/audio/response_123.mp3",
  "actions": [
    {
      "type": "zoom",
      "lat": 38.7223,
      "lng": -9.1393,
      "zoom": 12
    },
    {
      "type": "hotels",
      "hotels": [
        {
          "lat": 38.7223,
          "lng": -9.1393,
          "name": "Hotel Example"
        }
      ]
    }
  ]
}
```

### Types d'actions supportées:
- `zoom` : Zoom sur coordonnées (lat, lng, zoom)
- `marker` : Ajoute un marker unique (lat, lng, name)
- `hotels` : Ajoute plusieurs markers d'hôtels

## 🔧 Stack Technique

### Frontend
- **Framework** : React 19.2 + TypeScript
- **Build tool** : Vite 7.2.2
- **Package manager** : pnpm (npm est cassé sur ce système)
- **Carte** : react-leaflet 5.0 + leaflet 1.9.4
- **HTTP** : axios 1.13.2
- **Styles** : Inline styles (TailwindCSS-like)

### Backend (À implémenter)
- **Framework** : Flask (Python 3.11)
- **AI Agent** : ElevenLabs Conversational AI
- **TTS** : ElevenLabs Text-to-Speech
- **APIs externes** :
  - Google Places / Booking.com (hôtels)
  - Skyscanner / Kiwi.com (vols)
  - OpenWeatherMap (météo)

### Infrastructure
- **Conteneurisation** : Docker + docker-compose
- **Reverse proxy** : Nginx (prod)
- **Networking** : Bridge Docker (backend ↔ frontend)

## 🚀 Lancement

### Développement local

**Frontend seul :**
```bash
cd frontend
pnpm install
pnpm run dev
# Accessible sur http://localhost:4173
```

**Backend seul :**
```bash
cd backend
pip install -r requirements.txt
python app.py
# API sur http://localhost:5000
```

### Production (Docker)
```bash
docker-compose up --build
```
- Frontend : http://localhost:80
- Backend : http://localhost:5000

## 🔐 Configuration

### Variables d'environnement (Backend)
```bash
ELEVEN_API_KEY=sk-...           # Clé ElevenLabs
GOOGLE_PLACES_KEY=...           # Clé Google Places
FLASK_ENV=production
PORT=5000
```

⚠️ **IMPORTANT** : La clé ElevenLabs doit UNIQUEMENT être dans le backend (pas dans le frontend)

## 📝 TODO Backend

### Priorités
1. **Endpoint `/api/converse`** :
   - Recevoir `message` en POST
   - Appeler ElevenLabs Conversational AI Agent
   - Parser la réponse de l'agent
   - Extraire infos (destination, dates, budget)
   - Chercher hôtels via API
   - Générer audio TTS via ElevenLabs
   - Servir audio (ou renvoyer URL)
   - Construire `actions` pour la carte
   - Retourner JSON avec `{text, audioUrl, actions}`

2. **Services à créer** :
   - `elevenlabs_service.py` : Wrapper API ElevenLabs
   - `hotels_service.py` : Recherche hôtels
   - `flights_service.py` : Recherche vols
   - `geocoding_service.py` : Lat/Lng des villes

3. **Stockage audio** :
   - Option 1 : `/static/audio/` (simple)
   - Option 2 : S3/CloudFlare R2 (prod)
   - Option 3 : Stream direct depuis ElevenLabs

## 🎨 Design System

### Couleurs
- **Primary** : `#0ea5a4` (teal)
- **Secondary** : `#06b6d4` (cyan)
- **Background** : `#f8fafc` (slate-50)
- **User bubble** : `#0ea5a4` (teal) / text white
- **Agent bubble** : `#f1f5f9` (slate-100) / text `#0f172a`

### Layout
- **Grid** : 2 colonnes (420px chat | 1fr carte)
- **Gap** : 16px
- **Padding** : 16px global
- **Border radius** : 12px (cards), 8px (inputs/buttons)
- **Shadows** : `0 6px 20px rgba(0,0,0,0.08)`

## �� Problèmes connus

1. **npm cassé** : Utiliser pnpm obligatoirement
2. **Port 5173 occupé** : Vite utilise 4173 ou 5174 en fallback
3. **Leaflet icons** : Import explicite des PNG requis
4. **CORS** : Backend doit autoriser `http://localhost:4173`

## 📦 Dépendances installées

### Frontend (pnpm)
```json
{
  "dependencies": {
    "react": "^19.2.0",
    "react-dom": "^19.2.0",
    "axios": "^1.13.2",
    "leaflet": "^1.9.4",
    "react-leaflet": "^5.0.0"
  },
  "devDependencies": {
    "@types/leaflet": "^1.9.21",
    "@types/react": "^19.2.2",
    "@types/react-dom": "^19.2.2",
    "@vitejs/plugin-react": "^5.1.0",
    "typescript": "~5.9.3",
    "vite": "^7.2.2"
  }
}
```

### Backend (TODO)
```txt
flask==3.0.0
elevenlabs==1.0.0
requests==2.31.0
python-dotenv==1.0.0
gunicorn==21.2.0
flask-cors==4.0.0
```

## 🎯 Pitch (4 min présentation + 4 min Q&A)

### Points clés pour le jury
1. **Innovation** : Agent vocal intelligent avec cartographie temps réel
2. **UX** : Interface naturelle (voix + texte), feedback visuel immédiat
3. **Architecture** : Microservices Docker, séparation front/back claire
4. **Sécurité** : Clés API côté backend uniquement
5. **Démo** : "Prépare un week-end à Lisbonne" → zoom carte + markers hôtels + audio
6. **Stack moderne** : React 19, Vite, ElevenLabs AI, Leaflet

### Démo live suggérée
1. Montrer l'interface vide
2. Dire au micro : "Je veux partir 4 jours à Barcelone"
3. Montrer la carte qui zoom sur Barcelone
4. L'audio de l'agent se joue
5. Des markers d'hôtels apparaissent
6. Montrer le code backend (appel ElevenLabs)

## 📚 Documentation technique

- **ElevenLabs API** : https://elevenlabs.io/docs
- **React-Leaflet** : https://react-leaflet.js.org
- **Vite** : https://vitejs.dev
- **Docker Compose** : https://docs.docker.com/compose

---

**Date** : 2025-11-08
**Status** : Frontend ✅ | Backend ⏳
**Team** : Hackathon project
