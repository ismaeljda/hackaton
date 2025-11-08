from flask import Flask, jsonify, request
from flask_cors import CORS
from services import FlightSearchService, HotelService, ActivityService
from datetime import datetime, timedelta
import os
import requests
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
CORS(app)

# n8n webhook URL
N8N_WEBHOOK_URL = os.environ.get('N8N_WEBHOOK_URL', '')

# Initialize services
flight_service = FlightSearchService()
hotel_service = HotelService()
activity_service = ActivityService()

@app.route('/', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'message': 'Backend is running'})

@app.route('/api/health', methods=['GET'])
def api_health():
    return jsonify({'status': 'healthy'})

@app.route('/api/flights', methods=['GET'])
def search_flights():
    """Search for flights"""
    try:
        origin = request.args.get('origin', 'CDG')  # Default Paris
        destination = request.args.get('destination')
        
        if not destination:
            return jsonify({'success': False, 'error': 'Destination parameter is required'}), 400
        
        departure_date_from = request.args.get('departure_date_from')
        departure_date_to = request.args.get('departure_date_to')
        min_stay = int(request.args.get('min_stay', 4))
        
        flights = flight_service.search_flights(
            origin_city=origin,
            destination_city=destination,
            departure_date_from=departure_date_from,
            departure_date_to=departure_date_to,
            min_stay_duration=min_stay
        )
        
        return jsonify({
            'success': True,
            'flights': flights,
            'total': len(flights)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/hotels', methods=['GET'])
def search_hotels():
    """Search for hotels"""
    try:
        destination = request.args.get('destination')
        
        if not destination:
            return jsonify({'success': False, 'error': 'Destination parameter is required'}), 400
        
        checkin_date = request.args.get('checkin_date')
        checkout_date = request.args.get('checkout_date')
        adults = int(request.args.get('adults', 2))
        
        hotels = hotel_service.search_hotels(
            destination_city=destination,
            checkin_date=checkin_date,
            checkout_date=checkout_date,
            adults=adults
        )
        
        return jsonify({
            'success': True,
            'hotels': hotels,
            'total': len(hotels)
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/activities', methods=['GET'])
def search_activities():
    """Search for activities"""
    try:
        destination = request.args.get('destination')

        if not destination:
            return jsonify({'success': False, 'error': 'Destination parameter is required'}), 400

        activities = activity_service.search_activities(destination_city=destination)

        return jsonify({
            'success': True,
            'activities': activities,
            'total': len(activities)
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/converse', methods=['POST'])
def converse():
    """Handle chatbot conversation via n8n + Gemini or fallback to local intent detection"""
    try:
        data = request.get_json()
        message = data.get('message', '')

        # Try n8n webhook first if configured
        if N8N_WEBHOOK_URL:
            try:
                n8n_response = requests.post(
                    N8N_WEBHOOK_URL,
                    json={
                        'message': message,
                        'timestamp': datetime.now().isoformat()
                    },
                    timeout=10
                )

                if n8n_response.status_code == 200:
                    n8n_data = n8n_response.json()

                    # n8n should return: { "response": "...", "intent": "...", "destination": "...", "actions": [...] }
                    response = {
                        'text': n8n_data.get('response', 'Désolé, je n\'ai pas compris.'),
                        'actions': n8n_data.get('actions', [])
                    }

                    return jsonify(response)
            except Exception as n8n_error:
                print(f"n8n webhook error: {n8n_error}. Falling back to local intent detection.")

        # Fallback: Local intent detection (if n8n not configured or failed)
        message_lower = message.lower()
        response = {
            'text': '',
            'actions': []
        }

        # Detect hotels intent
        if any(word in message_lower for word in ['hotel', 'hôtel', 'hébergement', 'logement', 'dormir', 'sejour', 'séjour']):
            destination = extract_destination(message_lower)
            if destination:
                response['text'] = f"Parfait ! Je vais vous trouver les meilleurs hôtels à {destination.capitalize()}. Laissez-moi rechercher..."
                response['actions'] = [{
                    'type': 'navigate',
                    'url': f'/hotels?destination={destination}'
                }]
            else:
                response['text'] = "Pour quelle destination souhaitez-vous rechercher des hôtels ?"

        # Detect flights intent
        elif any(word in message_lower for word in ['vol', 'vols', 'avion', 'billet', 'voler', 'partir', 'aller']):
            destination = extract_destination(message_lower)
            if destination:
                response['text'] = f"Parfait ! Je vais vous trouver les meilleurs vols pour {destination.capitalize()}. Laissez-moi rechercher..."
                response['actions'] = [{
                    'type': 'navigate',
                    'url': f'/vols?destination={destination}'
                }]
            else:
                response['text'] = "Pour quelle destination souhaitez-vous rechercher des vols ?"

        # Detect activities intent
        elif any(word in message_lower for word in ['activité', 'activite', 'visite', 'faire', 'attraction', 'chose', 'excursion', 'tour']):
            destination = extract_destination(message_lower)
            if destination:
                response['text'] = f"Parfait ! Je vais vous trouver les meilleures activités à {destination.capitalize()}. Laissez-moi rechercher..."
                response['actions'] = [{
                    'type': 'navigate',
                    'url': f'/activites?destination={destination}'
                }]
            else:
                response['text'] = "Pour quelle destination souhaitez-vous rechercher des activités ?"

        # Default response
        else:
            response['text'] = "Bonjour ! Je suis votre assistant voyage. Je peux vous aider à trouver des vols, des hôtels ou des activités pour votre prochaine destination. Par exemple, dites-moi \"Je veux un vol pour Paris\" ou \"Trouve-moi des hôtels à Barcelone\"."

        return jsonify(response)

    except Exception as e:
        print(f"Error in /api/converse: {str(e)}")
        return jsonify({'text': f'Erreur: {str(e)}'}), 500

def extract_destination(message):
    """Extract destination from message"""
    # Common French prepositions for destinations
    prepositions = ['à', 'a', 'pour', 'vers', 'sur', 'en', 'au']

    words = message.split()
    for i, word in enumerate(words):
        if word in prepositions and i + 1 < len(words):
            # Return the next word(s) as destination
            destination = words[i + 1].strip('.,!?;')
            return destination.lower()

    # Check for common city names even without preposition
    common_cities = ['paris', 'londres', 'barcelone', 'madrid', 'rome', 'lisbonne', 'bruges', 'amsterdam', 'berlin', 'vienne']
    for city in common_cities:
        if city in message:
            return city

    return None

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
