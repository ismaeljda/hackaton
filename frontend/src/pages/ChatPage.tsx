import { useState, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import MapView from '../components/MapView'
import ChatAgent from '../components/ChatAgent'

export default function ChatPage() {
  const navigate = useNavigate()
  const [isMinimized, setIsMinimized] = useState(false)
  const [isTransitioning, setIsTransitioning] = useState(false)

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
  }

  // Fonction pour détecter le type de service et la destination
  const detectServiceAndDestination = useCallback((message: string) => {
    const lowerMessage = message.toLowerCase()
    
    // Détection du type de service
    let serviceType: 'vols' | 'hotels' | 'activites' | null = null
    
    if (lowerMessage.includes('vol') || lowerMessage.includes('avion') || lowerMessage.includes('fly') || lowerMessage.includes('compagnie aérienne')) {
      serviceType = 'vols'
    } else if (lowerMessage.includes('hôtel') || lowerMessage.includes('hotel') || lowerMessage.includes('hébergement') || lowerMessage.includes('logement') || lowerMessage.includes('sejour') || lowerMessage.includes('séjour')) {
      serviceType = 'hotels'
    } else if (lowerMessage.includes('activité') || lowerMessage.includes('activite') || lowerMessage.includes('excursion') || lowerMessage.includes('visite') || lowerMessage.includes('expérience') || lowerMessage.includes('experience') || lowerMessage.includes('tour') || lowerMessage.includes('excursion')) {
      serviceType = 'activites'
    }
    
    // Détection de la destination
    const destinations = Object.keys(cityCoords)
    const foundDestination = destinations.find(dest => 
      lowerMessage.includes(dest) || 
      lowerMessage.includes(`à ${dest}`) || 
      lowerMessage.includes(`pour ${dest}`) ||
      lowerMessage.includes(`voyage ${dest}`) ||
      lowerMessage.includes(`partir ${dest}`) ||
      lowerMessage.includes(`aller ${dest}`) ||
      lowerMessage.includes(`destination ${dest}`)
    )
    
    return { serviceType, destination: foundDestination || null }
  }, [])

  // Fonction pour rediriger vers la page appropriée
  const redirectToServicePage = useCallback((serviceType: 'vols' | 'hotels' | 'activites', destination: string) => {
    setIsTransitioning(true)
    
    setTimeout(() => {
      navigate(`/${serviceType}?destination=${destination}`)
      setIsTransitioning(false)
    }, 800)
  }, [navigate])

  // Fonction pour déclencher la transition avec carte
  const triggerTransition = useCallback((destination?: string) => {
    if (isTransitioning) return
    
    if (isMinimized) return
    
    setIsTransitioning(true)
    
    setTimeout(() => {
      setIsMinimized(true)
      setIsTransitioning(false)
      
      const dest = destination?.toLowerCase() || 'paris'
      const coord = cityCoords[dest] || cityCoords['paris']
      
      window.dispatchEvent(new CustomEvent('agent:actions', {
        detail: [{
          type: 'zoom',
          lat: coord.lat,
          lng: coord.lng,
          zoom: 12
        }]
      }))
    }, 800)
  }, [isMinimized, isTransitioning])


  return (
    <div style={{
      fontFamily: 'Inter, sans-serif',
      height: '100vh',
      width: '100vw',
      position: 'relative',
      background: isMinimized ? '#f8fafc' : '#ffffff',
      overflow: isMinimized ? 'hidden' : 'auto',
      transition: 'background 0.8s ease',
    }}>
      {/* Carte - visible seulement quand minimisé */}
      {isMinimized && (
        <div style={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          opacity: isTransitioning ? 0 : 1,
          transition: 'opacity 0.8s ease',
          zIndex: 1
        }}>
          <MapView />
        </div>
      )}

      {/* Chat Agent */}
      <div
        className={isMinimized ? 'widget-minimized' : 'widget-fullscreen'}
        style={{
          zIndex: isMinimized ? 1000 : 9999,
          transition: 'all 0.8s cubic-bezier(0.4, 0, 0.2, 1)',
          opacity: isTransitioning ? 0.95 : 1,
          pointerEvents: 'auto',
          position: isMinimized ? 'fixed' : 'relative',
          bottom: isMinimized ? '24px' : 'auto',
          right: isMinimized ? '24px' : 'auto',
          width: isMinimized ? '400px' : '100%',
          height: isMinimized ? '600px' : '100vh',
          borderRadius: isMinimized ? '20px' : '0',
          boxShadow: isMinimized
            ? '0 25px 70px rgba(0,0,0,0.25), 0 0 0 1px rgba(0,0,0,0.05)'
            : 'none',
          overflow: 'hidden',
          background: '#fff'
        }}
      >
        <ChatAgent />
      </div>
      
      {/* Bouton pour agrandir le widget quand il est minimisé */}
      {isMinimized && (
        <button
          onClick={() => setIsMinimized(false)}
          style={{
            position: 'fixed',
            bottom: '640px',
            right: '24px',
            zIndex: 1001,
            width: '48px',
            height: '48px',
            borderRadius: '50%',
            background: '#0ea5a4',
            color: 'white',
            border: 'none',
            cursor: 'pointer',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '20px',
            boxShadow: '0 4px 12px rgba(14, 165, 164, 0.4)',
            transition: 'all 0.3s ease',
            animation: 'slideIn 0.5s ease'
          }}
          onMouseEnter={(e) => {
            e.currentTarget.style.transform = 'scale(1.1)'
            e.currentTarget.style.boxShadow = '0 6px 16px rgba(14, 165, 164, 0.5)'
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.transform = 'scale(1)'
            e.currentTarget.style.boxShadow = '0 4px 12px rgba(14, 165, 164, 0.4)'
          }}
          title="Agrandir le chat"
        >
          ↗
        </button>
      )}

      {/* Overlay de transition */}
      {isTransitioning && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: 'rgba(255, 255, 255, 0.98)',
          zIndex: 999,
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          fontSize: '28px',
          color: '#0ea5a4',
          fontWeight: 600,
          animation: 'fadeOut 0.8s ease forwards',
          backdropFilter: 'blur(10px)'
        }}>
          <div style={{
            animation: 'slideIn 0.5s ease',
            textAlign: 'center'
          }}>
            ✈️ Préparation de votre voyage...
          </div>
        </div>
      )}
    </div>
  )
}
