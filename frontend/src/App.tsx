import { Routes, Route } from 'react-router-dom'
import HomePage from './pages/HomePage'
import SubmitFormPage from './pages/SubmitFormPage'
import HistoryPage from './pages/HistoryPage'

function App() {
  return (
    <div className="container">
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/submit" element={<SubmitFormPage />} />
        <Route path="/history" element={<HistoryPage />} />
      </Routes>
    </div>
  )
}

export default App

