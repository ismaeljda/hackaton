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
