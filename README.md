# 🌍 Agent de Voyage - Hackathon

Application de planification de voyage intelligent avec agent vocal et cartographie interactive.

## 🏗️ Architecture

```
hackaton/
├── backend/          # API Python Flask + ElevenLabs Agent
├── frontend/         # React + TypeScript + Leaflet
└── docker-compose.yml
```

## 🚀 Lancement rapide

### Avec Docker (recommandé)
```bash
docker-compose up --build
```

- **Frontend** : http://localhost:80
- **Backend** : http://localhost:5000

### Développement local

**Backend** :
```bash
cd backend
pip install -r requirements.txt
python app.py  # ou flask run
```

**Frontend** :
```bash
cd frontend
npm install
npm run dev
```

## 🎯 Fonctionnalités

✅ Interface chat avec reconnaissance vocale (Web Speech API)  
✅ Réponses audio générées via ElevenLabs  
✅ Carte interactive (React-Leaflet)  
✅ Zoom automatique sur destinations  
✅ Affichage des hôtels / POI sur carte  
✅ Architecture Docker multi-containers  

## 📡 API Contract

**Endpoint** : `POST /api/converse`

**Request** :
```json
{ "message": "Prépare un voyage à Lisbonne pour 4 jours" }
```

**Response** :
```json
{
  "text": "Voici votre itinéraire...",
  "audioUrl": "https://.../audio.mp3",
  "actions": [
    { "type": "zoom", "lat": 38.7223, "lng": -9.1393, "zoom": 12 },
    { "type": "hotels", "hotels": [{...}] }
  ]
}
```

## 🔐 Sécurité

⚠️ **La clé ElevenLabs doit être stockée côté backend uniquement** (variable d'environnement)

## 📦 Stack

- **Frontend** : React 19, TypeScript, Vite, Leaflet, Axios
- **Backend** : Python 3.11, Flask, ElevenLabs API
- **Infra** : Docker, Nginx
