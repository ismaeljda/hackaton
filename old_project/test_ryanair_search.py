#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for searching cheap Ryanair flights from Charleroi to beach destinations
in Spain and Portugal for specific dates.
"""

import sys
import os
from datetime import datetime, timedelta

# Set UTF-8 encoding for Windows
if sys.platform.startswith('win'):
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach())

sys.path.append(os.path.dirname(__file__))

from services.flight_service import FlightSearchService
from airport_themes import get_airports_by_theme, get_coastal_airports_by_countries

def test_spain_portugal_beach_flights():
    """Test flight search to Spanish and Portuguese beach destinations"""

    print("=== TEST RYANAIR API - VOLS PAS CHER DEPUIS CHARLEROI ===\n")

    # Initialize flight service
    flight_service = FlightSearchService()

    # Test 1: Dates spécifiques (28/09/25 - 08/10/25)
    print(">>> TEST 1: Vols du 28/09/25 au 08/10/25")
    print("-" * 50)

    search_params_specific = {
        'departure_airports': ['CRL'],  # Charleroi
        'departure_date_from': '2025-09-28',
        'departure_date_to': '2025-09-28',
        'min_stay_duration': 10,  # 10 jours de séjour
        'target_countries': ['spain', 'portugal'],
        'coastal_only': True  # Seulement les destinations côtières
    }

    print(f"Départ: {search_params_specific['departure_date_from']}")
    print(f"Retour: vers le {search_params_specific['departure_date_to']}")
    print(f"Durée séjour: {search_params_specific['min_stay_duration']} jours")
    print("Destinations: Plages d'Espagne et du Portugal\n")

    results_specific = flight_service.search_flights(search_params_specific)

    print(f"Résultats trouvés: {len(results_specific)}")

    if results_specific:
        print("\n*** TOP 10 VOLS LES MOINS CHERS:")
        for i, flight in enumerate(results_specific[:10]):
            print(f"{i+1}. {flight['origin_name']} -> {flight['destination_info']['name']}")
            print(f"   Prix total: {flight['total_price']} EUR")
            print(f"   Depart: {flight['departure_time']}")
            print(f"   Retour: {flight['return_time']}")
            print(f"   Lien: {flight['ryanair_link']}")
            print()
    else:
        print("XXX Aucun vol trouve pour ces dates specifiques")

    print("\n" + "="*60 + "\n")

    # Test 2: Recherche d'une semaine flexible
    print(">>> TEST 2: Vols pour une semaine (dates flexibles)")
    print("-" * 50)

    search_params_week = {
        'departure_airports': ['CRL'],
        'departure_date_from': '2025-09-28',
        'departure_date_to': '2025-10-05',  # Fenêtre de départ d'une semaine
        'min_stay_duration': 7,  # 7 jours de séjour
        'target_countries': ['spain', 'portugal'],
        'coastal_only': True
    }

    print(f"Fenêtre départ: {search_params_week['departure_date_from']} au {search_params_week['departure_date_to']}")
    print(f"Durée séjour: {search_params_week['min_stay_duration']} jours")
    print("Destinations: Plages d'Espagne et du Portugal\n")

    results_week = flight_service.search_flights(search_params_week)

    print(f"Résultats trouvés: {len(results_week)}")

    if results_week:
        print("\n*** TOP 15 VOLS LES MOINS CHERS (semaine flexible):")
        for i, flight in enumerate(results_week[:15]):
            # Handle both string and datetime objects
            if isinstance(flight['departure_time'], str):
                departure_date = datetime.strptime(flight['departure_time'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m')
                return_date = datetime.strptime(flight['return_time'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m')
            else:
                departure_date = flight['departure_time'].strftime('%d/%m')
                return_date = flight['return_time'].strftime('%d/%m')
            print(f"{i+1}. {flight['origin_name']} -> {flight['destination_info']['name']}")
            print(f"   Prix total: {flight['total_price']} EUR")
            print(f"   Dates: {departure_date} - {return_date}")
            print(f"   Lien: {flight['ryanair_link']}")
            print()
    else:
        print("XXX Aucun vol trouve pour cette periode")

    print("\n" + "="*60 + "\n")

    # Test 3: Recherche thématique "beach"
    print(">>> TEST 3: Recherche thematique 'plage' (toute l'Europe)")
    print("-" * 50)

    search_params_beach = {
        'departure_airports': ['CRL'],
        'departure_date_from': '2025-09-28',
        'departure_date_to': '2025-10-05',
        'min_stay_duration': 7,
        'theme': 'beach'  # Utilise la recherche thématique
    }

    print(f"Fenêtre départ: {search_params_beach['departure_date_from']} au {search_params_beach['departure_date_to']}")
    print(f"Durée séjour: {search_params_beach['min_stay_duration']} jours")
    print("Thème: Destinations plage (toute l'Europe)\n")

    results_beach = flight_service.search_flights(search_params_beach)

    print(f"Résultats trouvés: {len(results_beach)}")

    if results_beach:
        print("\n*** TOP 20 DESTINATIONS PLAGE LES MOINS CHERES:")
        for i, flight in enumerate(results_beach[:20]):
            # Handle both string and datetime objects
            if isinstance(flight['departure_time'], str):
                departure_date = datetime.strptime(flight['departure_time'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m')
                return_date = datetime.strptime(flight['return_time'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m')
            else:
                departure_date = flight['departure_time'].strftime('%d/%m')
                return_date = flight['return_time'].strftime('%d/%m')
            country = flight['destination_info'].get('country', 'N/A')
            print(f"{i+1}. {flight['destination_info']['name']} ({country})")
            print(f"   Prix total: {flight['total_price']} EUR")
            print(f"   Dates: {departure_date} - {return_date}")
            print(f"   Mer: {flight['destination_info'].get('sea', 'N/A')}")
            print(f"   Lien: {flight['ryanair_link']}")
            print()
    else:
        print("XXX Aucun vol trouve pour le theme plage")

def print_available_destinations():
    """Affiche les destinations disponibles pour debug"""
    print("\n" + "="*60)
    print("MAP - DESTINATIONS DISPONIBLES")
    print("="*60)

    # Destinations Espagne côtières
    spain_coastal = get_coastal_airports_by_countries(['spain'], coastal_only=True)
    print(f"\nESPAGNE - Destinations cotieres ({len(spain_coastal)}):")
    for code in spain_coastal:
        from airport_themes import get_airport_info
        info = get_airport_info(code)
        print(f"  • {code}: {info['name']} ({info.get('sea', 'N/A')})")

    # Destinations Portugal côtières
    portugal_coastal = get_coastal_airports_by_countries(['portugal'], coastal_only=True)
    print(f"\nPORTUGAL - Destinations cotieres ({len(portugal_coastal)}):")
    for code in portugal_coastal:
        from airport_themes import get_airport_info
        info = get_airport_info(code)
        print(f"  • {code}: {info['name']} ({info.get('sea', 'N/A')})")

    # Destinations thème plage (toute l'Europe)
    beach_destinations = get_airports_by_theme('beach')
    print(f"\nTHEME PLAGE - Toutes destinations ({len(beach_destinations)}):")
    for code in beach_destinations[:15]:  # Affiche seulement les 15 premiers
        from airport_themes import get_airport_info
        info = get_airport_info(code)
        print(f"  • {code}: {info['name']} ({info.get('sea', 'N/A')})")
    if len(beach_destinations) > 15:
        print(f"  ... et {len(beach_destinations) - 15} autres destinations")

if __name__ == "__main__":
    try:
        # Afficher les destinations disponibles
        print_available_destinations()

        # Lancer les tests
        test_spain_portugal_beach_flights()

        print("\n*** Tests termines avec succes!")

    except Exception as e:
        print(f"\nXXX Erreur lors du test: {str(e)}")
        import traceback
        traceback.print_exc()