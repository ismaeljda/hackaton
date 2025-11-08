# trip-agent-frontend (démo)

Front React + TypeScript pour la démo "agent de voyage" (hackathon).

## Lancer
1. Installer deps : `npm install` (déjà fait)
2. Démarrer : `npm run dev`

## Contrat backend attendu
Le frontend envoie `POST /api/converse` avec JSON `{ message: string }`.
Le backend doit répondre JSON `{ text: string, audioUrl?: string, actions?: any[] }`.
- `audioUrl` : URL publique pointant sur un audio (mp3) généré par ElevenLabs ou proxy.
- `actions` : liste d'actions pour le frontend, ex :
  - `{ type:'zoom', lat: 38.7223, lng: -9.1393, zoom: 12 }`
  - `{ type:'hotels', hotels: [{lat, lng, name}, ...] }`

**Important** : Ne mettez pas la clé ElevenLabs dans le frontend ; gérez les appels à ElevenLabs dans le backend Python.

## Configuration du proxy (développement)

Le proxy Vite est déjà configuré pour rediriger `/api/*` vers `http://localhost:8000`.
Assurez-vous que votre backend Python tourne sur le port 8000.
