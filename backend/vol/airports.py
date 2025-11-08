# Mapping ville -> code IATA
CITY_TO_IATA = {
    # Belgique
    'charleroi': 'CRL',
    'brussels': 'BRU',
    'bruxelles': 'BRU',
    'liege': 'LGG',
    'liège': 'LGG',
    'ostend': 'OST',
    'ostende': 'OST',
    'antwerp': 'ANR',
    'anvers': 'ANR',

    # Espagne
    'barcelona': 'BCN',
    'barcelone': 'BCN',
    'madrid': 'MAD',
    'palma': 'PMI',
    'mallorca': 'PMI',
    'ibiza': 'IBZ',
    'malaga': 'AGP',
    'valencia': 'VLC',
    'valence': 'VLC',
    'alicante': 'ALC',
    'seville': 'SVQ',
    'séville': 'SVQ',
    'bilbao': 'BIO',

    # Portugal
    'lisbon': 'LIS',
    'lisbonne': 'LIS',
    'porto': 'OPO',
    'faro': 'FAO',

    # Italie
    'rome': 'FCO',
    'roma': 'FCO',
    'venice': 'VCE',
    'venise': 'VCE',
    'naples': 'NAP',
    'milan': 'BGY',
    'milano': 'BGY',
    'florence': 'FLR',
    'firenze': 'FLR',
    'pisa': 'PSA',

    # France
    'paris': 'CDG',
    'nice': 'NCE',
    'marseille': 'MRS',
    'lyon': 'LYS',
    'toulouse': 'TLS',
    'bordeaux': 'BOD',
    'nantes': 'NTE',

    # Grèce
    'athens': 'ATH',
    'athènes': 'ATH',
    'heraklion': 'HER',
    'rhodes': 'RHO',
    'corfu': 'CFU',
    'corfou': 'CFU',
    'santorini': 'JTR',
    'mykonos': 'MYK',

    # Autres
    'prague': 'PRG',
    'budapest': 'BUD',
    'dublin': 'DUB',
    'berlin': 'BER',
    'amsterdam': 'AMS',
    'london': 'STN',
    'londres': 'STN',
}

def city_to_iata(city_name):
    """Convertit un nom de ville en code IATA"""
    if not city_name:
        return None

    # Nettoyer et normaliser
    clean_name = city_name.lower().strip()

    # Chercher dans le mapping
    return CITY_TO_IATA.get(clean_name)

