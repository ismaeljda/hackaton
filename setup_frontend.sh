#!/usr/bin/env bash
set -e

APP_NAME="trip-agent-frontend"
echo "Création du projet $APP_NAME..."

# 1) Create Vite React TypeScript app
npm create vite@latest $APP_NAME -- --template react-ts
cd $APP_NAME

# 2) Install dependencies
echo "Installation des dépendances..."
npm install axios react-leaflet leaflet
npm install -D @types/leaflet

# 3) Overwrite default src files with demo-ready code
echo "Ecriture des fichiers source..."

# main.tsx
cat > src/main.tsx <<'TSX'
import React from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'
import './index.css'
import 'leaflet/dist/leaflet.css'

createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
)
TSX

# App.tsx
cat > src/App.tsx <<'TSX'
import React from 'react'
import ChatAgent from './components/ChatAgent'
import MapView from './components/MapView'
import './App.css'

export default function App() {
  return (
    <div className="app-root" style={{fontFamily: 'Inter, sans-serif', height: '100vh', display: 'grid', gridTemplateColumns: '420px 1fr', gap: 16, padding: 16}}>
      <div style={{background:'#fff', borderRadius:12, boxShadow:'0 6px 20px rgba(0,0,0,0.08)', overflow:'hidden', display:'flex', flexDirection:'column'}}>
        <div style={{padding:16, borderBottom:'1px solid #eee', fontWeight:700}}>Agent de voyage — démo</div>
        <div style={{flex:1, padding:12}}>
          <ChatAgent />
        </div>
      </div>
      <div style={{borderRadius:12, overflow:'hidden', boxShadow:'0 6px 20px rgba(0,0,0,0.06)'}}>
        <MapView />
      </div>
    </div>
  )
}
TSX

# components folder
mkdir -p src/components

# ChatAgent.tsx
cat > src/components/ChatAgent.tsx <<'TSX'
import React, { useState, useRef, useEffect } from 'react'
import axios from 'axios'

type AgentResponse = {
  text: string
  audioUrl?: string
  actions?: any[] // ex: [{type:'zoom', lat, lng, zoom}] or [{type:'hotels', hotels:[{lat,lng,name}]}]
}

export default function ChatAgent(){
  const [messages, setMessages] = useState<{from:'user'|'agent', text:string}[]>([])
  const [input, setInput] = useState('')
  const [listening, setListening] = useState(false)
  const audioRef = useRef<HTMLAudioElement|null>(null)

  // Web Speech API (speech-to-text) optional
  const recognitionRef = useRef<any>(null)
  useEffect(() => {
    // @ts-ignore
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if(SpeechRecognition){
      const rec = new SpeechRecognition()
      rec.lang = 'fr-FR'
      rec.interimResults = false
      rec.onresult = (e: any) => {
        const text = e.results[0][0].transcript
        setInput(text)
        setListening(false)
        rec.stop()
      }
      rec.onend = () => setListening(false)
      recognitionRef.current = rec
    }
  },[])

  async function sendMessage(text: string){
    if(!text) return
    setMessages(prev => [...prev, {from:'user', text}])
    setInput('')
    try{
      // POST to your backend Python agent endpoint
      const res = await axios.post<AgentResponse>('/api/converse', { message: text })
      const data = res.data
      setMessages(prev => [...prev, {from:'agent', text: data.text}])

      // play audio if provided
      if(data.audioUrl){
        if(audioRef.current) {
          audioRef.current.src = data.audioUrl + (data.audioUrl.includes('?') ? '&' : '?') + 't=' + Date.now()
          audioRef.current.play().catch(()=>{})
        }
      }

      // dispatch custom actions via window events (MapView listens)
      if(data.actions){
        window.dispatchEvent(new CustomEvent('agent:actions', { detail: data.actions }))
      }
    }catch(err){
      console.error(err)
      setMessages(prev => [...prev, {from:'agent', text: 'Erreur: impossible de contacter le backend.'}])
    }
  }

  function toggleListen(){
    if(!recognitionRef.current) return alert('Microphone non supporté dans ce navigateur demo.')
    if(listening){
      recognitionRef.current.stop()
      setListening(false)
    } else {
      setListening(true)
      recognitionRef.current.start()
    }
  }

  return (
    <div style={{display:'flex', flexDirection:'column', height:'100%'}}>
      <div style={{flex:1, overflow:'auto', padding:8}}>
        {messages.map((m, i) => (
          <div key={i} style={{marginBottom:8, display:'flex', justifyContent: m.from === 'user' ? 'flex-end' : 'flex-start'}}>
            <div style={{
              maxWidth: '80%',
              padding:10,
              borderRadius:10,
              background: m.from === 'user' ? '#0ea5a4' : '#f1f5f9',
              color: m.from === 'user' ? '#fff' : '#0f172a'
            }}>{m.text}</div>
          </div>
        ))}
      </div>

      <div style={{padding:8, borderTop:'1px solid #eee', display:'flex', gap:8, alignItems:'center'}}>
        <button onClick={toggleListen} style={{padding:8, borderRadius:8, border:'1px solid #ddd', background: listening ? '#fee2e2' : '#fff'}}>
          {listening ? '⏹ Stop' : '🎤 Micro'}
        </button>
        <input value={input} onChange={e=>setInput(e.target.value)} placeholder="Demande: ex. 'Prépare un voyage à Lisbonne pour 4 jours'" style={{flex:1, padding:10, borderRadius:8, border:'1px solid #ddd'}} onKeyDown={(e)=>{ if(e.key==='Enter') sendMessage(input) }}/>
        <button onClick={()=>sendMessage(input)} style={{padding:'10px 14px', borderRadius:8, background:'#06b6d4', color:'#fff', border:'none'}}>Envoyer</button>
      </div>

      <audio ref={audioRef} hidden controls />
    </div>
  )
}
TSX

