import React, { useState, useRef, useEffect } from 'react'
import axios from 'axios'

type AgentResponse = {
  text: string
  audioUrl?: string
  actions?: any[]
}

export default function ChatAgent(){
  const [messages, setMessages] = useState<{from:'user'|'agent', text:string}[]>([])
  const [input, setInput] = useState('')
  const [listening, setListening] = useState(false)
  const audioRef = useRef<HTMLAudioElement|null>(null)

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
      const res = await axios.post<AgentResponse>('/api/converse', { message: text })
      const data = res.data
      setMessages(prev => [...prev, {from:'agent', text: data.text}])

      if(data.audioUrl && audioRef.current) {
        audioRef.current.src = data.audioUrl + (data.audioUrl.includes('?') ? '&' : '?') + 't=' + Date.now()
        audioRef.current.play().catch(()=>{})
      }

      if(data.actions){
        window.dispatchEvent(new CustomEvent('agent:actions', { detail: data.actions }))
      }
    }catch(err){
      console.error(err)
      setMessages(prev => [...prev, {from:'agent', text: 'Erreur: impossible de contacter le backend.'}])
    }
  }

  function toggleListen(){
    if(!recognitionRef.current) return alert('Microphone non supporté dans ce navigateur.')
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
        <input value={input} onChange={e=>setInput(e.target.value)} placeholder="Ex: 'Prépare un voyage à Lisbonne pour 4 jours'" style={{flex:1, padding:10, borderRadius:8, border:'1px solid #ddd'}} onKeyDown={(e)=>{ if(e.key==='Enter') sendMessage(input) }}/>
        <button onClick={()=>sendMessage(input)} style={{padding:'10px 14px', borderRadius:8, background:'#06b6d4', color:'#fff', border:'none'}}>Envoyer</button>
      </div>

      <audio ref={audioRef} hidden controls />
    </div>
  )
}
