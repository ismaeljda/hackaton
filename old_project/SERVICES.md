# Documentation des Services

Cette application Flask est organisée en plusieurs services modulaires qui gèrent différentes fonctionnalités. Chaque service est isolé dans son propre fichier pour faciliter la maintenance et les tests.

---

## 📋 Vue d'ensemble

L'application utilise 6 services principaux :

1. **FlightSearchService** - Recherche de vols Ryanair
2. **WeatherService** - Données météorologiques
3. **RyanairLinkService** - Génération de liens de réservation
4. **GoogleHotelsService** - Recherche d'hôtels via SERP API
5. **GooglePlacesService** - Activités et restaurants via Google Places API
6. **AccommodationService** - Recherche d'hébergements (service de base)

---

## 🛫 FlightSearchService

**Fichier**: `services/flight_service.py`

### Description
Service principal qui recherche des vols aller-retour Ryanair en fonction de différents critères (thèmes, pays, dates).

### Fonctionnalités principales

#### `search_flights(search_params)`
Recherche des vols en fonction des paramètres fournis.

**Paramètres** :
```python
search_params = {
    'departure_airports': ['CRL', 'BRU'],        # Aéroports de départ
    'departure_date_from': '2025-12-01',         # Date de départ min
    'departure_date_to': '2025-12-15',           # Date de départ max
    'min_stay_duration': 4,                      # Durée minimale du séjour en jours
    'return_date_max': '2025-12-20',             # Date de retour max (optionnel)
    'theme': 'beach',                            # Thème recherché (optionnel)
    'target_countries': ['spain', 'italy'],      # Pays cibles (si pas de thème)
    'coastal_only': True                         # Uniquement destinations côtières (optionnel)
}
```

**Retour** :
```python
[
    {
        'origin': 'CRL',
        'destination': 'BCN',
        'outbound_price': 25.5,
        'inbound_price': 30.0,
        'total_price': 55.5,
        'departure_time': '2025-12-05T08:30:00',
        'return_time': '2025-12-09T18:15:00',
        'origin_name': 'Brussels South Charleroi Airport',
        'destination_info': {
            'name': 'Barcelona-El Prat Airport',
            'coastal': True,
            'sea': 'Mediterranean',
            'themes': ['city_trip', 'party', 'beach', 'couple']
        },
        'ryanair_link': 'https://www.ryanair.com/...'
    },
    # ... autres résultats
]
```

### Logique de fonctionnement

1. **Récupération des destinations** :
   - Si `theme` est fourni → cherche tous les aéroports avec ce thème via `get_airports_by_theme()`
   - Sinon → cherche les aéroports des pays spécifiés via `get_airports_by_countries()`
   - Supporte le filtrage côtier avec `coastal_only`

2. **Recherche de vols** :
   - Pour chaque aéroport de départ, recherche les vols vers toutes les destinations
   - Utilise l'API Ryanair via `self.ryanair.get_cheapest_return_flights()`
   - Gère les erreurs silencieusement (continue même si une route échoue)

3. **Enrichissement des résultats** :
   - Arrondit les prix au 0.5€ le plus proche pour plus de clarté
   - Génère automatiquement le lien de réservation Ryanair
   - Ajoute les informations de l'aéroport (nom, mer, thèmes)

4. **Tri** :
   - Les résultats sont triés par prix total croissant

### Exemple d'utilisation
```python
from services.flight_service import FlightSearchService

flight_service = FlightSearchService()

results = flight_service.search_flights({
    'departure_airports': ['CRL'],
    'departure_date_from': '2025-12-01',
    'departure_date_to': '2025-12-15',
    'min_stay_duration': 5,
    'theme': 'beach'
})

print(f"Trouvé {len(results)} vols")
print(f"Moins cher : {results[0]['total_price']}€ vers {results[0]['destination']}")
```

---

## ☀️ WeatherService

**Fichier**: `services/weather_service.py`

### Description
Service pour obtenir les données météorologiques actuelles d'une destination via l'API OpenWeather.

### Fonctionnalités

