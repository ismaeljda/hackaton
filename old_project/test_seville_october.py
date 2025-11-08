#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script for searching cheap Ryanair flights from Charleroi to Seville in October 2025
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

def test_seville_october():
    """Test flight search to Seville for October 2025"""

    print("=== RECHERCHE VOLS CHARLEROI -> SEVILLE - OCTOBRE 2025 ===\n")

    # Initialize flight service
    flight_service = FlightSearchService()

    # Test 1: Tout le mois d'octobre (sejours de 3-7 jours)
    print(">>> RECHERCHE: Tout octobre 2025 (sejours courts)")
    print("-" * 60)

    search_params_october_short = {
        'departure_airports': ['CRL'],  # Charleroi
        'departure_date_from': '2025-10-01',
        'departure_date_to': '2025-10-28',  # Depart jusqu'au 28 pour avoir retour avant fin octobre
        'min_stay_duration': 3,  # Sejour minimum 3 jours
        'target_countries': ['spain'],
        'coastal_only': False  # Seville n'est pas cotiere
    }

    print(f"Periode depart: {search_params_october_short['departure_date_from']} au {search_params_october_short['departure_date_to']}")
    print(f"Duree sejour minimum: {search_params_october_short['min_stay_duration']} jours")
    print("Destination: Seville (SVQ)\n")

    # First search all Spanish destinations
    results_all_spain = flight_service.search_flights(search_params_october_short)

    # Filter only Seville results
    seville_results = [flight for flight in results_all_spain if flight['destination'] == 'SVQ']

    print(f"Resultats trouves pour Seville: {len(seville_results)}")

    if seville_results:
        print("\n*** TOP 15 VOLS SEVILLE LES MOINS CHERS (sejours courts):")
        for i, flight in enumerate(seville_results[:15]):
            # Handle both string and datetime objects
            if isinstance(flight['departure_time'], str):
                departure_date = datetime.strptime(flight['departure_time'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m')
                return_date = datetime.strptime(flight['return_time'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m')
            else:
                departure_date = flight['departure_time'].strftime('%d/%m')
                return_date = flight['return_time'].strftime('%d/%m')

            print(f"{i+1}. Charleroi -> Seville")
            print(f"   Prix total: {flight['total_price']} EUR")
            print(f"   Dates: {departure_date} - {return_date}")
            print(f"   Depart: {flight['departure_time']}")
            print(f"   Retour: {flight['return_time']}")
            print(f"   Lien: {flight['ryanair_link']}")
            print()
    else:
        print("XXX Aucun vol trouve pour Seville en octobre")

    print("\n" + "="*60 + "\n")

    # Test 2: Week-ends longs en octobre
    print(">>> RECHERCHE: Week-ends longs en octobre (sejours 7-10 jours)")
    print("-" * 60)

    search_params_october_long = {
        'departure_airports': ['CRL'],
        'departure_date_from': '2025-10-01',
        'departure_date_to': '2025-10-25',
        'min_stay_duration': 7,  # Sejour 7 jours minimum
        'target_countries': ['spain'],
        'coastal_only': False
    }

    print(f"Periode depart: {search_params_october_long['departure_date_from']} au {search_params_october_long['departure_date_to']}")
    print(f"Duree sejour: {search_params_october_long['min_stay_duration']} jours et plus")

    results_long_spain = flight_service.search_flights(search_params_october_long)
    seville_results_long = [flight for flight in results_long_spain if flight['destination'] == 'SVQ']

    print(f"Resultats trouves pour Seville (sejours longs): {len(seville_results_long)}")

    if seville_results_long:
        print("\n*** TOP 10 VOLS SEVILLE SEJOURS LONGS:")
        for i, flight in enumerate(seville_results_long[:10]):
            if isinstance(flight['departure_time'], str):
                departure_date = datetime.strptime(flight['departure_time'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m')
                return_date = datetime.strptime(flight['return_time'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m')
            else:
                departure_date = flight['departure_time'].strftime('%d/%m')
                return_date = flight['return_time'].strftime('%d/%m')

            print(f"{i+1}. Charleroi -> Seville")
            print(f"   Prix total: {flight['total_price']} EUR")
            print(f"   Dates: {departure_date} - {return_date}")
            print(f"   Lien: {flight['ryanair_link']}")
            print()
    else:
        print("XXX Aucun vol trouve pour sejours longs")

    print("\n" + "="*60 + "\n")

    # Test 3: Periodes specifiques recommandees
    print(">>> RECHERCHE: Periodes optimales (debut/milieu octobre)")
    print("-" * 60)

    # Recherche pour les meilleures periodes météo à Seville
    optimal_periods = [
        {'start': '2025-10-05', 'end': '2025-10-12', 'name': 'Debut octobre'},
        {'start': '2025-10-12', 'end': '2025-10-19', 'name': 'Mi-octobre'},
        {'start': '2025-10-19', 'end': '2025-10-26', 'name': 'Fin octobre'}
    ]

    all_optimal_results = []

    for period in optimal_periods:
        search_params_optimal = {
            'departure_airports': ['CRL'],
            'departure_date_from': period['start'],
            'departure_date_to': period['start'],  # Date fixe
            'min_stay_duration': 5,  # 5 jours
            'target_countries': ['spain'],
            'coastal_only': False
        }

        results_optimal = flight_service.search_flights(search_params_optimal)
        seville_optimal = [flight for flight in results_optimal if flight['destination'] == 'SVQ']

        if seville_optimal:
            best_flight = seville_optimal[0]  # Le moins cher
            if isinstance(best_flight['departure_time'], str):
                departure_date = datetime.strptime(best_flight['departure_time'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m')
                return_date = datetime.strptime(best_flight['return_time'], '%Y-%m-%d %H:%M:%S').strftime('%d/%m')
            else:
                departure_date = best_flight['departure_time'].strftime('%d/%m')
                return_date = best_flight['return_time'].strftime('%d/%m')

            print(f"*** {period['name']} (depart {period['start']}):")
            print(f"    Meilleur prix: {best_flight['total_price']} EUR")
            print(f"    Dates: {departure_date} - {return_date}")
            print(f"    Lien: {best_flight['ryanair_link']}")
            print()

            all_optimal_results.append({
                'period': period['name'],
                'flight': best_flight,
                'price': best_flight['total_price']
            })

    # Trouve la meilleure periode
    if all_optimal_results:
        best_period = min(all_optimal_results, key=lambda x: x['price'])
        print(f"\n*** MEILLEURE PERIODE: {best_period['period']}")
        print(f"    Prix: {best_period['price']} EUR")
        print(f"    Recommandation: Climat ideal et prix optimal")

def print_seville_info():
    """Display info about Seville"""
    print("\n" + "="*60)
    print("INFO - SEVILLE (SVQ)")
    print("="*60)
    print("Aeroport: Seville Airport (SVQ)")
    print("Ville: Seville, Andalousie, Espagne")
    print("Themes: City trip, Couple, Party")
    print("Climat octobre: 18-26°C, ideal pour visiter")
    print("Points d'interet: Alcazar, Cathedrale, Barrio Santa Cruz")
    print("Specialites: Tapas, Flamenco, Architecture mauresque")

if __name__ == "__main__":
    try:
        # Afficher les infos sur Seville
        print_seville_info()

        # Lancer les tests
        test_seville_october()

        print("\n*** Recherche terminee avec succes!")

    except Exception as e:
        print(f"\nXXX Erreur lors de la recherche: {str(e)}")
        import traceback
        traceback.print_exc()