# MapView.tsx
cat > src/components/MapView.tsx <<'TSX'
import React, { useEffect, useRef, useState } from 'react'
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet'
import L from 'leaflet'

delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
})

function MapActionsListener({ setMarkers }: { setMarkers: any }) {
  const map = useMap()
  useEffect(() => {
    function handler(e: any){
      const actions = e.detail as any[]
      actions.forEach(a=>{
        if(a.type === 'zoom' && a.lat && a.lng){
          map.setView([a.lat, a.lng], a.zoom || 12, { animate: true })
        } else if(a.type === 'marker' && a.lat && a.lng){
          setMarkers((m:any)=>[...m, {lat:a.lat, lng:a.lng, name: a.name || 'Point'}])
        } else if(a.type === 'hotels' && Array.isArray(a.hotels)){
          setMarkers((m:any)=>[...m, ...a.hotels.map((h:any)=>({lat:h.lat,lng:h.lng,name:h.name}))])
        }
      })
    }
    window.addEventListener('agent:actions', handler as EventListener)
    return ()=> window.removeEventListener('agent:actions', handler as EventListener)
  }, [map, setMarkers])
  return null
}

export default function MapView(){
  const [markers, setMarkers] = useState<{lat:number,lng:number,name:string}[]>([
    {lat:48.8566, lng:2.3522, name:'Paris (exemple)'}
  ])

  return (
    <MapContainer center={[48.8566,2.3522]} zoom={5} style={{height:'100%', minHeight: '100vh'}}>
      <MapActionsListener setMarkers={setMarkers} />
      <TileLayer
        attribution='&copy; OpenStreetMap contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      {markers.map((m,i)=>(
        <Marker key={i} position={[m.lat, m.lng]}>
          <Popup>
            <strong>{m.name}</strong>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  )
}
TSX

# index.css
cat > src/index.css <<'CSS'
/* simple neutral styles */
:root{
  --bg:#f8fafc;
}
html,body,#root{height:100%}
body{
  margin:0;
  background:var(--bg);
  font-family: Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial;
  -webkit-font-smoothing:antialiased;
}
CSS

# App.css
cat > src/App.css <<'CSS'
/* Optional small tweaks */
CSS

# README
cat > README.md <<'MD'
# trip-agent-frontend (démo)

Front React + TypeScript pour la démo "agent de voyage" (hackathon).

## Lancer
1. Installer deps : `npm install`
2. Démarrer : `npm run dev`

## Contrat backend attendu
Le frontend envoie `POST /api/converse` avec JSON `{ message: string }`.
Le backend doit répondre JSON `{ text: string, audioUrl?: string, actions?: any[] }`.
- `audioUrl` : URL publique pointant sur un audio (mp3) généré par ElevenLabs ou proxy.
- `actions` : liste d'actions pour le frontend, ex :
  - `{ type:'zoom', lat: 38.7223, lng: -9.1393, zoom: 12 }`
  - `{ type:'hotels', hotels: [{lat, lng, name}, ...] }`

**Important** : Ne mettez pas la clé ElevenLabs dans le frontend ; gérez les appels à ElevenLabs dans le backend Python.
MD

echo "Initialisation terminée."
echo "cd $APP_NAME && npm install && npm run dev"