#### `get_weather(airport_code)`
Récupère les données météo pour un aéroport donné.

**Paramètres** :
- `airport_code` (str) : Code IATA de l'aéroport (ex: 'BCN', 'PMI')

**Retour** :
```python
{
    'temperature': 22.5,           # Température en °C
    'description': 'Clear sky',    # Description textuelle
    'icon': '01d',                 # Code icône OpenWeather
    'humidity': 65,                # Humidité en %
    'wind_speed': 3.2             # Vitesse du vent en m/s
}
# ou None si erreur
```

### Configuration requise
- **Variable d'environnement** : `OPENWEATHER_API_KEY`
- Obtenir une clé sur : https://openweathermap.org/api

### Exemple d'utilisation
```python
from services.weather_service import WeatherService

weather_service = WeatherService(api_key="votre_clé_api")
weather = weather_service.get_weather('BCN')

if weather:
    print(f"Température à Barcelone : {weather['temperature']}°C")
    print(f"Conditions : {weather['description']}")
```

---

## 🔗 RyanairLinkService

**Fichier**: `services/ryanair_service.py`

### Description
Service statique qui génère des liens de réservation directs vers le site Ryanair.

### Fonctionnalités

#### `create_booking_link(origin, destination, departure_date, return_date)`
Crée un lien direct vers Ryanair avec les dates pré-remplies.

**Paramètres** :
- `origin` (str) : Code IATA de départ (ex: 'CRL')
- `destination` (str) : Code IATA de destination (ex: 'BCN')
- `departure_date` (str/datetime) : Date de départ (ISO format)
- `return_date` (str/datetime) : Date de retour (ISO format)

**Retour** : URL formatée vers Ryanair

**Exemple** :
```python
from services.ryanair_service import RyanairLinkService

link = RyanairLinkService.create_booking_link(
    'CRL', 'BCN', '2025-12-05', '2025-12-09'
)
# Retourne : https://www.ryanair.com/fr/fr/booking/home/CRL/BCN/2025-12-05/2025-12-09/1/0/0
```

---

## 🏨 GoogleHotelsService

**Fichier**: `services/hotel_service.py`

### Description
Service complet pour rechercher des hôtels via l'API SERP (Google Hotels). Inclut un mapping de 180+ codes IATA vers les noms de villes.

### Fonctionnalités principales

#### `search_hotels(destination, checkin_date, checkout_date, adults=2, **filters)`
Recherche d'hôtels avec filtres avancés.

**Paramètres** :
```python
destination = 'BCN'              # Code IATA
checkin_date = '2025-12-05'      # Format YYYY-MM-DD
checkout_date = '2025-12-09'
adults = 2

# Filtres optionnels
filters = {
    'price_min': 50,             # Prix minimum par nuit (€)
    'price_max': 150,            # Prix maximum par nuit (€)
    'hotel_class': '3',          # Nombre d'étoiles (1-5)
    'hotel_type': 'hotel',       # Type : hotel, hostel, resort, apartment, boutique
    'free_cancellation': True,   # Annulation gratuite
    'sort': '8'                  # '8' = prix croissant, '1' = note décroissante
}
```

**Retour** :
```python
{
    'hotels': [
        {
            'name': 'Hotel Barcelona Center',
            'rating': 8.5,                    # Note sur 10
            'price': '85€',                   # Prix affiché
            'price_numeric': 85,              # Prix numérique pour tri/filtrage
            'image': 'https://...',           # URL photo
            'description': 'Hotel description',
            'amenities': ['WiFi', 'AC', ...], # Top 5 équipements
            'booking_url': 'https://...',     # Lien de réservation
            'stars': 3,                       # Nombre d'étoiles (1-5)
            'stars_display': '3-star hotel',
            'location_rating': 8.9,           # Note de l'emplacement
            'reviews': 1250,                  # Nombre d'avis
            'free_cancellation': True,
            'type': 'Hotel',                  # Catégorie détectée
            'details_url': 'https://...'      # Lien pour plus d'infos
        },
        # ... jusqu'à 50 hôtels
    ],
    'total_results': 45,
    'city': 'Barcelona',
    'search_params': {...}
}
```

