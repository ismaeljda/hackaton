# API de Recherche de Vols

API simple pour rechercher des vols Ryanair selon les préférences de l'utilisateur.

## Installation

```bash
pip install -r requirements.txt
```

## Lancer l'API

```bash
cd backend/vol
python app.py
```

L'API sera disponible sur `http://localhost:5000`

## Endpoints

### 1. Health Check
```
GET /health
```

### 2. Liste des aéroports
```
GET /airports
```

Retourne tous les aéroports de départ (Belgique) et les destinations disponibles.

### 3. Types de voyage
```
GET /themes
```

Retourne les types de voyage disponibles:
- `couple`: Romantique
- `party`: Fête/Nightlife
- `beach`: Plage
- `nature`: Nature
- `mountain`: Montagne
- `city_trip`: City Trip

### 4. Rechercher des vols
```
POST /search
Content-Type: application/json

{
  "origin": "CRL",
  "departure_date": "2025-12-15",
  "return_date": "2025-12-20",
  "themes": ["beach", "party"],
  "coastal": true,
  "max_results": 10
}
```

**Paramètres:**
- `origin` (obligatoire): Code aéroport de départ (ex: "CRL", "BRU", "LGG")
- `departure_date` (obligatoire): Date de départ au format YYYY-MM-DD
- `return_date` (optionnel): Date de retour au format YYYY-MM-DD
- `themes` (optionnel): Liste de types de voyage
- `coastal` (optionnel): `true` pour destinations côtières uniquement
- `max_results` (optionnel): Nombre max de résultats (défaut: 10)

**Réponse:**
```json
{
  "origin": "CRL",
  "departure_date": "2025-12-15",
  "return_date": "2025-12-20",
  "filters": {
    "themes": ["beach", "party"],
    "coastal": true
  },
  "results_count": 5,
  "flights": [
    {
      "type": "round_trip",
      "origin": "CRL",
      "destination": "PMI",
      "destination_name": "Palma Mallorca",
      "destination_country": "Espagne",
      "themes": ["beach", "party", "couple"],
      "coastal": true,
      "departure_date": "2025-12-15T10:30:00",
      "return_date": "2025-12-20T14:15:00",
      "price": 89.99,
      "currency": "EUR"
    }
  ]
}
```

## Exemples d'utilisation pour un agent vocal

### Exemple 1: "Je veux aller à la plage en décembre depuis Charleroi"
```json
{
  "origin": "CRL",
  "departure_date": "2025-12-15",
  "return_date": "2025-12-22",
  "themes": ["beach"]
}
```

### Exemple 2: "Destinations romantiques en couple depuis Bruxelles"
```json
{
  "origin": "BRU",
  "departure_date": "2025-11-20",
  "return_date": "2025-11-23",
  "themes": ["couple"]
}
```

### Exemple 3: "Villes pour faire la fête, destinations côtières"
```json
{
  "origin": "CRL",
  "departure_date": "2025-12-01",
  "return_date": "2025-12-05",
  "themes": ["party"],
  "coastal": true
}
```
