import { useSearchParams, useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import axios from 'axios'
import DestinationMap from '../components/DestinationMap'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

export default function VolsPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const destination = searchParams.get('destination') || ''
  const [flights, setFlights] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!destination) {
      setLoading(false)
      return
    }

    setLoading(true)
    setError(null)

    axios.get(`${API_BASE_URL}/api/flights`, {
      params: {
        origin: 'CDG', // Paris par défaut
        destination: destination,
        min_stay: 4
      }
    })
    .then(response => {
      if (response.data.success) {
        // Formater les données pour correspondre au format attendu
        const formattedFlights = response.data.flights.map((flight: any, index: number) => ({
          id: index + 1,
          airline: flight.airline || 'Ryanair',
          departure: flight.departure || 'Paris CDG',
          arrival: flight.arrival || destination,
          departureTime: flight.departureTime || '08:30',
          arrivalTime: flight.arrivalTime || '10:45',
          departureDate: flight.departureDate || '',
          returnDate: flight.returnDate || '',
          price: flight.price || 0,
          duration: flight.duration || '2h15',
          stops: flight.stops || 0,
          bookingLink: flight.booking_link
        }))
        setFlights(formattedFlights)
      } else {
        setError(response.data.error || 'Erreur lors de la recherche')
      }
      setLoading(false)
    })
    .catch(err => {
      console.error('Erreur API vols:', err)
      setError('Impossible de charger les vols. Veuillez réessayer.')
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
          <button onClick={() => navigate('/vols')} style={{ background: 'none', border: 'none', color: '#0ea5a4', fontWeight: 600, cursor: 'pointer' }}>Vols</button>
          <button onClick={() => navigate('/hotels')} style={{ background: 'none', border: 'none', color: '#64748b', cursor: 'pointer' }}>Hôtels</button>
          <button onClick={() => navigate('/activites')} style={{ background: 'none', border: 'none', color: '#64748b', cursor: 'pointer' }}>Activités</button>
        </nav>
      </header>

      {/* Hero */}
      <div style={{
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        padding: '4rem 2rem',
        textAlign: 'center',
        color: 'white'
      }}>
        <h2 style={{ fontSize: '3rem', fontWeight: 800, marginBottom: '1rem' }}>
          ✈️ Recherche de Vols
        </h2>
        <p style={{ fontSize: '1.2rem', opacity: 0.9 }}>
          {destination ? `Trouvez les meilleurs vols pour ${destination.charAt(0).toUpperCase() + destination.slice(1)}` : 'Trouvez les meilleurs vols vers votre destination'}
        </p>
      </div>

      {/* Contenu */}
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '3rem 2rem' }}>
        {/* Carte avec zoom automatique */}
        {destination && (
          <div style={{ marginBottom: '3rem' }}>
            <DestinationMap destination={destination} height="400px" />
          </div>
        )}
        
        {loading ? (
          <div style={{ textAlign: 'center', padding: '4rem' }}>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>✈️</div>
            <p style={{ color: '#64748b', fontSize: '1.2rem' }}>Recherche de vols en cours...</p>
          </div>
        ) : error ? (
          <div style={{ textAlign: 'center', padding: '4rem' }}>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>⚠️</div>
            <p style={{ color: '#ef4444', fontSize: '1.2rem', marginBottom: '1rem' }}>{error}</p>
            <p style={{ color: '#64748b', fontSize: '1rem' }}>Les données mockées seront affichées en cas d'erreur API</p>
          </div>
        ) : flights.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '4rem' }}>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>✈️</div>
            <p style={{ color: '#64748b', fontSize: '1.2rem' }}>Aucun vol trouvé pour cette destination</p>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {flights.map((flight) => (
              <div
                key={flight.id}
                style={{
                  background: 'white',
                  borderRadius: '12px',
                  padding: '2rem',
                  boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  transition: 'all 0.3s ease'
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.15)'
                  e.currentTarget.style.transform = 'translateY(-2px)'
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.1)'
                  e.currentTarget.style.transform = 'translateY(0)'
                }}
              >
                <div style={{ flex: 1 }}>
                  <div style={{ display: 'flex', gap: '2rem', alignItems: 'center' }}>
                    <div>
                      <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#0f172a' }}>
                        {flight.departureTime}
                      </div>
                      <div style={{ fontSize: '0.9rem', color: '#64748b' }}>{flight.departure}</div>
                      {flight.departureDate && (
                        <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.25rem' }}>
                          {new Date(flight.departureDate).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })}
                        </div>
                      )}
                    </div>
                    <div style={{ flex: 1, textAlign: 'center' }}>
                      <div style={{ fontSize: '0.9rem', color: '#64748b', marginBottom: '0.5rem' }}>
                        {flight.duration} • {flight.stops === 0 ? 'Direct' : `${flight.stops} escale(s)`}
                      </div>
                      <div style={{ height: '2px', background: '#e2e8f0', position: 'relative' }}>
                        <div style={{ position: 'absolute', left: '50%', top: '-4px', transform: 'translateX(-50%)', background: '#0ea5a4', width: '8px', height: '8px', borderRadius: '50%' }} />
                      </div>
                      {flight.returnDate && flight.departureDate !== flight.returnDate && (
                        <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.5rem' }}>
                          Retour: {new Date(flight.returnDate).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })}
                        </div>
                      )}
                    </div>
                    <div>
                      <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#0f172a' }}>
                        {flight.arrivalTime}
                      </div>
                      <div style={{ fontSize: '0.9rem', color: '#64748b' }}>{flight.arrival}</div>
                      {flight.departureDate && (
                        <div style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '0.25rem' }}>
                          {new Date(flight.departureDate).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' })}
                        </div>
                      )}
                    </div>
                  </div>
                  <div style={{ marginTop: '1rem', color: '#64748b', fontSize: '0.9rem' }}>
                    {flight.airline}
                  </div>
                </div>
                <div style={{ textAlign: 'right', marginLeft: '2rem' }}>
                  <div style={{ fontSize: '2rem', fontWeight: 700, color: '#0ea5a4', marginBottom: '0.5rem' }}>
                    {flight.price}€
                  </div>
                  <button
                    onClick={() => {
                      if (flight.bookingLink) {
                        window.open(flight.bookingLink, '_blank')
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
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
