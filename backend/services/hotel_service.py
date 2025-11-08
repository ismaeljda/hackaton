import requests
import re
import os

class HotelService:
    def __init__(self):
        self.serpapi_key = os.environ.get('SERPAPI_KEY')
        self.base_url = "https://serpapi.com/search.json"
    
    def search_hotels(self, destination_city: str, checkin_date: str = None, checkout_date: str = None, adults: int = 2):
        """Search for hotels using SERP API Google Hotels"""
        from .mappings import IATA_TO_CITY, CITY_TO_IATA
        
        # Convert city name to IATA if needed, then to city name for API
        if destination_city.upper() in IATA_TO_CITY:
            city_name = IATA_TO_CITY[destination_city.upper()]
        elif destination_city.lower() in CITY_TO_IATA:
            iata = CITY_TO_IATA[destination_city.lower()]
            city_name = IATA_TO_CITY.get(iata, destination_city)
        else:
            city_name = destination_city
        
        if not checkin_date:
            from datetime import datetime, timedelta
            checkin_date = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        if not checkout_date:
            from datetime import datetime, timedelta
            checkout_date = (datetime.strptime(checkin_date, '%Y-%m-%d') + timedelta(days=3)).strftime('%Y-%m-%d')
        
        if not self.serpapi_key:
            return self._get_fallback_hotels(city_name, checkin_date, checkout_date)
        
        try:
            params = {
                'engine': 'google_hotels',
                'q': city_name,
                'check_in_date': checkin_date,
                'check_out_date': checkout_date,
                'adults': adults,
                'api_key': self.serpapi_key,
                'hl': 'fr',
                'gl': 'fr',
                'num': '20'
            }
            
            response = requests.get(self.base_url, params=params, timeout=15)
            
            if response.status_code != 200:
                return self._get_fallback_hotels(city_name, checkin_date, checkout_date)
            
            data = response.json()
            
            if 'error' in data:
                return self._get_fallback_hotels(city_name, checkin_date, checkout_date)
            
            hotels = []
            properties = data.get('properties', [])
            
            for hotel in properties[:30]:  # Check more hotels to find bookable ones
                rate_info = hotel.get('rate_per_night', {}) or hotel.get('prices', {}) or hotel.get('price', {})

                price_display = self._extract_price(rate_info)
                price_numeric = self._extract_price_numeric(rate_info)

                hotel_name = hotel.get('name', 'Hotel')

                # Try multiple fields for VALID booking links only
                booking_url = ''
                booking_source = ''

                # Method 1: Direct booking link from hotel data (BEST)
                direct_link = hotel.get('booking_link', '') or hotel.get('link', '')
                if direct_link and 'http' in direct_link and not 'google.com' in direct_link:
                    booking_url = direct_link
                    booking_source = 'direct'

                # Method 2: Check for extension links (Booking.com, Hotels.com, Expedia, etc.)
                if not booking_url and hotel.get('extensions'):
                    for ext in hotel.get('extensions', []):
                        if isinstance(ext, dict):
                            link = ext.get('link', '')
                            # Only accept known booking sites
                            if link and any(site in link.lower() for site in ['booking.com', 'hotels.com', 'expedia', 'agoda', 'trip.com', 'kayak']):
                                booking_url = link
                                booking_source = 'extension'
                                break

                # Method 3: Check serpapi_link
                if not booking_url:
                    serpapi_link = hotel.get('serpapi_link', '')
                    if serpapi_link and 'http' in serpapi_link and not 'google.com' in serpapi_link:
                        booking_url = serpapi_link
                        booking_source = 'serpapi'

                # Method 4: Try extracted_link
                if not booking_url:
                    extracted = hotel.get('extracted_link', '')
                    if extracted and 'http' in extracted and not 'google.com' in extracted:
                        booking_url = extracted
                        booking_source = 'extracted'

                # ONLY add hotel if we have a valid booking link (not generic search)
                if booking_url and booking_source in ['direct', 'extension', 'serpapi', 'extracted']:
                    hotels.append({
                        'name': hotel_name,
                        'rating': hotel.get('overall_rating', 0),
                        'price': price_display or 'Prix sur demande',
                        'price_numeric': price_numeric,
                        'image': hotel.get('images', [{}])[0].get('thumbnail') if hotel.get('images') else None,
                        'description': hotel.get('description', ''),
                        'amenities': hotel.get('amenities', [])[:5],
                        'booking_url': booking_url,
                        'stars': self._extract_stars(hotel.get('hotel_class')),
                        'reviews': hotel.get('reviews', 0),
                    })
            
            return hotels
            
        except Exception as e:
            print(f"Hotel search error: {e}")
            return self._get_fallback_hotels(city_name, checkin_date, checkout_date)
    
    def _extract_price(self, rate_info):
        """Extract price from rate information"""
        if not rate_info:
            return None
        
        if isinstance(rate_info, dict):
            price_fields = ['lowest', 'extracted_lowest', 'before_taxes_fees', 'displayed_price', 'total', 'price']
            for field in price_fields:
                if rate_info.get(field):
                    price = rate_info[field]
                    price_str = str(price).replace('$', '').replace('€', '').replace(',', '').strip()
                    numbers = re.findall(r'\d+\.?\d*', price_str)
                    if numbers:
                        try:
                            price_num = float(numbers[0])
                            if '$' in str(price):
                                price_num *= 0.85  # USD to EUR
                            return f"{int(price_num)}€"
                        except:
                            pass
        
        return None
    
    def _extract_price_numeric(self, rate_info):
        """Extract price as numeric value"""
        if not rate_info:
            return None
        
        if isinstance(rate_info, dict):
            price_fields = ['lowest', 'extracted_lowest', 'before_taxes_fees', 'displayed_price', 'total', 'price']
            for field in price_fields:
                if rate_info.get(field):
                    price = rate_info[field]
                    price_str = str(price).replace('$', '').replace('€', '').replace(',', '').strip()
                    numbers = re.findall(r'\d+\.?\d*', price_str)
                    if numbers:
                        try:
                            price_num = float(numbers[0])
                            if '$' in str(price):
                                price_num *= 0.85
                            return int(price_num)
                        except:
                            pass
        
        return None
    
    def _extract_stars(self, hotel_class_str):
        """Extract number of stars"""
        if not hotel_class_str:
            return 0
        numbers = re.findall(r'(\d+)', str(hotel_class_str))
        if numbers:
            try:
                stars = int(numbers[0])
                if 1 <= stars <= 5:
                    return stars
            except:
                pass
        return 0
    
    def _get_fallback_hotels(self, city_name, checkin_date, checkout_date):
        """Fallback hotels when API fails"""
        return [
            {
                'name': f'Hôtel à {city_name}',
                'rating': 4.0,
                'price': 'Prix sur demande',
                'price_numeric': None,
                'image': None,
                'description': f'Hébergement disponible à {city_name}',
                'amenities': ['WiFi', 'Petit-déjeuner'],
                'booking_url': f"https://www.booking.com/searchresults.html?ss={city_name}&checkin={checkin_date}&checkout={checkout_date}",
                'stars': 3,
                'reviews': 0,
            }
        ]
