from datetime import datetime
from ryanair import Ryanair
from airports import get_destinations_by_theme, get_airport_info, search_destinations

class FlightSearch:
    def __init__(self):
        self.ryanair = Ryanair()

    def search(self, origin, departure_date, return_date=None, themes=None, coastal=None, max_results=10):
        """
        Recherche des vols selon les critères

        Args:
            origin: Code aéroport de départ (ex: 'CRL')
            departure_date: Date de départ (format: 'YYYY-MM-DD')
            return_date: Date de retour optionnelle (format: 'YYYY-MM-DD')
            themes: Liste de thèmes (ex: ['beach', 'party'])
            coastal: True pour destinations côtières uniquement
            max_results: Nombre max de résultats

        Returns:
            Liste de vols triés par prix
        """
        # Trouver les destinations selon les critères
        destinations = search_destinations(themes=themes, coastal=coastal)

        if not destinations:
            return []

        results = []

        for dest in destinations:
            try:
                if return_date:
                    # Aller-retour
                    trips = self.ryanair.get_cheapest_return_flights(
                        origin,
                        departure_date,
                        departure_date,
                        return_date,
                        return_date,
                        destination_airport=dest
                    )

                    for trip in trips:
                        dest_info = get_airport_info(trip.outbound.destination)
                        results.append({
                            'type': 'round_trip',
                            'origin': trip.outbound.origin,
                            'destination': trip.outbound.destination,
                            'destination_name': dest_info['name'] if dest_info else trip.outbound.destination,
                            'destination_country': dest_info['country'] if dest_info else '',
                            'themes': dest_info['themes'] if dest_info else [],
                            'coastal': dest_info['coastal'] if dest_info else False,
                            'departure_date': trip.outbound.departureTime,
                            'return_date': trip.inbound.departureTime,
                            'price': round(trip.totalPrice, 2),
                            'currency': 'EUR'
                        })
                else:
                    # Aller simple
                    flights = self.ryanair.get_cheapest_flights(
                        origin,
                        departure_date,
                        departure_date,
                        destination_airport=dest
                    )

                    for flight in flights:
                        dest_info = get_airport_info(flight.destination)
                        results.append({
                            'type': 'one_way',
                            'origin': flight.origin,
                            'destination': flight.destination,
                            'destination_name': dest_info['name'] if dest_info else flight.destination,
                            'destination_country': dest_info['country'] if dest_info else '',
                            'themes': dest_info['themes'] if dest_info else [],
                            'coastal': dest_info['coastal'] if dest_info else False,
                            'departure_date': flight.departureTime,
                            'price': round(flight.price, 2),
                            'currency': 'EUR'
                        })
            except Exception as e:
                # Continue si erreur pour une destination
                continue

        # Trier par prix
        results.sort(key=lambda x: x['price'])

        # Limiter les résultats
        return results[:max_results]
