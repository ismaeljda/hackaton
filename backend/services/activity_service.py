import requests
import os

class ActivityService:
    def __init__(self):
        self.google_maps_api_key = os.environ.get('GOOGLE_MAPS_API_KEY') or os.environ.get('GOOGLE_MAP_API')
        self.base_url = "https://maps.googleapis.com/maps/api/place"
        
        # Coordonnées des villes principales
        self.city_coordinates = {
            'paris': (48.8566, 2.3522),
            'lisbonne': (38.7223, -9.1393),
            'barcelone': (41.3851, 2.1734),
            'rome': (41.9028, 12.4964),
            'madrid': (40.4168, -3.7038),
            'londres': (51.5074, -0.1278),
            'berlin': (52.5200, 13.4050),
            'amsterdam': (52.3676, 4.9041),
            'vienne': (48.2082, 16.3738),
            'prague': (50.0755, 14.4378),
            'budapest': (47.4979, 19.0402),
            'athènes': (37.9838, 23.7275),
            'dublin': (53.3498, -6.2603),
            'edimbourg': (55.9533, -3.1883),
            'stockholm': (59.3293, 18.0686),
            'copenhague': (55.6761, 12.5683),
            'oslo': (59.9139, 10.7522),
            'helsinki': (60.1699, 24.9384),
            'bruxelles': (50.8503, 4.3517),
            'zurich': (47.3769, 8.5417),
            'genève': (46.2044, 6.1432),
            'milan': (45.4642, 9.1900),
            'venise': (45.4408, 12.3155),
            'florence': (43.7696, 11.2558),
            'naples': (40.8518, 14.2681),
            'porto': (41.1579, -8.6291),
            'sevilla': (37.3891, -5.9845),
            'valencia': (39.4699, -0.3763),
            'nice': (43.7102, 7.2620),
            'marseille': (43.2965, 5.3698),
            'lyon': (45.7640, 4.8357),
            'bordeaux': (44.8378, -0.5792),
            'toulouse': (43.6047, 1.4442),
            'strasbourg': (48.5734, 7.7521),
            'nantes': (47.2184, -1.5536),
        }
    
    def search_activities(self, destination_city: str):
        """Search for activities using Google Places API"""
        city_lower = destination_city.lower()
        coordinates = self.city_coordinates.get(city_lower)
        
        if not coordinates:
            return self._get_fallback_activities(destination_city)
        
        if not self.google_maps_api_key:
            return self._get_fallback_activities(destination_city)
        
        lat, lng = coordinates
        activities = []
        
        try:
            # Rechercher des attractions touristiques
            attractions = self._search_places(lat, lng, 'tourist_attraction', limit=6)
            activities.extend(self._format_activities(attractions, 'Visite'))
            
            # Rechercher des musées
            museums = self._search_places(lat, lng, 'museum', limit=4)
            activities.extend(self._format_activities(museums, 'Culture'))
            
            # Rechercher des parcs
            parks = self._search_places(lat, lng, 'park', limit=4)
            activities.extend(self._format_activities(parks, 'Nature'))
            
            # Rechercher des restaurants
            restaurants = self._search_places(lat, lng, 'restaurant', limit=4)
            activities.extend(self._format_activities(restaurants, 'Gastronomie'))
            
        except Exception as e:
            print(f"Activity search error: {e}")
            return self._get_fallback_activities(destination_city)
        
        return activities[:12]  # Limiter à 12 activités
    
    def _search_places(self, lat, lng, place_type, radius=15000, limit=10):
        """Search for places using Google Places API"""
        if not self.google_maps_api_key:
            return []
        
        params = {
            'location': f"{lat},{lng}",
            'radius': radius,
            'type': place_type,
            'key': self.google_maps_api_key
        }
        
        try:
            response = requests.get(f"{self.base_url}/nearbysearch/json", params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'OK':
                    places = data.get('results', [])
                    places = [p for p in places if p.get('name') and p.get('rating', 0) > 3.5]
                    places = sorted(places, key=lambda x: x.get('rating', 0), reverse=True)
                    return places[:limit]
        except Exception as e:
            print(f"Places API error: {e}")
        
        return []
    
    def _format_activities(self, places, category):
        """Format places as activities"""
        activities = []
        for place in places:
            activities.append({
                'name': place.get('name', 'Activité'),
                'category': category,
                'price': self._estimate_price(category),
                'duration': self._estimate_duration(category),
                'image': self._get_photo_url(place.get('photos', [])),
                'description': f"Activité recommandée avec {place.get('user_ratings_total', 0)} avis",
                'rating': round(place.get('rating', 4.0), 1)
            })
        return activities
    
    def _estimate_price(self, category):
        """Estimate activity price based on category"""
        prices = {
            'Visite': 35,
            'Culture': 15,
            'Nature': 0,
            'Gastronomie': 50,
            'Aventure': 60,
            'Sport': 25,
        }
        return prices.get(category, 30)
    
    def _estimate_duration(self, category):
        """Estimate activity duration"""
        durations = {
            'Visite': '3h',
            'Culture': '2h',
            'Nature': '2h',
            'Gastronomie': '2h30',
            'Aventure': '4h',
            'Sport': '2h',
        }
        return durations.get(category, '2h')
    
    def _get_photo_url(self, photos):
        """Get photo URL from Google Places"""
        if not photos or not self.google_maps_api_key:
            return None
        
        photo_ref = photos[0].get('photo_reference')
        if photo_ref:
            return f"{self.base_url}/photo?maxwidth=400&photoreference={photo_ref}&key={self.google_maps_api_key}"
        
        return None
    
    def _get_fallback_activities(self, city_name):
        """Fallback activities when API fails"""
        return [
            {
                'name': f'Visite guidée de {city_name}',
                'category': 'Visite',
                'price': 35,
                'duration': '3h',
                'image': None,
                'description': f'Découvrez les secrets de {city_name}',
                'rating': 4.7
            },
            {
                'name': f'Cours de cuisine locale',
                'category': 'Gastronomie',
                'price': 75,
                'duration': '2h30',
                'image': None,
                'description': f'Apprenez les spécialités de {city_name}',
                'rating': 4.8
            },
            {
                'name': f'Excursion en bateau',
                'category': 'Aventure',
                'price': 55,
                'duration': '4h',
                'image': None,
                'description': f'Croisière autour de {city_name}',
                'rating': 4.9
            },
        ]
