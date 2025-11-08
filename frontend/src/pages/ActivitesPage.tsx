import { useSearchParams, useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import axios from 'axios'
import DestinationMap from '../components/DestinationMap'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:5000'

export default function ActivitesPage() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const destination = searchParams.get('destination') || ''
  const [activities, setActivities] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!destination) {
      setLoading(false)
      return
    }

    setLoading(true)
    setError(null)

    axios.get(`${API_BASE_URL}/api/activities`, {
      params: {
        destination: destination
      }
    })
    .then(response => {
      if (response.data.success) {
        const formattedActivities = response.data.activities.map((activity: any, index: number) => ({
          id: index + 1,
          name: activity.name,
          category: activity.category,
          price: activity.price,
          duration: activity.duration,
          image: activity.image || '🎫',
          description: activity.description,
          rating: activity.rating || 4.5
        }))
        setActivities(formattedActivities)
      } else {
        setError(response.data.error || 'Erreur lors de la recherche')
      }
      setLoading(false)
    })
    .catch(err => {
      console.error('Erreur API activités:', err)
      setError('Impossible de charger les activités. Veuillez réessayer.')
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
          <button onClick={() => navigate('/hotels')} style={{ background: 'none', border: 'none', color: '#64748b', cursor: 'pointer' }}>Hôtels</button>
          <button onClick={() => navigate('/activites')} style={{ background: 'none', border: 'none', color: '#0ea5a4', fontWeight: 600, cursor: 'pointer' }}>Activités</button>
        </nav>
      </header>

      {/* Hero */}
      <div style={{
        background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
        padding: '4rem 2rem',
        textAlign: 'center',
        color: 'white'
      }}>
        <h2 style={{ fontSize: '3rem', fontWeight: 800, marginBottom: '1rem' }}>
          🎫 Activités & Expériences
        </h2>
        <p style={{ fontSize: '1.2rem', opacity: 0.9 }}>
          {destination ? `Découvrez les meilleures activités à ${destination.charAt(0).toUpperCase() + destination.slice(1)}` : 'Découvrez des expériences inoubliables'}
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
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🎫</div>
            <p style={{ color: '#64748b', fontSize: '1.2rem' }}>Recherche d'activités en cours...</p>
          </div>
        ) : error ? (
          <div style={{ textAlign: 'center', padding: '4rem' }}>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>⚠️</div>
            <p style={{ color: '#ef4444', fontSize: '1.2rem' }}>{error}</p>
          </div>
        ) : activities.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '4rem' }}>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🎫</div>
            <p style={{ color: '#64748b', fontSize: '1.2rem' }}>Aucune activité trouvée pour cette destination</p>
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '2rem' }}>
            {activities.map((activity) => (
              <div
                key={activity.id}
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
                  height: '180px',
                  background: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '4rem'
                }}>
                  {activity.image}
                </div>
                <div style={{ padding: '1.5rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '0.5rem' }}>
                    <span style={{
                      padding: '0.25rem 0.75rem',
                      background: '#fef3c7',
                      borderRadius: '12px',
                      fontSize: '0.75rem',
                      color: '#92400e',
                      fontWeight: 600
                    }}>
                      {activity.category}
                    </span>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}>
                      <span style={{ fontSize: '1rem' }}>⭐</span>
                      <span style={{ fontWeight: 600, fontSize: '0.9rem' }}>{activity.rating}</span>
                    </div>
                  </div>
                  <h3 style={{ fontSize: '1.3rem', fontWeight: 700, color: '#0f172a', marginBottom: '0.5rem' }}>
                    {activity.name}
                  </h3>
                  <p style={{ color: '#64748b', marginBottom: '1rem', fontSize: '0.9rem', lineHeight: 1.5 }}>
                    {activity.description}
                  </p>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                    <div>
                      <div style={{ fontSize: '1.5rem', fontWeight: 700, color: '#f59e0b' }}>
                        {activity.price}€
                      </div>
                      <div style={{ fontSize: '0.8rem', color: '#64748b' }}>{activity.duration}</div>
                    </div>
                    <button
                      onClick={() => navigate('/')}
                      style={{
                        padding: '0.75rem 1.5rem',
                        borderRadius: '8px',
                        background: '#f59e0b',
                        color: 'white',
                        border: 'none',
                        cursor: 'pointer',
                        fontWeight: 600,
                        transition: 'all 0.3s ease'
                      }}
                      onMouseEnter={(e) => {
                        e.currentTarget.style.background = '#d97706'
                      }}
                      onMouseLeave={(e) => {
                        e.currentTarget.style.background = '#f59e0b'
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