# Base de données des aéroports avec thèmes
AIRPORTS = {
    'CRL': {
        'name': 'Brussels Charleroi',
        'country': 'Belgique',
        'coastal': False,
        'themes': ['city_trip']
    },
    'BRU': {
        'name': 'Brussels Airport',
        'country': 'Belgique',
        'coastal': False,
        'themes': ['city_trip']
    },
    'LGG': {
        'name': 'Liège Airport',
        'country': 'Belgique',
        'coastal': False,
        'themes': ['city_trip']
    },
    'BCN': {
        'name': 'Barcelona',
        'country': 'Espagne',
        'coastal': True,
        'themes': ['city_trip', 'party', 'beach', 'couple']
    },
    'MAD': {
        'name': 'Madrid',
        'country': 'Espagne',
        'coastal': False,
        'themes': ['city_trip', 'party', 'couple']
    },
    'PMI': {
        'name': 'Palma Mallorca',
        'country': 'Espagne',
        'coastal': True,
        'themes': ['beach', 'party', 'couple']
    },
    'IBZ': {
        'name': 'Ibiza',
        'country': 'Espagne',
        'coastal': True,
        'themes': ['party', 'beach', 'couple']
    },
    'AGP': {
        'name': 'Málaga',
        'country': 'Espagne',
        'coastal': True,
        'themes': ['beach', 'party', 'couple']
    },
    'VLC': {
        'name': 'Valencia',
        'country': 'Espagne',
        'coastal': True,
        'themes': ['beach', 'party', 'city_trip']
    },
    'ALC': {
        'name': 'Alicante',
        'country': 'Espagne',
        'coastal': True,
        'themes': ['beach', 'couple']
    },
    'SVQ': {
        'name': 'Seville',
        'country': 'Espagne',
        'coastal': False,
        'themes': ['city_trip', 'couple', 'party']
    },
    'LIS': {
        'name': 'Lisbon',
        'country': 'Portugal',
        'coastal': True,
        'themes': ['city_trip', 'couple', 'beach', 'party']
    },
    'OPO': {
        'name': 'Porto',
        'country': 'Portugal',
        'coastal': True,
        'themes': ['city_trip', 'couple', 'party']
    },
    'FAO': {
        'name': 'Faro',
        'country': 'Portugal',
        'coastal': True,
        'themes': ['beach', 'couple', 'party']
    },
    'FCO': {
        'name': 'Rome',
        'country': 'Italie',
        'coastal': True,
        'themes': ['city_trip', 'couple', 'beach']
    },
    'VCE': {
        'name': 'Venice',
        'country': 'Italie',
        'coastal': True,
        'themes': ['couple', 'city_trip', 'beach']
    },
    'NAP': {
        'name': 'Naples',
        'country': 'Italie',
        'coastal': True,
        'themes': ['beach', 'city_trip', 'couple']
    },
    'BGY': {
        'name': 'Milan Bergamo',
        'country': 'Italie',
        'coastal': False,
        'themes': ['city_trip', 'couple', 'mountain']
    },
    'NCE': {
        'name': 'Nice',
        'country': 'France',
        'coastal': True,
        'themes': ['beach', 'party', 'couple', 'city_trip']
    },
    'MRS': {
        'name': 'Marseille',
        'country': 'France',
        'coastal': True,
        'themes': ['beach', 'party', 'city_trip']
    },
    'CDG': {
        'name': 'Paris CDG',
        'country': 'France',
        'coastal': False,
        'themes': ['city_trip', 'couple', 'party']
    },
    'ATH': {
        'name': 'Athens',
        'country': 'Grèce',
        'coastal': False,
        'themes': ['city_trip', 'couple', 'beach']
    },
    'HER': {
        'name': 'Heraklion',
        'country': 'Grèce',
        'coastal': True,
        'themes': ['beach', 'party', 'nature']
    },
    'RHO': {
        'name': 'Rhodes',
        'country': 'Grèce',
        'coastal': True,
        'themes': ['beach', 'couple', 'party']
    },
    'CFU': {
        'name': 'Corfu',
        'country': 'Grèce',
        'coastal': True,
        'themes': ['beach', 'party', 'couple']
    },
    'JTR': {
        'name': 'Santorini',
        'country': 'Grèce',
        'coastal': True,
        'themes': ['couple', 'beach', 'city_trip']
    },
    'PRG': {
        'name': 'Prague',
        'country': 'République Tchèque',
        'coastal': False,
        'themes': ['city_trip', 'party', 'couple']
    },
    'BUD': {
        'name': 'Budapest',
        'country': 'Hongrie',
        'coastal': False,
        'themes': ['city_trip', 'party', 'couple']
    },
    'DUB': {
        'name': 'Dublin',
        'country': 'Irlande',
        'coastal': True,
        'themes': ['city_trip', 'party', 'couple']
    },
    'BER': {
        'name': 'Berlin',
        'country': 'Allemagne',
        'coastal': False,
        'themes': ['city_trip', 'party', 'couple']
    },
    'AMS': {
        'name': 'Amsterdam',
        'country': 'Pays-Bas',
        'coastal': False,
        'themes': ['city_trip', 'party', 'couple']
    }
}

# Types de voyage disponibles
THEMES = {
    'couple': 'Romantique',
    'party': 'Fête/Nightlife',
    'beach': 'Plage',
    'nature': 'Nature',
    'mountain': 'Montagne',
    'city_trip': 'City Trip'
}

def get_destinations_by_theme(theme):
    """Retourne les codes aéroports qui correspondent à un thème"""
    return [code for code, info in AIRPORTS.items() if theme in info['themes']]

def get_airport_info(code):
    """Retourne les infos d'un aéroport"""
    return AIRPORTS.get(code.upper())

def search_destinations(themes=None, coastal=None, countries=None):
    """
    Recherche des destinations selon des critères

    Args:
        themes: liste de thèmes (ex: ['beach', 'party'])
        coastal: True pour côtier, False pour non-côtier, None pour tous
        countries: liste de pays (ex: ['Espagne', 'Portugal'])

    Returns:
        Liste de codes aéroports
    """
    results = []

    for code, info in AIRPORTS.items():
        # Skip Belgian airports (departure airports)
        if info['country'] == 'Belgique':
            continue

        # Filtre par thème
        if themes:
            if not any(theme in info['themes'] for theme in themes):
                continue

        # Filtre côtier
        if coastal is not None:
            if info['coastal'] != coastal:
                continue

        # Filtre par pays
        if countries:
            if info['country'] not in countries:
                continue

        results.append(code)

    return results
