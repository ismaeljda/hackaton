from flask import Flask, request, jsonify
from datetime import datetime
from flight_search import FlightSearch
from airports import AIRPORTS, THEMES, city_to_iata

app = Flask(__name__)
flight_search = FlightSearch()

@app.route('/health', methods=['GET'])
def health():
    """Vérifier que l'API fonctionne"""
    return jsonify({'status': 'ok'}), 200

@app.route('/airports', methods=['GET'])
def get_airports():
    """Récupérer la liste des aéroports"""
    # Aéroports de départ (Belgique)
    departure = [
        {'code': code, 'name': info['name']}
        for code, info in AIRPORTS.items()
        if info['country'] == 'Belgique'
    ]

    # Destinations (hors Belgique)
    destinations = [
        {
            'code': code,
            'name': info['name'],
            'country': info['country'],
            'coastal': info['coastal'],
            'themes': info['themes']
        }
        for code, info in AIRPORTS.items()
        if info['country'] != 'Belgique'
    ]

    return jsonify({
        'departure_airports': departure,
        'destinations': destinations
    }), 200

@app.route('/themes', methods=['GET'])
def get_themes():
    """Récupérer les types de voyage disponibles"""
    themes_list = [
        {'id': theme_id, 'name': name}
        for theme_id, name in THEMES.items()
    ]
    return jsonify({'themes': themes_list}), 200

@app.route('/search', methods=['POST'])
def search():
    """
    Rechercher des vols

    Body JSON:
    {
        "origin_city": "Charleroi",           // Ville de départ
        "destination_city": "Barcelona",      // Ville de destination
        "departure_date": "2025-12-15",       // Date de départ
        "return_date": "2025-12-20"           // Date de retour (optionnel)
    }
    """
    try:
        data = request.json

        # Paramètres obligatoires
        origin_city = data.get('origin_city', '')
        destination_city = data.get('destination_city', '')
        departure_date = data.get('departure_date')

        if not origin_city or not destination_city or not departure_date:
            return jsonify({
                'error': 'Paramètres manquants: origin_city, destination_city et departure_date sont obligatoires'
            }), 400

        # Convertir les villes en codes IATA
        origin = city_to_iata(origin_city)
        destination = city_to_iata(destination_city)

        if not origin:
            return jsonify({'error': f'Ville de départ inconnue: {origin_city}'}), 400

        if not destination:
            return jsonify({'error': f'Ville de destination inconnue: {destination_city}'}), 400

        # Valider le format de date
        try:
            datetime.strptime(departure_date, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Format de date invalide. Utiliser YYYY-MM-DD'}), 400

        # Paramètres optionnels
        return_date = data.get('return_date')
        if return_date:
            try:
                datetime.strptime(return_date, '%Y-%m-%d')
            except ValueError:
                return jsonify({'error': 'Format de return_date invalide. Utiliser YYYY-MM-DD'}), 400

        # Rechercher les vols pour cette destination spécifique
        from ryanair import Ryanair
        ryanair = Ryanair()

        results = []

        try:
            if return_date:
                # Aller-retour
                trips = ryanair.get_cheapest_return_flights(
                    origin,
                    departure_date,
                    departure_date,
                    return_date,
                    return_date,
                    destination_airport=destination
                )

                for trip in trips:
                    results.append({
                        'type': 'round_trip',
                        'origin': trip.outbound.origin,
                        'destination': trip.outbound.destination,
                        'departure_date': trip.outbound.departureTime,
                        'return_date': trip.inbound.departureTime,
                        'price': round(trip.totalPrice, 2),
                        'currency': 'EUR'
                    })
            else:
                # Aller simple
                flights = ryanair.get_cheapest_flights(
                    origin,
                    departure_date,
                    departure_date,
                    destination_airport=destination
                )

                for flight in flights:
                    results.append({
                        'type': 'one_way',
                        'origin': flight.origin,
                        'destination': flight.destination,
                        'departure_date': flight.departureTime,
                        'price': round(flight.price, 2),
                        'currency': 'EUR'
                    })

            # Trier par prix
            results.sort(key=lambda x: x['price'])

        except Exception as e:
            return jsonify({'error': f'Erreur lors de la recherche de vols: {str(e)}'}), 500

        return jsonify({
            'origin_city': origin_city,
            'origin': origin,
            'destination_city': destination_city,
            'destination': destination,
            'departure_date': departure_date,
            'return_date': return_date,
            'results_count': len(results),
            'flights': results
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
