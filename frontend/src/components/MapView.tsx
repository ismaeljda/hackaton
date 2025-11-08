import { useEffect, useState } from 'react'
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