### Stratégies de recherche

Le service utilise **3 stratégies** pour maximiser le nombre de résultats :

1. **Recherche principale** : Requête standard avec filtres
2. **Recherche avec variantes** : Si moins de 35 résultats
   - Recherche avec différentes localisations (US, UK, DE)
   - Différentes requêtes ("hotels near Barcelona", "Barcelona accommodation")
   - Combine les résultats uniques
3. **Pagination** : Si l'API indique plus de pages disponibles
   - Charge jusqu'à 3 pages supplémentaires
   - Limite pour éviter les appels excessifs

### Mapping IATA → Ville

Le service inclut un dictionnaire `IATA_TO_CITY` avec **180+ aéroports** :
```python
IATA_TO_CITY = {
    'BCN': 'Barcelona',
    'MAD': 'Madrid',
    'CDG': 'Paris',
    'FCO': 'Rome',
    # ... 180+ entrées
}
```

### Catégorisation automatique

Le service catégorise automatiquement les hôtels :
- **Hostel** : contient "hostel", "auberge", "backpack"
- **Resort** : contient "resort", "spa"
- **Apartment** : contient "apartment", "appart", "residence"
- **Boutique Hotel** : contient "boutique", "design"
- **Hotel** : par défaut

### Configuration requise
- **Variable d'environnement** : `SERPAPI_KEY`
- Obtenir une clé sur : https://serpapi.com/

### Exemple d'utilisation
```python
from services.hotel_service import GoogleHotelsService
from config import Config

hotel_service = GoogleHotelsService(Config.__dict__)

results = hotel_service.search_hotels(
    destination='BCN',
    checkin_date='2025-12-05',
    checkout_date='2025-12-09',
    adults=2,
    price_max=100,
    hotel_class='3',
    sort='8'  # Tri par prix
)

print(f"Trouvé {results['total_results']} hôtels à {results['city']}")
for hotel in results['hotels'][:5]:
    print(f"{hotel['name']} - {hotel['price']} - ⭐ {hotel['rating']}")
```

---

## 🍽️ GooglePlacesService

**Fichier**: `services/google_places_service.py`

### Description
Service complet utilisant l'API Google Places pour trouver restaurants, attractions touristiques, activités et points d'intérêt.

### Fonctionnalités principales

#### `get_restaurants_for_destination(airport_code, cuisine_type=None, price_level=None, min_rating=None)`
Recherche de restaurants avec filtres détaillés.

**Paramètres** :
```python
airport_code = 'BCN'
cuisine_type = 'italian'    # italian, french, spanish, asian, mediterranean, etc.
price_level = 2             # 1-4 (€ à €€€€)
min_rating = 4.0            # Note minimale (défaut: 3.5)
```

**Retour** :
```python
[
    {
        'name': 'La Pizzeria',
        'rating': 4.5,
        'price_level': 2,                    # 1-4
        'user_ratings_total': 856,
        'address': 'Carrer de la Marina, 25',
        'cuisine_type': 'Italienne',
        'place_id': 'ChIJ...',
        'photo': 'https://maps.googleapis.com/...',
        'website': 'https://...',
        'phone': '+34 123 456 789',
        'opening_hours': [
            'Monday: 12:00 PM – 11:00 PM',
            'Tuesday: 12:00 PM – 11:00 PM',
            # ...
        ],
        'has_photo': True
    },
    # ... jusqu'à 20 restaurants
]
```

#### `get_activities_for_destination(airport_code, theme=None, full_fetch=False)`
Récupère un ensemble complet d'activités et points d'intérêt.

**Paramètres** :
- `airport_code` (str) : Code IATA de destination
- `theme` (str, optionnel) : Thème spécifique (non implémenté actuellement)
- `full_fetch` (bool) : Fetch complet vs résumé

