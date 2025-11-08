import { useSearchParams, useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import axios from 'axios'
import DestinationMap from '../components/DestinationMap'

const API_BASE_URL = import.meta.env.VITE_API_URL || ''

export default function HotelsPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const destination = searchParams.get('destination') || ''
  const [hotels, setHotels] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!destination) {
      setLoading(false)
      return
    }

    setLoading(true)
    setError(null)

    axios.get(`${API_BASE_URL}/api/hotels`, {
      params: {
        destination: destination,
        adults: 2
      }
    })
    .then(response => {
      if (response.data.success) {
        const formattedHotels = response.data.hotels.map((hotel: any, index: number) => ({
          id: index + 1,
          name: hotel.name,
          location: destination,
          rating: hotel.rating || 4.0,
          price: hotel.price_numeric || parseInt(hotel.price?.replace('€', '').replace(/[^0-9]/g, '')) || 100,
          image: hotel.image || '🏨',
          amenities: hotel.amenities || ['WiFi', 'Petit-déjeuner'],
          description: hotel.description || 'Hôtel confortable',
          bookingUrl: hotel.booking_url
        }))
        setHotels(formattedHotels)
      } else {
        setError(response.data.error || 'Erreur lors de la recherche')
      }
      setLoading(false)
    })
    .catch(err => {
      console.error('Erreur API hôtels:', err)
      setError('Impossible de charger les hôtels. Veuillez réessayer.')
      setLoading(false)
    })
  }, [destination])

  return (
    <div style={{ minHeight: '100vh', background: '#f8fafc' }}>
      {/* Header */}
      <header style={{
        background: 'white',
        borderBottom: '1px solid #e2e8f0',
        padding: '1rem 2rem',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', cursor: 'pointer' }} onClick={() => navigate('/')}>
          <span style={{ fontSize: '24px' }}>✈️</span>
          <h1 style={{ margin: 0, fontSize: '20px', fontWeight: 700, color: '#0f172a' }}>
            VoyageAI
          </h1>
        </div>
        <nav style={{ display: 'flex', gap: '1.5rem', alignItems: 'center' }}>
          <button onClick={() => navigate('/vols')} style={{ background: 'none', border: 'none', color: '#64748b', cursor: 'pointer' }}>Vols</button>
          <button onClick={() => navigate('/hotels')} style={{ background: 'none', border: 'none', color: '#0ea5a4', fontWeight: 600, cursor: 'pointer' }}>Hôtels</button>
          <button onClick={() => navigate('/activites')} style={{ background: 'none', border: 'none', color: '#64748b', cursor: 'pointer' }}>Activités</button>
        </nav>
      </header>

      {/* Hero */}
      <div style={{
        background: 'linear-gradient(135deg, #0ea5a4 0%, #06b6d4 100%)',
        padding: '4rem 2rem',
        textAlign: 'center',
        color: 'white'
      }}>
        <h2 style={{ fontSize: '3rem', fontWeight: 800, marginBottom: '1rem' }}>
          🏨 Recherche d'Hôtels
        </h2>
        <p style={{ fontSize: '1.2rem', opacity: 0.9 }}>
          {destination ? `Trouvez les meilleurs hôtels à ${destination.charAt(0).toUpperCase() + destination.slice(1)}` : 'Trouvez les meilleurs hôtels pour votre séjour'}
        </p>
      </div>

      {/* Contenu */}
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '3rem 2rem' }}>
        {/* Carte avec zoom automatique et marqueurs d'hôtels */}
        {destination && (
          <div style={{ marginBottom: '3rem' }}>
            <DestinationMap destination={destination} height="500px" hotels={hotels} />
          </div>
        )}
        
        {loading ? (
          <div style={{ textAlign: 'center', padding: '4rem' }}>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🏨</div>
            <p style={{ color: '#64748b', fontSize: '1.2rem' }}>Recherche d'hôtels en cours...</p>
          </div>
        ) : error ? (
          <div style={{ textAlign: 'center', padding: '4rem' }}>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>❌</div>
            <p style={{ color: '#ef4444', fontSize: '1.2rem' }}>{error}</p>
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '2rem' }}>
            {hotels.map((hotel) => (
              <div
                key={hotel.id}
                style={{
                  background: 'white',
                  borderRadius: '16px',
                  overflow: 'hidden',
                  boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
                  transition: 'all 0.3s ease',
                  cursor: 'pointer'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.boxShadow = '0 8px 20px rgba(0, 0, 0, 0.15)'
                  e.currentTarget.style.transform = 'translateY(-4px)'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.1)'
                  e.currentTarget.style.transform = 'translateY(0)'
                }}
              >
                <div style={{
                  height: '200px',
                  background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '5rem',
                  overflow: 'hidden',
                  position: 'relative'
                }}>
                  {hotel.image && hotel.image.startsWith('http') ? (
                    <img
                      src={hotel.image}
                      alt={hotel.name}
                      style={{
                        width: '100%',
                        height: '100%',
                        objectFit: 'cover'
                      }}
                      onError={(e) => {
                        // Fallback to emoji if image fails to load
                        const target = e.target as HTMLElement;
                        target.style.display = 'none';
                        if (target.parentElement) {
                          target.parentElement.innerHTML = '🏨';
                          target.parentElement.style.fontSize = '5rem';
                        }
                      }}
                    />
                  ) : (
                    hotel.image || '🏨'
                  )}
                </div>
                <div style={{ padding: '1.5rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '0.5rem' }}>
                    <h3 style={{ fontSize: '1.5rem', fontWeight: 700, color: '#0f172a', margin: 0 }}>
                      {hotel.name}
                    </h3>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                      <span style={{ fontSize: '1.2rem' }}>⭐</span>
                      <span style={{ fontWeight: 600 }}>{hotel.rating}</span>
                    </div>
                  </div>
                  <p style={{ color: '#64748b', marginBottom: '1rem', fontSize: '0.9rem' }}>
                    {hotel.description}
                  </p>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', marginBottom: '1rem' }}>
                    {hotel.amenities.map((amenity: string, idx: number) => (
                      <span
                        key={idx}
                        style={{
                          padding: '0.25rem 0.75rem',
                          background: '#f1f5f9',
                          borderRadius: '12px',
                          fontSize: '0.8rem',
                          color: '#64748b'
                        }}
                      >
                        {amenity}
                      </span>
                    ))}
                  </div>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <div style={{ fontSize: '1.8rem', fontWeight: 700, color: '#0ea5a4' }}>
                        {hotel.price}€
                      </div>
                      <div style={{ fontSize: '0.8rem', color: '#64748b' }}>par nuit</div>
                    </div>
                    <button
                      onClick={() => {
                        if (hotel.bookingUrl) {
                          window.open(hotel.bookingUrl, '_blank')
                        } else {
                          navigate('/')
                        }
                      }}
                      style={{
                        padding: '0.75rem 1.5rem',
                        borderRadius: '8px',
                        background: '#0ea5a4',
                        color: 'white',
                        border: 'none',
                        cursor: 'pointer',
                        fontWeight: 600,
                        transition: 'all 0.3s ease'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.background = '#0d9488'
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.background = '#0ea5a4'
                      }}
                    >
                      Réserver
                    </button>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
