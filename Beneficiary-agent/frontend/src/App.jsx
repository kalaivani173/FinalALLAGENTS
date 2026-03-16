import { Routes, Route } from 'react-router-dom'
import ListPage from './pages/ListPage'
import ChangeDetailPage from './pages/ChangeDetailPage'

export default function App() {
  return (
    <div className="app-wrap theme-beneficiary">
      <header className="app-header">
        <span className="entity-badge">Beneficiary Bank</span>
        <h1>Beneficiary Bank AI Agent</h1>
        <p className="subtitle">Change requests from NPCI Switch – credit/CBS integration</p>
      </header>

      <main className="app-main">
        <Routes>
          <Route path="/" element={<ListPage />} />
          <Route path="/changes/:changeId" element={<ChangeDetailPage />} />
        </Routes>
      </main>
    </div>
  )
}
