# Intégration n8n + Gemini

## Architecture

```
User Message → Frontend → Backend /api/converse → n8n Webhook → Gemini AI → n8n → Backend → Frontend
```

## Configuration Backend

### 1. Variable d'environnement

Ajoutez dans votre fichier `.env` ou `docker-compose.yml`:

```env
N8N_WEBHOOK_URL=https://your-n8n-instance.com/webhook/chatbot
SERPAPI_KEY=votre_cle_serpapi
```

### 2. Format attendu par le backend

Le backend accepte deux modes:

#### Mode 1: Le backend envoie le message à n8n

```json
// Frontend → Backend
POST /api/converse
{
  "message": "Je veux un hotel à Paris"
}

// Backend → n8n webhook
POST https://n8n.../webhook/chatbot
{
  "message": "je veux un hotel à paris",
  "timestamp": "2025-11-08T14:30:00"
}
```

#### Mode 2: n8n répond directement au backend

```json
// n8n → Backend (réponse)
{
  "response": "Parfait ! Je vais vous trouver les meilleurs hôtels à Paris",
  "intent": "hotels",
  "destination": "paris",
  "actions": [
    {
      "type": "navigate",
      "url": "/hotels?destination=paris"
    }
  ]
}
```

## Workflow n8n recommandé

### Étape 1: Webhook Trigger
- **URL**: `/webhook/chatbot`
- **Method**: POST
- **Reçoit**: `{ "message": "...", "timestamp": "..." }`

### Étape 2: Gemini AI
- **Prompt système**:
```
Tu es un assistant de voyage intelligent. Analyse le message de l'utilisateur et détermine:
1. L'intention (hotels, flights, activities)
2. La destination
3. Une réponse conversationnelle en français

Format de réponse JSON:
{
  "response": "votre réponse en français",
  "intent": "hotels|flights|activities|none",
  "destination": "nom de ville en minuscules",
  "confidence": 0.9
}
```

- **Message utilisateur**: `{{ $json.message }}`

### Étape 3: Traitement conditionnel (IF)
```javascript
// Si intent détecté ET destination trouvée
{{ $json.intent !== 'none' && $json.destination }}
```

### Étape 4a: Si intent détecté - Créer actions
```javascript
{
  "response": "{{ $json.response }}",
  "intent": "{{ $json.intent }}",
  "destination": "{{ $json.destination }}",
  "actions": [
    {
      "type": "navigate",
      "url": "/{{ $json.intent }}?destination={{ $json.destination }}"
    }
  ]
}
```

### Étape 4b: Si pas d'intent - Réponse simple
```javascript
{
  "response": "{{ $json.response || 'Je peux vous aider à trouver des vols, hôtels ou activités. Quelle destination vous intéresse ?' }}",
  "actions": []
}
```

### Étape 5: Respond to Webhook
Retourne le JSON formaté au backend

## Exemple de prompt Gemini optimisé

```
Tu es un assistant de voyage expert qui aide les utilisateurs à planifier leurs voyages.

TÂCHE:
Analyse le message de l'utilisateur et extrait:
1. L'intention: hotels, flights, activities, ou none
2. La destination (ville en minuscules)
3. Une réponse conversationnelle naturelle en français

RÈGLES:
- Si l'utilisateur demande des hôtels/logement → intent: "hotels"
- Si l'utilisateur demande des vols/avions → intent: "flights"
- Si l'utilisateur demande des activités/visites → intent: "activities"
- Si pas clair → intent: "none"
- Détecte la destination même sans préposition (ex: "Paris" dans "un vol Paris")
- Sois enthousiaste et utile

VILLES CONNUES: paris, londres, barcelone, madrid, rome, lisbonne, bruges, amsterdam, berlin, vienne, prague, budapest

FORMAT DE RÉPONSE (JSON strict):
{
  "response": "ta réponse conversationnelle ici",
  "intent": "hotels|flights|activities|none",
  "destination": "nom ville en minuscules ou null",
  "confidence": 0.0-1.0
}

MESSAGE UTILISATEUR: {{ $json.message }}

RÉPONSE (JSON uniquement):
```

## Test du workflow

### 1. Test sans n8n (fallback local)
```bash
curl -X POST http://localhost:5000/api/converse \
  -H "Content-Type: application/json" \
  -d '{"message": "Je veux un hotel à Paris"}'
```

### 2. Test avec n8n
```bash
# Configurer N8N_WEBHOOK_URL dans .env
N8N_WEBHOOK_URL=https://your-n8n.com/webhook/chatbot

# Même requête, mais sera routée via n8n
curl -X POST http://localhost:5000/api/converse \
  -H "Content-Type: application/json" \
  -d '{"message": "Je veux un hotel à Paris"}'
```

## Avantages de cette approche

✅ **Flexible**: Fonctionne avec ou sans n8n
✅ **Puissant**: Gemini comprend le langage naturel complexe
✅ **Évolutif**: Ajoutez facilement de nouvelles intentions
✅ **Traçable**: n8n logs tous les échanges
✅ **Testable**: Fallback local pour développement

## Prochaines étapes

1. Créez votre workflow n8n avec les étapes ci-dessus
2. Testez avec le test webhook n8n
3. Configurez `N8N_WEBHOOK_URL` dans votre backend
4. Reconstruisez le backend: `docker-compose up --build -d backend`
5. Testez depuis le frontend!

## Améliorations possibles

- **Multi-destinations**: "Vol Paris-Londres-Rome"
- **Dates**: "Hotel à Paris le 15 décembre"
- **Budget**: "Vol pas cher pour Barcelone"
- **Préférences**: "Hotel 4 étoiles avec piscine"
- **Comparaisons**: "Comparer vols Ryanair vs Air France"
