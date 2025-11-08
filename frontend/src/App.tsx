import { BrowserRouter, Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import VolsPage from './pages/VolsPage'
import HotelsPage from './pages/HotelsPage'
import ActivitesPage from './pages/ActivitesPage'
import ChatSidebar from './components/ChatSidebar'
import './App.css'

function AppContent() {
  return (
    <>
      <ChatSidebar />
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/vols" element={<VolsPage />} />
        <Route path="/hotels" element={<HotelsPage />} />
        <Route path="/activites" element={<ActivitesPage />} />
      </Routes>
    </>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  )
}