**Retour** :
```python
{
    'gastronomie': [
        {
            'name': 'Restaurant Els Quatre Gats',
            'category': 'gastronomie',
            'subcategory': 'restaurants_locaux',
            'rating': 4.5,
            'price_range': '€€',
            'description': 'Restaurant recommandé avec 856 avis',
            'address': 'Carrer Montsió, 3',
            'place_id': 'ChIJ...',
            'photo': 'https://...'
        },
        # ... jusqu'à 8 restaurants
    ],
    'culture': [
        {
            'name': 'Sagrada Família',
            'category': 'culture',
            'subcategory': 'monuments',
            'rating': 4.8,
            'price_range': '€€',
            'description': 'Attraction touristique populaire avec 125000 avis',
            # ...
        },
        # ... monuments (6) + musées (4)
    ],
    'nature': [
        {
            'name': 'Park Güell',
            'category': 'nature',
            'subcategory': 'parcs',
            'rating': 4.6,
            'price_range': 'Gratuit',
            # ...
        },
        # ... jusqu'à 6 parcs
    ],
    'loisirs': [
        # Shopping (4) + vie nocturne (4)
    ],
    'detente': [
        # Spas et bien-être (4)
    ]
}
```

### Mapping des coordonnées

Le service inclut un mapping de **40+ aéroports** vers les coordonnées des centres-villes :
```python
airport_coordinates = {
    'BCN': (41.3851, 2.1734),    # Barcelona
    'MAD': (40.4168, -3.7038),   # Madrid
    'FCO': (41.9028, 12.4964),   # Rome
    # ... 40+ entrées
}
```

### Types de recherche

Le service effectue **7 types de recherches** via Google Places API :

1. **Restaurants** : Type `restaurant`, rayon 15km, top 8
2. **Attractions touristiques** : Type `tourist_attraction`, top 6
3. **Musées** : Type `museum`, top 4
4. **Parcs** : Type `park`, top 6
5. **Shopping** : Type `shopping_mall`, top 4
6. **Spas** : Type `spa`, top 4
7. **Bars** : Type `bar`, rayon 15km, top 4

### Filtres de qualité

- **Note minimale** : 3.5/5 pour tous les résultats
- **Tri** : Par note décroissante
- **Photos** : URL générée automatiquement (max 400px)

### Mapping des cuisines

Supporte 15+ types de cuisine :
```python
cuisine_mapping = {
    'italian_restaurant': 'Italienne',
    'french_restaurant': 'Française',
    'japanese_restaurant': 'Japonaise',
    'indian_restaurant': 'Indienne',
    # ... etc
}
```

### Fallback intelligent

Si l'API échoue ou retourne peu de résultats, génère des suggestions de base :
```python
{
    'culture': ['Centre historique de {ville}'],
    'gastronomie': ['Restaurants locaux de {ville}'],
    'nature': ['Espaces verts de {ville}']
}
```

### Configuration requise
- **Variable d'environnement** : `GOOGLE_MAPS_API_KEY`
- Obtenir une clé sur : https://console.cloud.google.com/
- Activer : Places API, Maps JavaScript API

### Exemple d'utilisation

```python
from services.google_places_service import GooglePlacesService

places_service = GooglePlacesService(api_key="votre_clé_api")

# Recherche de restaurants italiens haut de gamme
restaurants = places_service.get_restaurants_for_destination(
    airport_code='BCN',
    cuisine_type='italian',
    price_level=3,
    min_rating=4.2
)

print(f"Trouvé {len(restaurants)} restaurants italiens")

# Recherche d'activités complètes
activities = places_service.get_activities_for_destination('BCN')

print(f"Catégories disponibles : {list(activities.keys())}")
print(f"Restaurants : {len(activities['gastronomie'])}")
print(f"Attractions : {len(activities['culture'])}")
```

---

## 🏠 AccommodationService

**Fichier**: `services/__init__.py` (service de base)

### Description
Service simple pour la recherche d'hébergements. Actuellement un placeholder pour future implémentation.

### Fonctionnalités

#### `search_accommodations(destination, checkin_date, checkout_date)`
Recherche basique d'hébergements.

