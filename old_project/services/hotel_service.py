"""
Google Hotels Service for searching hotels using SERP API
"""
import requests
import re
import time
from airport_themes import get_airport_info

# IATA code to city name mapping
IATA_TO_CITY = {
    # France
    'CDG': 'Paris',
    'ORY': 'Paris', 
    'NCE': 'Nice',
    'LYS': 'Lyon',
    'MRS': 'Marseille',
    'TLS': 'Toulouse',
    'BOD': 'Bordeaux',
    'NTE': 'Nantes',
    'BIQ': 'Biarritz',
    'CFR': 'Caen',
    'BVA': 'Paris',
    'MLH': 'Mulhouse',
    
    # Spain
    'BCN': 'Barcelona',
    'MAD': 'Madrid',
    'AGP': 'Malaga',
    'PMI': 'Palma',
    'LPA': 'Las Palmas',
    'ACE': 'Lanzarote',
    'SVQ': 'Seville',
    'VLC': 'Valencia',
    'BIO': 'Bilbao',
    'SDR': 'Santander',
    'SCQ': 'Santiago',
    'VGO': 'Vigo',
    'LEI': 'Almeria',
    'ALC': 'Alicante',
    'IBZ': 'Ibiza',
    'MAH': 'Menorca',
    'TFS': 'Tenerife',
    
    # Italy
    'FCO': 'Rome',
    'CIA': 'Rome',
    'MXP': 'Milan',
    'LIN': 'Milan',
    'BGY': 'Bergamo',
    'NAP': 'Naples',
    'CTA': 'Catania',
    'PMO': 'Palermo',
    'BLQ': 'Bologna',
    'VCE': 'Venice',
    'TSF': 'Venice',
    'FLR': 'Florence',
    'PSA': 'Pisa',
    'BRI': 'Bari',
    'CAG': 'Cagliari',
    'OLB': 'Olbia',
    'AHO': 'Alghero',
    'REG': 'Reggio Calabria',
    'CRV': 'Crotone',
    'SUF': 'Lamezia',
    'TRN': 'Turin',
    'GOA': 'Genoa',
    'VRN': 'Verona',
    'AOI': 'Ancona',
    'PEG': 'Perugia',
    'PSR': 'Pescara',
    
    # Germany
    'FRA': 'Frankfurt',
    'MUC': 'Munich',
    'DUS': 'Dusseldorf',
    'TXL': 'Berlin',
    'SXF': 'Berlin',
    'BER': 'Berlin',
    'HAM': 'Hamburg',
    'STR': 'Stuttgart',
    'CGN': 'Cologne',
    'NUE': 'Nuremberg',
    'HHN': 'Frankfurt-Hahn',
    'FMM': 'Memmingen',
    'DTM': 'Dortmund',
    'FKB': 'Karlsruhe',
    'PAD': 'Paderborn',
    'NRN': 'Weeze',
    'LEJ': 'Leipzig',
    'DRS': 'Dresden',
    
    # UK
    'LGW': 'London',
    'LTN': 'London', 
    'STN': 'London',
    'LHR': 'London',
    'MAN': 'Manchester',
    'EDI': 'Edinburgh',
    'GLA': 'Glasgow',
    'BHX': 'Birmingham',
    'LPL': 'Liverpool',
    'BRS': 'Bristol',
    'EXT': 'Exeter',
    'CWL': 'Cardiff',
    'BFS': 'Belfast',
    'DUB': 'Dublin',
    'ORK': 'Cork',
    'SNN': 'Shannon',
    'NOC': 'Knock',
    
    # Belgium
    'CRL': 'Brussels',
    'BRU': 'Brussels',
    'LGG': 'Liege',
    'OST': 'Ostend',
    'ANR': 'Antwerp',
    
    # Netherlands
    'AMS': 'Amsterdam',
    'EIN': 'Eindhoven',
    'MST': 'Maastricht',
    'GRQ': 'Groningen',
    
    # Poland
    'WAW': 'Warsaw',
    'KRK': 'Krakow',
    'GDN': 'Gdansk',
    'WRO': 'Wroclaw',
    'KTW': 'Katowice',
    'POZ': 'Poznan',
    'RZE': 'Rzeszow',
    'BZG': 'Bydgoszcz',
    'LUZ': 'Lublin',
    'SZZ': 'Szczecin',
    'IEG': 'Zielona Gora',
    
    # Other European cities
    'VIE': 'Vienna',
    'PRG': 'Prague', 
    'BUD': 'Budapest',
    'BTS': 'Bratislava',
    'LJU': 'Ljubljana',
    'ZAG': 'Zagreb',
    'SPU': 'Split',
    'DBV': 'Dubrovnik',
    'ZAD': 'Zadar',
    'PUY': 'Pula',
    'RJK': 'Rijeka',
    'OSI': 'Osijek',
    'ATH': 'Athens',
    'CFU': 'Corfu',
    'HER': 'Heraklion',
    'RHO': 'Rhodes',
    'JTR': 'Santorini',
    'SKG': 'Thessaloniki',
    'CHQ': 'Chania',
    'KGS': 'Kos',
    'JMK': 'Mykonos',
    'MLO': 'Milos',
    'JSI': 'Skiathos',
    'VOL': 'Volos',
    'PVK': 'Preveza',
    'ARK': 'Araxos',
    'KIT': 'Kithira',
    'LRS': 'Leros',
    'SOF': 'Sofia',
    'BOJ': 'Burgas',
    'VAR': 'Varna',
    'PDV': 'Plovdiv',
    'OTP': 'Bucharest',
    'CLJ': 'Cluj',
    'TSR': 'Timisoara',
    'IAS': 'Iasi',
    'CND': 'Constanta',
    'SBZ': 'Sibiu',
    'BCM': 'Bacau',
    'OMR': 'Oradea',
    'SUJ': 'Satu Mare',
    'TGM': 'Targu Mures',
    'ARW': 'Arad',
    'CVT': 'Craiova'
}


