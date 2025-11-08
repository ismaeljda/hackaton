import { useEffect } from 'react'
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
import L from 'leaflet'
import markerIcon from 'leaflet/dist/images/marker-icon.png'
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png'
import markerShadow from 'leaflet/dist/images/marker-shadow.png'

delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow,
})

// Coordonnées des villes
const cityCoords: { [key: string]: { lat: number; lng: number } } = {
  'paris': { lat: 48.8566, lng: 2.3522 },
  'lisbonne': { lat: 38.7223, lng: -9.1393 },
  'barcelone': { lat: 41.3851, lng: 2.1734 },
  'rome': { lat: 41.9028, lng: 12.4964 },
  'madrid': { lat: 40.4168, lng: -3.7038 },
  'londres': { lat: 51.5074, lng: -0.1278 },
  'berlin': { lat: 52.5200, lng: 13.4050 },
  'amsterdam': { lat: 52.3676, lng: 4.9041 },
  'vienne': { lat: 48.2082, lng: 16.3738 },
  'prague': { lat: 50.0755, lng: 14.4378 },
  'budapest': { lat: 47.4979, lng: 19.0402 },
  'athènes': { lat: 37.9838, lng: 23.7275 },
  'istanbul': { lat: 41.0082, lng: 28.9784 },
  'dublin': { lat: 53.3498, lng: -6.2603 },
  'edimbourg': { lat: 55.9533, lng: -3.1883 },
  'stockholm': { lat: 59.3293, lng: 18.0686 },
  'copenhague': { lat: 55.6761, lng: 12.5683 },
  'oslo': { lat: 59.9139, lng: 10.7522 },
  'helsinki': { lat: 60.1699, lng: 24.9384 },
  'bruxelles': { lat: 50.8503, lng: 4.3517 },
  'zurich': { lat: 47.3769, lng: 8.5417 },
  'genève': { lat: 46.2044, lng: 6.1432 },
  'milan': { lat: 45.4642, lng: 9.1900 },
  'venise': { lat: 45.4408, lng: 12.3155 },
  'florence': { lat: 43.7696, lng: 11.2558 },
  'naples': { lat: 40.8518, lng: 14.2681 },
  'porto': { lat: 41.1579, lng: -8.6291 },
  'sevilla': { lat: 37.3891, lng: -5.9845 },
  'valencia': { lat: 39.4699, lng: -0.3763 },
  'nice': { lat: 43.7102, lng: 7.2620 },
  'marseille': { lat: 43.2965, lng: 5.3698 },
  'lyon': { lat: 45.7640, lng: 4.8357 },
  'bordeaux': { lat: 44.8378, lng: -0.5792 },
  'toulouse': { lat: 43.6047, lng: 1.4442 },
  'strasbourg': { lat: 48.5734, lng: 7.7521 },
  'nantes': { lat: 47.2184, lng: -1.5536 },
  'rennes': { lat: 48.1173, lng: -1.6778 },
  'lille': { lat: 50.6292, lng: 3.0573 },
  'reims': { lat: 49.2583, lng: 4.0317 },
  'bruges': { lat: 51.2093, lng: 3.2247 },
}

function MapZoom({ destination }: { destination: string }) {
  const map = useMap()
  
  useEffect(() => {
    if (destination) {
      const dest = destination.toLowerCase()
      const coord = cityCoords[dest]
      if (coord) {
        map.setView([coord.lat, coord.lng], 12, { animate: true, duration: 1.5 })
      }
    }
  }, [destination, map])
  
  return null
}

interface Hotel {
  id: number
  name: string
  location: string
  rating: number
  price: number
  image: string
  amenities: string[]
  description: string
  bookingUrl?: string
}

interface DestinationMapProps {
  destination?: string
  height?: string
  hotels?: Hotel[]
}

// Custom hotel icon - using URL encoding to avoid btoa emoji issues
const hotelIcon = new L.Icon({
  iconUrl: 'data:image/svg+xml;charset=utf-8,' + encodeURIComponent(`
    <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32">
      <circle cx="16" cy="16" r="14" fill="#0ea5a4" stroke="white" stroke-width="2"/>
      <path d="M10 18h12v6H10z" fill="white"/>
      <rect x="11" y="19" width="2" height="2" fill="#0ea5a4"/>
      <rect x="15" y="19" width="2" height="2" fill="#0ea5a4"/>
      <rect x="19" y="19" width="2" height="2" fill="#0ea5a4"/>
      <rect x="11" y="22" width="2" height="2" fill="#0ea5a4"/>
      <rect x="15" y="22" width="2" height="2" fill="#0ea5a4"/>
      <rect x="19" y="22" width="2" height="2" fill="#0ea5a4"/>
      <rect x="14" y="13" width="4" height="5" fill="white"/>
      <path d="M12 13l4-5 4 5z" fill="white"/>
    </svg>
  `),
  iconSize: [32, 32],
  iconAnchor: [16, 32],
  popupAnchor: [0, -32]
})

export default function DestinationMap({ destination = '', height = '400px', hotels = [] }: DestinationMapProps) {
  const dest = destination.toLowerCase()
  const coord = cityCoords[dest] || { lat: 48.8566, lng: 2.3522 }
  const cityName = destination ? destination.charAt(0).toUpperCase() + destination.slice(1) : 'Paris'

  return (
    <div style={{ height, borderRadius: '12px', overflow: 'hidden', boxShadow: '0 4px 12px rgba(0, 0, 0, 0.1)' }}>
      <MapContainer
        center={[coord.lat, coord.lng]}
        zoom={destination ? 13 : 5}
        style={{ height: '100%', width: '100%' }}
        scrollWheelZoom={true}
      >
        <MapZoom destination={destination} />
        <TileLayer
          attribution='&copy; OpenStreetMap contributors'
          url="https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png"
        />
        {destination && !hotels.length && (
          <Marker position={[coord.lat, coord.lng]}>
            <Popup>
              <strong>{cityName}</strong>
            </Popup>
          </Marker>
        )}
        {hotels.map((hotel, index) => {
          // Generate random position around city center (within ~1km radius)
          const offsetLat = (Math.random() - 0.5) * 0.015
          const offsetLng = (Math.random() - 0.5) * 0.015
          return (
            <Marker
              key={hotel.id || index}
              position={[coord.lat + offsetLat, coord.lng + offsetLng]}
              icon={hotelIcon}
            >
              <Popup>
                <div style={{ minWidth: '200px' }}>
                  <strong style={{ fontSize: '14px', color: '#0f172a' }}>{hotel.name}</strong>
                  <div style={{ marginTop: '8px', fontSize: '12px', color: '#64748b' }}>
                    ⭐ {hotel.rating} • {hotel.price}€/nuit
                  </div>
                  <div style={{ marginTop: '4px', fontSize: '11px', color: '#94a3b8', marginBottom: '8px' }}>
                    {hotel.description?.substring(0, 80)}...
                  </div>
                  {hotel.bookingUrl && (
                    <button
                      onClick={() => window.open(hotel.bookingUrl, '_blank')}
                      style={{
                        width: '100%',
                        padding: '8px 12px',
                        background: '#0ea5a4',
                        color: 'white',
                        border: 'none',
                        borderRadius: '6px',
                        cursor: 'pointer',
                        fontSize: '12px',
                        fontWeight: 600
                      }}
                    >
                      Réserver →
                    </button>
                  )}
                </div>
              </Popup>
            </Marker>
          )
        })}
      </MapContainer>
    </div>
  )
}