**Note** : Ce service est actuellement minimal. Pour les hôtels, utilisez plutôt `GoogleHotelsService` qui offre des fonctionnalités complètes.

---

## 🗺️ airport_themes.py - Base de données des aéroports

**Fichier**: `airport_themes.py`

Bien qu'il ne s'agisse pas d'un service au sens strict, ce fichier est **essentiel** au fonctionnement de tous les services.

### Contenu

- **250+ aéroports** organisés par pays
- **6 thèmes** de voyage : couple, party, beach, nature, mountain, city_trip
- Métadonnées : coastal (côtier ou non), sea (mer adjacente), themes (tags)

### Structure des données

```python
airports_by_country = {
    'spain': {
        'name': 'Espagne',
        'airports': {
            'BCN': {
                'name': 'Barcelona-El Prat Airport',
                'coastal': True,
                'sea': 'Mediterranean',
                'themes': ['city_trip', 'party', 'beach', 'couple']
            },
            # ... autres aéroports
        }
    },
    # ... autres pays
}

THEMES = {
    'couple': {
        'name': '💕 Couple',
        'description': 'Romantique mais abordable',
        'color': '#ff6b9d',
        'icon': 'bi-heart-fill'
    },
    # ... autres thèmes
}
```

### Fonctions utilitaires

```python
# Récupérer tous les aéroports d'un thème
get_airports_by_theme('beach')  # → ['BCN', 'PMI', 'AGP', ...]

# Récupérer tous les aéroports de plusieurs thèmes
get_airports_by_themes(['beach', 'party'])  # → ['BCN', 'IBZ', ...]

# Récupérer les aéroports de pays spécifiques
get_airports_by_countries(['spain', 'italy'])  # → ['BCN', 'MAD', 'FCO', ...]

# Récupérer uniquement les aéroports côtiers
get_coastal_airports_by_countries(['france', 'spain'], coastal_only=True)

# Obtenir le nom d'un aéroport
get_airport_name('BCN')  # → 'Barcelona-El Prat Airport'

# Obtenir toutes les infos d'un aéroport
get_airport_info('BCN')  # → {'name': '...', 'coastal': True, 'sea': 'Mediterranean', ...}
```

---

## 🔌 Intégration dans Flask

### Initialisation (app.py)

```python
from config import Config
from services import (
    FlightSearchService, WeatherService, RyanairLinkService,
    AccommodationService, GoogleHotelsService, GooglePlacesService
)

# Initialize services
flight_service = FlightSearchService()
weather_service = WeatherService(app.config['OPENWEATHER_API_KEY'])
hotel_service = GoogleHotelsService(app.config)
google_places_service = GooglePlacesService(app.config['GOOGLE_MAPS_API_KEY'])
```

### Routes API principales

#### POST `/api/search` - Recherche de vols
```javascript
fetch('/api/search', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        departure_airports: ['CRL'],
        departure_date_from: '2025-12-01',
        departure_date_to: '2025-12-15',
        min_stay_duration: 5,
        theme: 'beach',
        include_weather: true
    })
})
```

#### GET `/api/hotels/search` - Recherche d'hôtels
```javascript
fetch('/api/hotels/search?' + new URLSearchParams({
    destination: 'BCN',
    checkin: '2025-12-05',
    checkout: '2025-12-09',
    adults: 2,
    price_max: 100,
    sort: '8'
}))
```

#### GET `/api/restaurants/<destination>` - Recherche de restaurants
```javascript
fetch('/api/restaurants/BCN?' + new URLSearchParams({
    cuisine_type: 'italian',
    price_level: 2,
    min_rating: 4.0
}))
```

---

## 🔑 Variables d'environnement (.env)

```env
# OpenWeather API (gratuit : 1000 calls/jour)
OPENWEATHER_API_KEY=your_openweather_key

# SERP API pour Google Hotels (gratuit : 100 searches/mois)
SERPAPI_KEY=your_serpapi_key

# Google Maps API pour Places et activités
GOOGLE_MAPS_API_KEY=your_google_maps_key

# Amadeus API (optionnel, non utilisé actuellement)
API_KEY=your_amadeus_key
API_SECRET=your_amadeus_secret
```

