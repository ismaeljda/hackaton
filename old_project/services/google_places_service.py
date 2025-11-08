import requests
import time
from airport_themes import get_airport_info


class GooglePlacesService:
    def __init__(self, api_key):
        """Initialize with Google Maps API key"""
        self.api_key = api_key
        self.base_url = "https://maps.googleapis.com/maps/api/place"
        
        # Mapping aéroports vers coordonnées principales des villes
        self.airport_coordinates = {
            'BCN': (41.3851, 2.1734),    # Barcelona
            'MAD': (40.4168, -3.7038),  # Madrid
            'PMI': (39.5696, 2.6502),   # Palma
            'SDR': (43.4623, -3.8099),  # Santander
            'FCO': (41.9028, 12.4964),  # Rome
            'VCE': (45.4408, 12.3155),  # Venice
            'MXP': (45.4642, 8.7064),   # Milan
            'NAP': (40.8518, 14.2681),  # Naples
            'CDG': (48.8566, 2.3522),   # Paris
            'NCE': (43.7102, 7.2620),   # Nice
            'LIS': (38.7223, -9.1393),  # Lisbon
            'OPO': (41.1579, -8.6291),  # Porto
            'ATH': (37.9755, 23.7348),  # Athens
            'SKG': (40.6401, 22.9444),  # Thessaloniki
            'DUB': (53.3498, -6.2603),  # Dublin
            'STN': (51.5074, -0.1278),  # London
            'LTN': (51.5074, -0.1278),  # London
            'LGW': (51.5074, -0.1278),  # London
            'AMS': (52.3676, 4.9041),   # Amsterdam
            'BER': (52.5200, 13.4050),  # Berlin
            'MUC': (48.1351, 11.5820),  # Munich
            'PRG': (50.0755, 14.4378),  # Prague
            'BUD': (47.4979, 19.0402),  # Budapest
            'WAW': (52.2297, 21.0122),  # Warsaw
            'VIE': (48.2082, 16.3738),  # Vienna
            'ZUR': (47.3769, 8.5417),   # Zurich
            'CPH': (55.6761, 12.5683),  # Copenhagen
            'OSL': (59.9139, 10.7522),  # Oslo
            'ARN': (59.3293, 18.0686),  # Stockholm
        }
    
    def get_airport_coordinates(self, airport_code):
        """Get coordinates for airport or city"""
        return self.airport_coordinates.get(airport_code, None)
    
    def get_activities_for_destination(self, airport_code, theme=None, full_fetch=False):
        """Get activities and restaurants using Google Places API"""
        coordinates = self.get_airport_coordinates(airport_code)
        if not coordinates:
            return self._generate_fallback_activities(airport_code)
        
        lat, lng = coordinates
        
        activities = {
            'gastronomie': [],
            'culture': [],
            'nature': [],
            'loisirs': [],
            'detente': []
        }
        
        try:
            # Search for restaurants
            restaurants = self._search_places(lat, lng, 'restaurant', radius=15000, limit=8)
            activities['gastronomie'].extend(self._format_restaurants(restaurants))
            
            # Search for tourist attractions
            attractions = self._search_places(lat, lng, 'tourist_attraction', radius=15000, limit=6)
            activities['culture'].extend(self._format_attractions(attractions))
            
            # Search for museums
            museums = self._search_places(lat, lng, 'museum', radius=15000, limit=4)
            activities['culture'].extend(self._format_museums(museums))
            
            # Search for parks
            parks = self._search_places(lat, lng, 'park', radius=15000, limit=6)
            activities['nature'].extend(self._format_parks(parks))
            
            # Search for shopping areas
            shopping = self._search_places(lat, lng, 'shopping_mall', radius=15000, limit=4)
            activities['loisirs'].extend(self._format_shopping(shopping))
            
            # Search for spas and wellness
            spas = self._search_places(lat, lng, 'spa', radius=15000, limit=4)
            activities['detente'].extend(self._format_spas(spas))
            
            # Search for bars and nightlife
            bars = self._search_places(lat, lng, 'bar', radius=15000, limit=4)
            activities['loisirs'].extend(self._format_bars(bars))
            
        except Exception as e:
            print(f"Google Places API error: {e}")
            return self._generate_fallback_activities(airport_code)
        
        # Remove empty categories
        activities = {k: v for k, v in activities.items() if v}
        
        return activities if activities else self._generate_fallback_activities(airport_code)
    
    def get_restaurants_for_destination(self, airport_code, cuisine_type=None, price_level=None, min_rating=None):
        """Get restaurants specifically using Google Places API"""
        print(f"DEBUG: Searching restaurants for airport code: {airport_code}")
        print(f"DEBUG: Filters - cuisine_type: {cuisine_type}, price_level: {price_level}, min_rating: {min_rating}")
        
        coordinates = self.get_airport_coordinates(airport_code)
        print(f"DEBUG: Coordinates for {airport_code}: {coordinates}")
        
        if not coordinates:
            print(f"DEBUG: No coordinates found for {airport_code}")
            return []
        
        lat, lng = coordinates
        
        try:
            # Search for restaurants with specific filters
            params = {
                'location': f"{lat},{lng}",
                'radius': 15000,
                'type': 'restaurant',
                'key': self.api_key
            }
            
            # Apply price filter if specified
            if price_level:
                try:
                    price_int = int(price_level)
                    if 1 <= price_int <= 4:
                        params['minprice'] = price_int
                        params['maxprice'] = price_int
                        print(f"DEBUG: Applied price filter: {price_int}")
                except ValueError:
                    print(f"DEBUG: Invalid price level: {price_level}")
            
            # For cuisine, we'll search with keywords
            if cuisine_type:
                cuisine_keywords = self._get_cuisine_keywords(cuisine_type)
                if cuisine_keywords:
                    params['keyword'] = cuisine_keywords
                    print(f"DEBUG: Applied cuisine keyword: {cuisine_keywords}")
            
            print(f"DEBUG: API request params: {params}")
            
            response = requests.get(f"{self.base_url}/nearbysearch/json", params=params, timeout=10)
            
            print(f"DEBUG: API response status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                
                print(f"DEBUG: API response status field: {data.get('status')}")
                print(f"DEBUG: API response keys: {list(data.keys())}")
                
                # Check for API errors
                if data.get('status') == 'REQUEST_DENIED':
                    print(f"DEBUG: Google Places API error: {data.get('error_message', 'Request denied')}")
                    return []
                elif data.get('status') != 'OK':
                    print(f"DEBUG: Google Places API status: {data.get('status')} - {data.get('error_message', '')}")
                    return []
                
                restaurants = data.get('results', [])
                print(f"DEBUG: Raw restaurants found: {len(restaurants)}")
                
                if restaurants:
                    print(f"DEBUG: First restaurant example: {restaurants[0]}")
                
                # Filter out low-rated restaurants and sort by rating
                rating_threshold = max(min_rating or 3.5, 3.5)  # Minimum 3.5 or user's choice
                restaurants_filtered = [r for r in restaurants if r.get('rating', 0) >= rating_threshold and r.get('name')]
                print(f"DEBUG: Applied rating filter >= {rating_threshold}")
                print(f"DEBUG: Restaurants after filtering (rating >= 3.5): {len(restaurants_filtered)}")
                
                restaurants_sorted = sorted(restaurants_filtered, key=lambda x: x.get('rating', 0), reverse=True)
                
                formatted_restaurants = self._format_restaurants_detailed(restaurants_sorted[:20], cuisine_type)
                print(f"DEBUG: Final formatted restaurants: {len(formatted_restaurants)}")
                
                return formatted_restaurants
            else:
                print(f"DEBUG: API request failed with status {response.status_code}")
                print(f"DEBUG: Response content: {response.text}")
                
        except Exception as e:
            print(f"DEBUG: Restaurant search error: {e}")
            import traceback
            print(f"DEBUG: Full traceback: {traceback.format_exc()}")
        
        return []
    
    def _search_places(self, lat, lng, place_type, radius=10000, limit=10):
        """Search for places using Google Places Nearby Search API"""
        params = {
            'location': f"{lat},{lng}",
            'radius': radius,
            'type': place_type,
            'key': self.api_key
        }
        
        response = requests.get(f"{self.base_url}/nearbysearch/json", params=params, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Check for API errors
            if data.get('status') == 'REQUEST_DENIED':
                print(f"Google Places API error: {data.get('error_message', 'Request denied')}")
                raise Exception(f"Google Places API access denied: {data.get('error_message', 'Check API key restrictions')}")
            elif data.get('status') != 'OK':
                print(f"Google Places API status: {data.get('status')} - {data.get('error_message', '')}")
                return []
            
            places = data.get('results', [])
            
            # Filter out places without names and sort by rating
            places = [p for p in places if p.get('name') and p.get('rating', 0) > 3.5]
            places = sorted(places, key=lambda x: x.get('rating', 0), reverse=True)
            
            return places[:limit]
        
        print(f"Google Places API HTTP error: {response.status_code}")
        return []
    
    def _format_restaurants(self, places):
        """Format restaurant data from Google Places"""
        restaurants = []
        for place in places:
            restaurant = {
                'name': place.get('name', 'Restaurant'),
                'category': 'gastronomie',
                'subcategory': 'restaurants_locaux',
                'rating': round(place.get('rating', 4.0), 1),
                'price_range': self._get_price_range(place.get('price_level')),
                'description': f"Restaurant recommandé avec {place.get('user_ratings_total', 0)} avis",
                'address': place.get('vicinity', ''),
                'place_id': place.get('place_id', ''),
                'photo': self._get_photo_url(place.get('photos', []))
            }
            restaurants.append(restaurant)
        return restaurants
    
    def _format_restaurants_detailed(self, places, cuisine_filter=None):
        """Format restaurant data with detailed information for restaurant page"""
        restaurants = []
        for place in places:
            # Extract cuisine type from place types
            cuisine_type = self._extract_cuisine_type(place.get('types', []))
            
            # Apply cuisine filter if specified
            if cuisine_filter and cuisine_type:
                if cuisine_filter.lower() not in cuisine_type.lower():
                    continue
            
            # Get place details for more information
            details = self._get_place_details(place.get('place_id', ''))
            
            # Get photo URL
            photo_url = self._get_photo_url(place.get('photos', []))
            
            restaurant = {
                'name': place.get('name', 'Restaurant'),
                'rating': round(place.get('rating', 0), 1),
                'price_level': place.get('price_level', 2),
                'user_ratings_total': place.get('user_ratings_total', 0),
                'address': place.get('vicinity', ''),
                'cuisine_type': cuisine_type,
                'place_id': place.get('place_id', ''),
                'photo': photo_url,
                'website': details.get('website', ''),
                'phone': details.get('formatted_phone_number', ''),
                'opening_hours': details.get('opening_hours', {}).get('weekday_text', []),
                'has_photo': bool(photo_url)
            }
            
            # Only add restaurants with decent ratings
            if restaurant['rating'] >= 3.5:
                restaurants.append(restaurant)
        
        return restaurants
    
    def _format_attractions(self, places):
        """Format tourist attraction data from Google Places"""
        attractions = []
        for place in places:
            attraction = {
                'name': place.get('name', 'Attraction'),
                'category': 'culture',
                'subcategory': 'monuments',
                'rating': round(place.get('rating', 4.0), 1),
                'price_range': self._guess_attraction_price(place),
                'description': f"Attraction touristique populaire avec {place.get('user_ratings_total', 0)} avis",
                'address': place.get('vicinity', ''),
                'place_id': place.get('place_id', ''),
                'photo': self._get_photo_url(place.get('photos', []))
            }
            attractions.append(attraction)
        return attractions
    
    def _format_museums(self, places):
        """Format museum data from Google Places"""
        museums = []
        for place in places:
            museum = {
                'name': place.get('name', 'Musée'),
                'category': 'culture',
                'subcategory': 'musees',
                'rating': round(place.get('rating', 4.0), 1),
                'price_range': '€€',
                'description': f"Musée avec {place.get('user_ratings_total', 0)} avis visiteurs",
                'address': place.get('vicinity', ''),
                'place_id': place.get('place_id', ''),
                'photo': self._get_photo_url(place.get('photos', []))
            }
            museums.append(museum)
        return museums
    
    def _format_parks(self, places):
        """Format park data from Google Places"""
        parks = []
        for place in places:
            park = {
                'name': place.get('name', 'Parc'),
                'category': 'nature',
                'subcategory': 'parcs',
                'rating': round(place.get('rating', 4.0), 1),
                'price_range': 'Gratuit',
                'description': f"Espace vert pour se détendre avec {place.get('user_ratings_total', 0)} avis",
                'address': place.get('vicinity', ''),
                'place_id': place.get('place_id', ''),
                'photo': self._get_photo_url(place.get('photos', []))
            }
            parks.append(park)
        return parks
    
    def _format_shopping(self, places):
        """Format shopping data from Google Places"""
        shopping_places = []
        for place in places:
            shop = {
                'name': place.get('name', 'Centre commercial'),
                'category': 'loisirs',
                'subcategory': 'shopping',
                'rating': round(place.get('rating', 4.0), 1),
                'price_range': '€€',
                'description': f"Centre commercial avec {place.get('user_ratings_total', 0)} avis",
                'address': place.get('vicinity', ''),
                'place_id': place.get('place_id', ''),
                'photo': self._get_photo_url(place.get('photos', []))
            }
            shopping_places.append(shop)
        return shopping_places
    
    def _format_spas(self, places):
        """Format spa data from Google Places"""
        spas = []
        for place in places:
            spa = {
                'name': place.get('name', 'Spa'),
                'category': 'detente',
                'subcategory': 'spa',
                'rating': round(place.get('rating', 4.0), 1),
                'price_range': '€€€',
                'description': f"Espace détente et bien-être avec {place.get('user_ratings_total', 0)} avis",
                'address': place.get('vicinity', ''),
                'place_id': place.get('place_id', ''),
                'photo': self._get_photo_url(place.get('photos', []))
            }
            spas.append(spa)
        return spas
    
    def _format_bars(self, places):
        """Format bar data from Google Places"""
        bars = []
        for place in places:
            bar = {
                'name': place.get('name', 'Bar'),
                'category': 'loisirs',
                'subcategory': 'vie_nocturne',
                'rating': round(place.get('rating', 4.0), 1),
                'price_range': '€€',
                'description': f"Bar avec ambiance locale, {place.get('user_ratings_total', 0)} avis",
                'address': place.get('vicinity', ''),
                'place_id': place.get('place_id', ''),
                'photo': self._get_photo_url(place.get('photos', []))
            }
            bars.append(bar)
        return bars
    
    def _get_price_range(self, price_level):
        """Convert Google Places price level to our format"""
        if price_level is None:
            return '€€'
        
        price_map = {
            0: '€',
            1: '€',
            2: '€€',
            3: '€€€',
            4: '€€€€'
        }
        return price_map.get(price_level, '€€')
    
    def _guess_attraction_price(self, place):
        """Guess attraction price based on type and name"""
        name = place.get('name', '').lower()
        types = place.get('types', [])
        
        if any(t in types for t in ['church', 'cemetery', 'park']):
            return 'Gratuit'
        elif any(word in name for word in ['museum', 'gallery', 'tower', 'palace']):
            return '€€'
        elif any(word in name for word in ['cathedral', 'church', 'square', 'bridge']):
            return 'Gratuit'
        else:
            return '€'
    
    def _get_photo_url(self, photos):
        """Get photo URL from Google Places photo reference"""
        if not photos:
            return None
        
        photo_ref = photos[0].get('photo_reference')
        if photo_ref:
            return f"{self.base_url}/photo?maxwidth=400&photoreference={photo_ref}&key={self.api_key}"
        
        return None
    
    def _extract_cuisine_type(self, types):
        """Extract cuisine type from Google Places types"""
        cuisine_mapping = {
            'italian_restaurant': 'Italienne',
            'french_restaurant': 'Française', 
            'spanish_restaurant': 'Espagnole',
            'chinese_restaurant': 'Chinoise',
            'japanese_restaurant': 'Japonaise',
            'thai_restaurant': 'Thaïlandaise',
            'indian_restaurant': 'Indienne',
            'mexican_restaurant': 'Mexicaine',
            'american_restaurant': 'Américaine',
            'mediterranean_restaurant': 'Méditerranéenne',
            'seafood_restaurant': 'Fruits de mer',
            'steakhouse': 'Steakhouse',
            'pizza_restaurant': 'Pizza',
            'sushi_restaurant': 'Sushi',
            'vegetarian_restaurant': 'Végétarienne',
            'fast_food_restaurant': 'Fast Food'
        }
        
        for place_type in types:
            if place_type in cuisine_mapping:
                return cuisine_mapping[place_type]
        
        # Default fallback
        if 'restaurant' in types:
            return 'Cuisine locale'
        
        return 'Restaurant'
    
    def _get_place_details(self, place_id):
        """Get detailed information about a place"""
        if not place_id:
            return {}
        
        try:
            params = {
                'place_id': place_id,
                'fields': 'website,formatted_phone_number,opening_hours',
                'key': self.api_key
            }
            
            response = requests.get(f"{self.base_url}/details/json", params=params, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'OK':
                    return data.get('result', {})
        except Exception as e:
            print(f"Place details error: {e}")
        
        return {}
    
    def _get_cuisine_keywords(self, cuisine_type):
        """Convert cuisine filter to search keywords for Google Places API"""
        cuisine_keywords = {
            'italian': 'italian restaurant pizza pasta',
            'french': 'french restaurant bistro',
            'spanish': 'spanish restaurant tapas paella',
            'asian': 'asian restaurant chinese japanese thai sushi',
            'mediterranean': 'mediterranean restaurant greek',
            'american': 'american restaurant burger',
            'mexican': 'mexican restaurant',
            'indian': 'indian restaurant curry'
        }
        
        return cuisine_keywords.get(cuisine_type.lower(), cuisine_type)
    
    def _generate_fallback_activities(self, airport_code):
        """Generate minimal fallback activities when API fails"""
        airport_info = get_airport_info(airport_code)
        city_name = self._extract_city_name_from_airport(airport_info.get('name', ''))
        
        return {
            'culture': [
                {'name': f'Centre historique de {city_name}', 'category': 'culture', 'subcategory': 'quartiers_traditionnels', 'rating': 7.5, 'price_range': 'Gratuit', 'description': 'Exploration du patrimoine architectural'}
            ],
            'gastronomie': [
                {'name': f'Restaurants locaux de {city_name}', 'category': 'gastronomie', 'subcategory': 'restaurants_locaux', 'rating': 7.8, 'price_range': '€€', 'description': 'Découverte des spécialités régionales'}
            ],
            'nature': [
                {'name': f'Espaces verts de {city_name}', 'category': 'nature', 'subcategory': 'parcs', 'rating': 7.6, 'price_range': 'Gratuit', 'description': 'Parcs et jardins pour se détendre'}
            ]
        }
    
    def _extract_city_name_from_airport(self, airport_name):
        """Extract city name from airport name"""
        if not airport_name:
            return "la ville"
        
        city_name = airport_name.lower()
        remove_words = ['airport', 'international', 'airfield', 'aéroport', 'aeroporto']
        for word in remove_words:
            city_name = city_name.replace(word, '')
        
        parts = [part.strip() for part in city_name.split() if len(part.strip()) > 2]
        return parts[0].capitalize() if parts else "la ville"