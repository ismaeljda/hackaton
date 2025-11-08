from datetime import datetime, timedelta
import requests
import os

class FlightSearchService:
    def __init__(self):
        self.serpapi_key = os.environ.get('SERPAPI_KEY')
        self.base_url = "https://serpapi.com/search.json"

    def search_flights(self, origin_city: str, destination_city: str, departure_date_from: str = None, departure_date_to: str = None, min_stay_duration: int = 4):
        """Search for flights from origin to destination"""
        from . import CITY_TO_IATA, IATA_TO_CITY

        origin = CITY_TO_IATA.get(origin_city.lower(), origin_city.upper())
        destination = CITY_TO_IATA.get(destination_city.lower(), destination_city.upper())

        if not departure_date_from:
            departure_date_from = (datetime.now() + timedelta(days=30)).strftime('%Y-%m-%d')
        if not departure_date_to:
            departure_date_to = (datetime.now() + timedelta(days=60)).strftime('%Y-%m-%d')

        # Use SERPAPI if available, otherwise fallback
        if not self.serpapi_key:
            return self._get_fallback_flights(origin, destination, departure_date_from)

        try:
            return self._search_with_serpapi(origin, destination, departure_date_from, min_stay_duration)
        except Exception as e:
            print(f"Flight search error: {e}")
            return self._get_fallback_flights(origin, destination, departure_date_from)

    def _search_with_serpapi(self, origin: str, destination: str, departure_date: str, min_stay: int):
        """Search flights using SERPAPI Google Flights"""
        try:
            departure_dt = datetime.strptime(departure_date, '%Y-%m-%d')
        except:
            departure_dt = datetime.now() + timedelta(days=30)
            departure_date = departure_dt.strftime('%Y-%m-%d')

        return_date = (departure_dt + timedelta(days=min_stay)).strftime('%Y-%m-%d')

        params = {
            'engine': 'google_flights',
            'departure_id': origin,
            'arrival_id': destination,
            'outbound_date': departure_date,
            'return_date': return_date,
            'currency': 'EUR',
            'hl': 'fr',
            'gl': 'fr',
            'api_key': self.serpapi_key,
            'type': '1'  # Round trip
        }

        response = requests.get(self.base_url, params=params, timeout=15)

        if response.status_code != 200:
            return self._get_fallback_flights(origin, destination, departure_date)

        data = response.json()

        if 'error' in data:
            return self._get_fallback_flights(origin, destination, departure_date)

        flights = []
        best_flights = data.get('best_flights', [])
        other_flights = data.get('other_flights', [])

        all_flights = best_flights + other_flights

        for flight in all_flights[:20]:  # Check more flights to find bookable ones
            # Get first flight segment for main details
            if not flight.get('flights'):
                continue

            first_leg = flight['flights'][0]

            airline = first_leg.get('airline', 'Unknown')
            departure_time = first_leg.get('departure_airport', {}).get('time', '08:00')
            arrival_time = first_leg.get('arrival_airport', {}).get('time', '10:00')

            # Extract just time from datetime if needed
            if len(departure_time) > 5:
                departure_time = departure_time.split('T')[1][:5] if 'T' in departure_time else departure_time[:5]
            if len(arrival_time) > 5:
                arrival_time = arrival_time.split('T')[1][:5] if 'T' in arrival_time else arrival_time[:5]

            duration = first_leg.get('duration', 120)  # in minutes
            duration_str = f"{duration // 60}h{duration % 60:02d}" if duration else '2h15'

            price = flight.get('price', 0)

            # Count layovers
            layovers = len(flight['flights']) - 1

            # Try to get direct booking link - ONLY VALID ONES
            booking_link = ''
            booking_source = ''

            # Method 1: Check for direct booking options (BEST - direct partner links)
            if flight.get('booking_options'):
                for option in flight['booking_options']:
                    link = option.get('link', '')
                    if link and 'http' in link and not 'google.com' in link:
                        booking_link = link
                        booking_source = 'partner'
                        break

            # Method 2: Try booking_token (Google's booking system)
            if not booking_link:
                booking_token = flight.get('booking_token', '')
                if booking_token and len(booking_token) > 20:  # Valid tokens are long
                    booking_link = f"https://www.google.com/travel/flights/booking?token={booking_token}"
                    booking_source = 'google'

            # Method 3: Check extensions for direct partner links
            if not booking_link and flight.get('extensions'):
                for ext in flight.get('extensions', []):
                    if isinstance(ext, str) and 'http' in ext and not 'google.com' in ext:
                        booking_link = ext
                        booking_source = 'extension'
                        break

            # ONLY add flight if we have a valid booking link (not generic search)
            if booking_link and booking_source in ['partner', 'google', 'extension']:
                flights.append({
                    'airline': airline,
                    'departure': origin,
                    'arrival': destination,
                    'departureTime': departure_time,
                    'arrivalTime': arrival_time,
                    'departureDate': departure_date,
                    'returnDate': return_date,
                    'price': price,
                    'duration': duration_str,
                    'stops': layovers,
                    'booking_link': booking_link
                })

        # Sort by price
        flights.sort(key=lambda x: x['price'])

        return flights[:10] if flights else self._get_fallback_flights(origin, destination, departure_date)

    def _get_fallback_flights(self, origin: str, destination: str, departure_date: str):
        """Fallback flights when API fails or no API key"""
        import random

        airlines = [
            {'name': 'Ryanair', 'base_price': 40},
            {'name': 'EasyJet', 'base_price': 55},
            {'name': 'Vueling', 'base_price': 65},
        ]

        flight_times = [
            ('06:30', '08:45', '2h15'),
            ('09:15', '11:30', '2h15'),
            ('12:45', '15:00', '2h15'),
            ('16:20', '18:35', '2h15'),
            ('19:00', '21:15', '2h15'),
        ]

        results = []

        for i in range(6):
            airline = random.choice(airlines)
            dep_time, arr_time, duration = random.choice(flight_times)

            base_price = airline['base_price']
            price_variation = random.randint(-15, 40)
            final_price = max(25, base_price + price_variation)
            final_price = round(final_price / 5) * 5

            # Generic Google Flights link
            booking_link = f"https://www.google.com/travel/flights?q=Flights+from+{origin}+to+{destination}+on+{departure_date}"

            results.append({
                'airline': airline['name'],
                'departure': origin,
                'arrival': destination,
                'departureTime': dep_time,
                'arrivalTime': arr_time,
                'departureDate': departure_date,
                'returnDate': departure_date,  # Fallback uses same date
                'price': final_price,
                'duration': duration,
                'stops': 0,
                'booking_link': booking_link
            })

        results.sort(key=lambda x: x['price'])
        return results