---

## 📊 Limites et quotas

| Service | API utilisée | Plan gratuit | Limite |
|---------|--------------|--------------|--------|
| **FlightSearchService** | Ryanair (unofficial) | Oui | Illimité (pas d'API officielle) |
| **WeatherService** | OpenWeather | Oui | 1000 calls/jour |
| **GoogleHotelsService** | SERP API | Oui | 100 searches/mois |
| **GooglePlacesService** | Google Places | Oui | $200 de crédit/mois (~40k requests) |

---

## 🛠️ Gestion des erreurs

Tous les services implémentent une gestion d'erreurs robuste :

### FlightSearchService
- Continue la recherche même si une route échoue
- Utilise `try/except` sur chaque destination
- Retourne une liste vide si tout échoue

### GoogleHotelsService
- Fallback vers liens Booking.com/Hotels.com si SERP API échoue
- Conversion automatique USD → EUR
- Gestion des prix manquants (affiche "Prix non disponible")

### GooglePlacesService
- Fallback vers suggestions génériques si API échoue
- Validation des coordonnées avant recherche
- Filtre les résultats sans nom ou note trop basse

### Exemple de gestion d'erreur robuste

```python
try:
    hotels = hotel_service.search_hotels('BCN', '2025-12-05', '2025-12-09')
    if hotels['total_results'] == 0:
        # Afficher les liens de fallback
        print("Aucun hôtel trouvé, voir liens directs :")
        for link in hotels.get('booking_links', []):
            print(f"{link['name']}: {link['url']}")
except Exception as e:
    print(f"Erreur : {e}")
    # L'app continue de fonctionner
```

---

## 🚀 Améliorations futures possibles

### FlightSearchService
- [ ] Cache Redis pour éviter les recherches redondantes
- [ ] Support multi-devises (USD, GBP, etc.)
- [ ] Alertes prix (notifications si prix baisse)

### GoogleHotelsService
- [ ] Géolocalisation précise (quartiers spécifiques)
- [ ] Comparaison de prix multi-plateformes
- [ ] Filtres avancés (piscine, parking, petit-déjeuner)

### GooglePlacesService
- [ ] Itinéraires suggérés (jour par jour)
- [ ] Réservations de restaurants
- [ ] Billets d'attractions en direct

### Général
- [ ] Tests unitaires pour chaque service
- [ ] Rate limiting et retry automatique
- [ ] Logs structurés (JSON) pour monitoring
- [ ] Docker compose avec Redis pour cache

---

## 📝 Notes de développement

### Pourquoi des services séparés ?

1. **Maintenabilité** : Chaque service est isolé, facile à tester et modifier
2. **Réutilisabilité** : Les services peuvent être utilisés dans d'autres projets
3. **Scalabilité** : Facile de déplacer un service vers un microservice séparé
4. **Testabilité** : Tests unitaires plus simples à écrire

### Architecture recommandée

```
services/
├── __init__.py           # Exports all services
├── flight_service.py     # FlightSearchService
├── weather_service.py    # WeatherService
├── ryanair_service.py    # RyanairLinkService
├── hotel_service.py      # GoogleHotelsService
└── google_places_service.py  # GooglePlacesService
```

### Bonnes pratiques

1. **Chaque service est une classe** avec méthodes bien définies
2. **Injection de dépendances** via constructeur (`__init__`)
3. **Gestion d'erreurs** avec try/except et retours par défaut
4. **Documentation** : docstrings pour chaque méthode publique
5. **Typage** : Utiliser des dict typés pour les paramètres complexes

---

## 📚 Ressources

- [Ryanair Python Package](https://github.com/costaparas/Ryanair-py)
- [OpenWeather API Docs](https://openweathermap.org/api)
- [SERP API Documentation](https://serpapi.com/google-hotels-api)
- [Google Places API](https://developers.google.com/maps/documentation/places/web-service)
- [Flask Documentation](https://flask.palletsprojects.com/)
