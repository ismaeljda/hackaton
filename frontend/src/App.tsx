import { useEffect, useState, useRef, useCallback } from 'react'
import MapView from './components/MapView'
import './App.css'

export default function App() {
  const [isMinimized, setIsMinimized] = useState(false)
  const [isTransitioning, setIsTransitioning] = useState(false)
  const widgetRef = useRef<HTMLElement | null>(null)
  
  // Debug log
  useEffect(() => {
    console.log('🔍 App mount - isMinimized:', isMinimized)
  }, [isMinimized])

  // Fonction pour déclencher la transition
  const triggerTransition = useCallback((destination?: string) => {
    if (isMinimized || isTransitioning) return
    
    setIsTransitioning(true)
    
    // Attendre un peu pour une transition smooth
    setTimeout(() => {
      setIsMinimized(true)
      setIsTransitioning(false)
      
      // Dispatcher un événement pour la carte
      // En production, cela viendrait du backend via le widget ElevenLabs
      // Pour l'instant, on utilise des coordonnées par défaut
      const coords: { [key: string]: { lat: number; lng: number } } = {
        'paris': { lat: 48.8566, lng: 2.3522 },
        'lisbonne': { lat: 38.7223, lng: -9.1393 },
        'barcelone': { lat: 41.3851, lng: 2.1734 },
        'rome': { lat: 41.9028, lng: 12.4964 },
        'madrid': { lat: 40.4168, lng: -3.7038 },
        'londres': { lat: 51.5074, lng: -0.1278 },
      }
      
      const dest = destination?.toLowerCase() || 'paris'
      const coord = coords[dest] || coords['paris']
      
      window.dispatchEvent(new CustomEvent('agent:actions', {
        detail: [{
          type: 'zoom',
          lat: coord.lat,
          lng: coord.lng,
          zoom: 12
        }]
      }))
    }, 800) // Durée de la transition
  }, [isMinimized, isTransitioning])

  // Fonction pour détecter les destinations dans les messages
  const handleWidgetMessage = useCallback((event: any) => {
    const message = event.detail?.text || event.detail?.message || event.detail || ''
    const messageStr = typeof message === 'string' ? message : JSON.stringify(message)
    
    // Liste de villes/destinations communes (à étendre)
    const destinations = [
      'paris', 'lisbonne', 'barcelone', 'rome', 'madrid', 'londres', 'berlin',
      'amsterdam', 'vienne', 'prague', 'budapest', 'athènes', 'istanbul',
      'dublin', 'edimbourg', 'stockholm', 'copenhague', 'oslo', 'helsinki',
      'bruxelles', 'zurich', 'genève', 'milan', 'venise', 'florence', 'naples',
      'porto', 'sevilla', 'valencia', 'nice', 'marseille', 'lyon', 'bordeaux',
      'toulouse', 'strasbourg', 'nantes', 'rennes', 'lille', 'reims'
    ]
    
    const lowerMessage = messageStr.toLowerCase()
    const foundDestination = destinations.find(dest => 
      lowerMessage.includes(dest) || 
      lowerMessage.includes(`à ${dest}`) || 
      lowerMessage.includes(`pour ${dest}`) ||
      lowerMessage.includes(`voyage ${dest}`) ||
      lowerMessage.includes(`partir ${dest}`)
    )
    
    if (foundDestination) {
      triggerTransition(foundDestination)
    }
  }, [triggerTransition])

  useEffect(() => {
    // Attendre que le widget soit chargé
    const checkWidget = setInterval(() => {
      const widget = document.querySelector('elevenlabs-convai') as HTMLElement
      if (widget) {
        widgetRef.current = widget
        clearInterval(checkWidget)
        
        console.log('✅ Widget ElevenLabs trouvé, forçage du style...')
        
        // FORCER le style du widget ET son parent de manière persistante
        const forceFullscreen = () => {
          const widgetWrapper = widget.parentElement as HTMLElement
          if (widgetWrapper && !isMinimized) {
            widgetWrapper.style.cssText = `
              position: fixed !important;
              top: 0 !important;
              left: 0 !important;
              right: 0 !important;
              bottom: 0 !important;
              width: 100vw !important;
              height: 100vh !important;
              max-width: 100vw !important;
              max-height: 100vh !important;
              z-index: 9999 !important;
              margin: 0 !important;
              padding: 0 !important;
            `
          }
          
          // Forcer aussi le widget lui-même
          widget.style.cssText = `
            width: 100% !important;
            height: 100% !important;
            position: relative !important;
          `
        }
        
        console.log('🎯 Forçage plein écran sur wrapper')
        forceFullscreen()
        
        // Surveiller les changements et reforcer le style
        const styleObserver = new MutationObserver(() => {
          if (!isMinimized) {
            forceFullscreen()
          }
        })
        
        styleObserver.observe(widget, { 
          attributes: true, 
          attributeFilter: ['style'] 
        })
        
        if (widget.parentElement) {
          styleObserver.observe(widget.parentElement, { 
            attributes: true, 
            attributeFilter: ['style'] 
          })
        }
        
        // Forcer toutes les 100ms pendant 3 secondes (au cas où le widget se charge progressivement)
        let forceCount = 0
        const forceInterval = setInterval(() => {
          forceFullscreen()
          forceCount++
          if (forceCount > 30) {
            clearInterval(forceInterval)
            console.log('✅ Forçage terminé après 3 secondes')
          }
        }, 100)
        
        // Écouter les événements du widget ElevenLabs
        // Le widget peut émettre différents types d'événements
        const events = ['message', 'conversation-update', 'agent-response', 'user-message']
        events.forEach(eventType => {
          widget.addEventListener(eventType, handleWidgetMessage)
        })
        
        // Écouter aussi les mutations du DOM pour détecter les nouveaux messages
        const observer = new MutationObserver((mutations) => {
          mutations.forEach((mutation) => {
            mutation.addedNodes.forEach((node) => {
              if (node.nodeType === Node.ELEMENT_NODE) {
                const element = node as HTMLElement
                const text = element.textContent || element.innerText || ''
                if (text.length > 10) { // Ignorer les petits textes
                  handleWidgetMessage({ detail: text })
                }
              }
            })
          })
        })
        
        observer.observe(widget, {
          childList: true,
          subtree: true,
          characterData: true
        })
        
        // Écouter aussi les clics sur le widget pour détecter les interactions
        widget.addEventListener('click', (e) => {
          // Si minimisé et qu'on clique en dehors du widget, on peut le remettre en grand
          if (isMinimized && e.target === widget) {
            setIsMinimized(false)
          }
        })
      }
    }, 100)

    return () => {
      clearInterval(checkWidget)
      if (widgetRef.current) {
        const events = ['message', 'conversation-update', 'agent-response', 'user-message']
        events.forEach(eventType => {
          widgetRef.current?.removeEventListener(eventType, handleWidgetMessage)
        })
      }
    }
  }, [isMinimized, handleWidgetMessage])
  
  // Bouton de test pour déclencher la transition manuellement (à retirer en production)
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      if (e.key === 't' && e.ctrlKey && !isMinimized) {
        triggerTransition('paris')
      }
    }
    window.addEventListener('keydown', handleKeyPress)
    return () => window.removeEventListener('keydown', handleKeyPress)
  }, [isMinimized, triggerTransition])

  return (
    <div style={{
      fontFamily: 'Inter, sans-serif',
      height: '100vh',
      width: '100vw',
      position: 'relative',
      background: isMinimized ? '#f8fafc' : '#ffffff',
      overflow: 'hidden',
      transition: 'background 0.8s ease',
      display: isMinimized ? 'block' : 'flex',
      alignItems: 'center',
      justifyContent: 'center'
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

      {/* Widget ElevenLabs avec transition */}
      <div
        className={isMinimized ? 'widget-minimized' : 'widget-fullscreen'}
        style={{
          position: isMinimized ? 'fixed' : 'fixed',
          top: isMinimized ? 'auto' : '0',
          left: isMinimized ? 'auto' : '0',
          right: isMinimized ? '24px' : '0',
          bottom: isMinimized ? '24px' : '0',
          transform: isMinimized ? 'translate(0, 0)' : 'none',
          width: isMinimized ? '420px' : '100vw',
          height: isMinimized ? '600px' : '100vh',
          maxWidth: isMinimized ? '420px' : 'none',
          maxHeight: isMinimized ? '85vh' : 'none',
          zIndex: isMinimized ? 1000 : 9999,
          transition: 'all 0.8s cubic-bezier(0.4, 0, 0.2, 1)',
          opacity: isTransitioning ? 0.95 : 1,
          pointerEvents: 'auto',
          willChange: 'transform, width, height'
        }}
      >
        <elevenlabs-convai 
          agent-id="agent_4401k9hg1vs8efb9nr6wp6mrjf1r"
          style={{
            width: '100%',
            height: '100%',
            borderRadius: isMinimized ? '20px' : '0',
            boxShadow: isMinimized 
              ? '0 25px 70px rgba(0,0,0,0.25), 0 0 0 1px rgba(0,0,0,0.05)' 
              : 'none',
            overflow: 'hidden',
            transition: 'border-radius 0.8s cubic-bezier(0.4, 0, 0.2, 1), box-shadow 0.8s cubic-bezier(0.4, 0, 0.2, 1)'
          }}
        />
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