class GoogleHotelsService:
    def __init__(self, config):
        """
        Initialize the Google Hotels Service
        
        Args:
            config: Configuration object containing API keys
        """
        self.serpapi_key = config.get('SERPAPI_KEY')
        self.base_url = "https://serpapi.com/search.json"
    
    def search_hotels(self, destination, checkin_date, checkout_date, adults=2, **filters):
        """Search for hotels using SERP API Google Hotels"""
        try:
            # Get city name from IATA code using direct mapping
            city_name = IATA_TO_CITY.get(destination, destination)
            
            print(f"DEBUG: destination={destination} -> city_name='{city_name}'")
            
            # Build SERP API parameters
            params = {
                'engine': 'google_hotels',
                'q': city_name,
                'check_in_date': checkin_date,
                'check_out_date': checkout_date,
                'adults': adults,
                'api_key': self.serpapi_key,
                'hl': 'fr',  # Language
                'gl': 'fr',  # Geolocation
                'no_cache': 'false',  # Enable caching for better performance
                'num': '100',  # Request more results (default is often 20-25)
                'start': '0'  # Starting position for results
            }
            
            # Add filters if provided
            if filters.get('price_min'):
                params['price_min'] = filters['price_min']
            if filters.get('price_max'):
                params['price_max'] = filters['price_max']
            if filters.get('hotel_class'):
                params['hotel_class'] = filters['hotel_class']
            if filters.get('free_cancellation'):
                params['free_cancellation'] = '1'
            # Note: Don't pass sort_by to SERP API as it limits results
            # We'll sort on our side after getting all results
            # if filters.get('sort'):
            #     params['sort_by'] = filters['sort']  # 8: lowest price, 1: highest rating
                
            
            response = requests.get(self.base_url, params=params, timeout=15)
            
            if response.status_code != 200:
                print(f"SERP API error: HTTP {response.status_code}")
                return self._get_fallback_hotels(city_name, checkin_date, checkout_date)
            
            data = response.json()
            
            if 'error' in data:
                print(f"SERP API error: {data['error']}")
                return self._get_fallback_hotels(city_name, checkin_date, checkout_date)
            
            hotels = []
            properties = data.get('properties', [])
            
            
            # Check if there are pagination indicators
            has_more_pages = False
            if 'serpapi_pagination' in data:
                pagination = data['serpapi_pagination']
                has_more_pages = 'next' in pagination
            
            # Check total results if available
            total_available = None
            if 'search_information' in data:
                search_info = data['search_information']
                if 'total_results' in search_info:
                    total_available = search_info['total_results']
            
            for hotel in properties[:50]:  # Increased limit to get more results  
                # Try multiple price extraction methods
                rate_info = hotel.get('rate_per_night', {})
                if not rate_info:
                    # Try alternative price fields
                    rate_info = hotel.get('prices', {}) or hotel.get('price', {}) or hotel.get('rates', {})
                
                price_display = self._extract_price(rate_info)
                price_numeric = self._extract_price_numeric(rate_info)
                
                # If still no price, try extracting from raw data
                if not price_display and not price_numeric:
                    price_display = self._extract_price(hotel)
                    price_numeric = self._extract_price_numeric(hotel)
                
                hotel_data = {
                    'name': hotel.get('name', 'Hotel'),
                    'rating': hotel.get('overall_rating', 0),
                    'price': price_display,
                    'price_numeric': price_numeric,  # For sorting and filtering
                    'image': hotel.get('images', [{}])[0].get('thumbnail') if hotel.get('images') else None,
                    'description': hotel.get('description', ''),
                    'amenities': hotel.get('amenities', [])[:5],  # Top 5 amenities
                    'booking_url': hotel.get('booking_link', ''),
                    'stars': self._extract_stars(hotel.get('hotel_class')),
                    'stars_display': hotel.get('hotel_class', ''),
                    'location_rating': hotel.get('location_rating', 0),
                    'reviews': hotel.get('reviews', 0),
                    'free_cancellation': hotel.get('free_cancellation', False),
                    'address': hotel.get('gps_coordinates', {}).get('latitude', ''),
                    'type': self._categorize_hotel(hotel),
                    'details_url': hotel.get('link', '')  # Link for more info
                }
                
                # Apply client-side hotel type filter
                if filters.get('hotel_type'):
                    filter_type = filters['hotel_type'].lower()
                    hotel_type = hotel_data['type'].lower()
                    
                    # Match filter with hotel type
                    if filter_type == 'hotel' and 'hotel' not in hotel_type and 'boutique' not in hotel_type:
                        continue
                    elif filter_type == 'hostel' and 'hostel' not in hotel_type:
                        continue
                    elif filter_type == 'resort' and 'resort' not in hotel_type:
                        continue
                    elif filter_type == 'apartment' and 'apartment' not in hotel_type:
                        continue
                    elif filter_type == 'boutique' and 'boutique' not in hotel_type:
                        continue
                
                # Apply price range filter (only if price is available)
                if filters.get('price_min') or filters.get('price_max'):
                    if hotel_data['price_numeric']:
                        price_num = hotel_data['price_numeric']
                        if filters.get('price_min') and price_num < int(filters['price_min']):
                            continue
                        if filters.get('price_max') and price_num > int(filters['price_max']):
                            continue
                
                hotels.append(hotel_data)
            
            # Strategy: Try with different search parameters to get more variety
            if len(hotels) < 35:
                additional_hotels = self._get_additional_hotels_with_variants(params, city_name)
                
                # Add unique additional hotels
                existing_names = {h['name'] for h in hotels}
                added_count = 0
                for hotel in additional_hotels:
                    if hotel['name'] not in existing_names:
                        hotels.append(hotel)
                        existing_names.add(hotel['name'])
                        added_count += 1
                
            
            # Try to get more results if pagination is available and we have fewer than 40 hotels
            if has_more_pages and len(hotels) < 40:
                additional_hotels = self._get_paginated_results(params, city_name, has_more_pages, len(hotels))
                
                # Add unique additional hotels
                existing_names = {h['name'] for h in hotels}
                for hotel in additional_hotels:
                    if hotel['name'] not in existing_names:
                        hotels.append(hotel)
                        existing_names.add(hotel['name'])
                
            
            # Apply sorting
            if filters.get('sort') == '8':  # Price ascending
                # Separate hotels with and without prices
                hotels_with_prices = [h for h in hotels if h['price_numeric']]
                hotels_without_prices = [h for h in hotels if not h['price_numeric']]
                # Sort hotels with prices by price, put hotels without prices at the end
                hotels_with_prices.sort(key=lambda x: x['price_numeric'])
                hotels = hotels_with_prices + hotels_without_prices
            elif filters.get('sort') == '1':  # Rating descending
                hotels.sort(key=lambda x: x['rating'] if x['rating'] else 0, reverse=True)
            
            return {
                'hotels': hotels,
                'total_results': len(hotels),
                'city': city_name,
                'search_params': params
            }
            
        except Exception as e:
            print(f"Google Hotels service error: {e}")
            import traceback
            print(f"Full traceback: {traceback.format_exc()}")
            return self._get_fallback_hotels(city_name if 'city_name' in locals() else destination, checkin_date, checkout_date)
    
    def _extract_price(self, rate_info):
        """Extract price from rate information"""
        if not rate_info:
            return None
            
            
        if isinstance(rate_info, dict):
            # Try different price fields in order of preference
            price_fields = [
                'lowest', 'extracted_lowest', 'before_taxes_fees', 'displayed_price', 
                'total', 'price', 'rate', 'amount', 'cost', 'value'
            ]
            price = None
            for field in price_fields:
                if rate_info.get(field):
                    price = rate_info.get(field)
                    break
                    
            if price:
                # Remove any existing currency symbols and convert to EUR
                price_str = str(price)
                # Handle unicode currency symbols
                price_clean = price_str.replace('$', '').replace('€', '').replace('US', '').replace('\\u20ac', '€').replace('\\u00a0', '').replace('€', '').replace(',', '').replace('USD', '').replace('EUR', '').strip()
                
                # Extract numbers from string
                numbers = re.findall(r'\d+\.?\d*', price_clean)
                if numbers:
                    try:
                        price_num = float(numbers[0])
                        # Convert from USD to EUR if USD detected
                        if '$' in price_str or 'US' in price_str or 'USD' in price_str:
                            price_num *= 0.85
                        return f"{int(price_num)}€"
                    except Exception as e:
                        pass
            else:
                # Try to find any numeric values in the entire dict
                for key, value in rate_info.items():
                    if isinstance(value, (int, float)) and value > 0 and value < 10000:
                        price_num = float(value) * 0.85  # Assume USD and convert
                        return f"{int(price_num)}€"
                        
        elif isinstance(rate_info, str):
            # Handle string prices directly
            price_clean = rate_info.replace('$', '').replace('€', '').replace('US', '').replace('\\u20ac', '').replace('\\u00a0', '').replace(',', '').replace('USD', '').replace('EUR', '').strip()
            numbers = re.findall(r'\d+\.?\d*', price_clean)
            if numbers:
                try:
                    price_num = float(numbers[0])
                    if '$' in rate_info or 'US' in rate_info or 'USD' in rate_info:
                        price_num *= 0.85
                    return f"{int(price_num)}€"
                except:
                    pass
        elif isinstance(rate_info, (int, float)) and rate_info > 0:
            # Handle numeric prices directly
            price_num = float(rate_info) * 0.85  # Assume USD
            return f"{int(price_num)}€"
        
        return None
    
    def _extract_price_numeric(self, rate_info):
        """Extract price as numeric value for filtering and sorting"""
        if not rate_info:
            return None
            
        if isinstance(rate_info, dict):
            price_fields = [
                'lowest', 'extracted_lowest', 'before_taxes_fees', 'displayed_price', 
                'total', 'price', 'rate', 'amount', 'cost', 'value'
            ]
            price = None
            for field in price_fields:
                if rate_info.get(field):
                    price = rate_info.get(field)
                    break
                    
            if price:
                price_str = str(price)
                price_clean = price_str.replace('$', '').replace('€', '').replace('US', '').replace('\\u20ac', '').replace('\\u00a0', '').replace(',', '').strip()
                
                numbers = re.findall(r'\d+\.?\d*', price_clean)
                if numbers:
                    try:
                        price_num = float(numbers[0])
                        # Convert from USD to EUR if USD detected
                        if '$' in price_str or 'US' in price_str or 'USD' in price_str:
                            price_num *= 0.85
                        return int(price_num)
                    except:
                        pass
            else:
                # Try to find any numeric values in the entire dict
                for key, value in rate_info.items():
                    if isinstance(value, (int, float)) and value > 0 and value < 10000:
                        return int(float(value) * 0.85)  # Assume USD and convert
                        
        elif isinstance(rate_info, str):
            price_clean = rate_info.replace('$', '').replace('€', '').replace('US', '').replace('\\u20ac', '').replace('\\u00a0', '').replace(',', '').replace('USD', '').replace('EUR', '').strip()
            numbers = re.findall(r'\d+\.?\d*', price_clean)
            if numbers:
                try:
                    price_num = float(numbers[0])
                    if '$' in rate_info or 'US' in rate_info or 'USD' in rate_info:
                        price_num *= 0.85
                    return int(price_num)
                except:
                    pass
        elif isinstance(rate_info, (int, float)) and rate_info > 0:
            # Handle numeric prices directly
            return int(float(rate_info) * 0.85)  # Assume USD
        
        return None
    
    def _get_paginated_results(self, base_params, city_name, has_more_pages, current_count):
        """Get additional hotel results using pagination"""
        additional_hotels = []
        page = 1
        max_pages = 3  # Limit to avoid excessive API calls
        
        while has_more_pages and page < max_pages and len(additional_hotels) < 30:
            try:
                # Create new params for next page
                paginated_params = base_params.copy()
                paginated_params['start'] = str(current_count + (page - 1) * 20)  # Offset for pagination
                
                
                response = requests.get(self.base_url, params=paginated_params, timeout=15)
                
                if response.status_code != 200:
                    break
                
                data = response.json()
                
                if 'error' in data:
                    break
                
                properties = data.get('properties', [])
                
                if not properties:
                    break
                
                # Process hotels from this page
                for hotel in properties[:25]:  # Limit per page
                    rate_info = hotel.get('rate_per_night', {})
                    if not rate_info:
                        rate_info = hotel.get('prices', {}) or hotel.get('price', {}) or hotel.get('rates', {})
                    
                    price_display = self._extract_price(rate_info)
                    price_numeric = self._extract_price_numeric(rate_info)
                    
                    if not price_display and not price_numeric:
                        price_display = self._extract_price(hotel)
                        price_numeric = self._extract_price_numeric(hotel)
                    
                    hotel_data = {
                        'name': hotel.get('name', 'Hotel'),
                        'rating': hotel.get('overall_rating', 0),
                        'price': price_display,
                        'price_numeric': price_numeric,
                        'image': hotel.get('images', [{}])[0].get('thumbnail') if hotel.get('images') else None,
                        'description': hotel.get('description', ''),
                        'amenities': hotel.get('amenities', [])[:5],
                        'booking_url': hotel.get('booking_link', ''),
                        'stars': self._extract_stars(hotel.get('hotel_class')),
                        'stars_display': hotel.get('hotel_class', ''),
                        'location_rating': hotel.get('location_rating', 0),
                        'reviews': hotel.get('reviews', 0),
                        'free_cancellation': hotel.get('free_cancellation', False),
                        'address': hotel.get('gps_coordinates', {}).get('latitude', ''),
                        'type': self._categorize_hotel(hotel),
                        'details_url': hotel.get('link', '')
                    }
                    
                    additional_hotels.append(hotel_data)
                
                # Check if more pages are available
                has_more_pages = 'serpapi_pagination' in data and 'next' in data['serpapi_pagination']
                page += 1
                
            except Exception as e:
                break
        
        return additional_hotels
    
    def _get_additional_hotels_with_variants(self, base_params, city_name):
        """Try different search parameters to get more hotel variety"""
        additional_hotels = []
        
        # Different search variants to try
        variants = [
            # Try with different geolocation
            {'gl': 'us', 'hl': 'en'},  # US perspective
            {'gl': 'uk', 'hl': 'en'},  # UK perspective
            
            # Try searching with broader location terms
            {'q': f"hotels near {city_name}"},
            {'q': f"{city_name} accommodation"},
            
            # Try with different currency/region settings
            {'gl': 'de', 'hl': 'de'},  # German perspective (EUR currency)
        ]
        
        for variant_index, variant in enumerate(variants):
            try:
                variant_params = base_params.copy()
                variant_params.update(variant)
                
                
                response = requests.get(self.base_url, params=variant_params, timeout=10)
                
                if response.status_code != 200:
                    continue
                
                data = response.json()
                
                if 'error' in data:
                    continue
                
                properties = data.get('properties', [])
                
                # Process hotels from this variant (limit to avoid too many)
                for hotel in properties[:15]:  # Limit per variant
                    rate_info = hotel.get('rate_per_night', {})
                    if not rate_info:
                        rate_info = hotel.get('prices', {}) or hotel.get('price', {}) or hotel.get('rates', {})
                    
                    price_display = self._extract_price(rate_info)
                    price_numeric = self._extract_price_numeric(rate_info)
                    
                    if not price_display and not price_numeric:
                        price_display = self._extract_price(hotel)
                        price_numeric = self._extract_price_numeric(hotel)
                    
                    hotel_data = {
                        'name': hotel.get('name', 'Hotel'),
                        'rating': hotel.get('overall_rating', 0),
                        'price': price_display,
                        'price_numeric': price_numeric,
                        'image': hotel.get('images', [{}])[0].get('thumbnail') if hotel.get('images') else None,
                        'description': hotel.get('description', ''),
                        'amenities': hotel.get('amenities', [])[:5],
                        'booking_url': hotel.get('booking_link', ''),
                        'stars': self._extract_stars(hotel.get('hotel_class')),
                        'stars_display': hotel.get('hotel_class', ''),
                        'location_rating': hotel.get('location_rating', 0),
                        'reviews': hotel.get('reviews', 0),
                        'free_cancellation': hotel.get('free_cancellation', False),
                        'address': hotel.get('gps_coordinates', {}).get('latitude', ''),
                        'type': self._categorize_hotel(hotel),
                        'details_url': hotel.get('link', '')
                    }
                    
                    additional_hotels.append(hotel_data)
                
                # Don't overwhelm API - small delay between requests
                time.sleep(0.5)
                
            except Exception as e:
                continue
        
        return additional_hotels
    
    def _extract_stars(self, hotel_class_str):
        """Extract number of stars from hotel class string"""
        if not hotel_class_str:
            return 0
            
        # Look for patterns like "4 étoiles", "4-star", "4 star", etc.
        numbers = re.findall(r'(\d+)', str(hotel_class_str))
        if numbers:
            try:
                stars = int(numbers[0])
                if 1 <= stars <= 5:  # Valid star range
                    return stars
            except:
                pass
        return 0
    
    def _categorize_hotel(self, hotel_data):
        """Categorize hotel type based on data"""
        name = hotel_data.get('name', '').lower()
        
        if any(word in name for word in ['hostel', 'auberge', 'backpack']):
            return 'Hostel'
        elif any(word in name for word in ['resort', 'spa']):
            return 'Resort'
        elif any(word in name for word in ['apartment', 'appart', 'residence']):
            return 'Apartment'
        elif any(word in name for word in ['boutique', 'design']):
            return 'Boutique Hotel'
        else:
            return 'Hotel'
    
    
    def _get_fallback_hotels(self, city_name, checkin_date, checkout_date):
        """Fallback when SERP API fails"""
        return {
            'hotels': [],
            'booking_links': [
                {
                    'name': 'Booking.com',
                    'url': f"https://www.booking.com/searchresults.html?ss={city_name}&checkin={checkin_date}&checkout={checkout_date}",
                    'type': 'booking_platform'
                },
                {
                    'name': 'Hotels.com', 
                    'url': f"https://www.hotels.com/search.do?q-destination={city_name}&q-check-in={checkin_date}&q-check-out={checkout_date}",
                    'type': 'hotel_platform'
                }
            ],
            'total_results': 0,
            'city': city_name
        }