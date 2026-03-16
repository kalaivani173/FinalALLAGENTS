import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { fetchApi, formatDate } from '../api'
import StateBadge from '../components/StateBadge'

export default function ListPage() {
  const [changes, setChanges] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  const loadList = useCallback(async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await fetchApi('/agent/status')
      setChanges(data.changes || [])
    } catch (err) {
      setError(err.message || 'Failed to load requests')
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    loadList()
  }, [loadList])

  const openDetail = (changeId) => {
    navigate(`/changes/${encodeURIComponent(changeId)}`)
  }

  return (
    <section className="section">
      <div className="section-header">
        <h2>Change Requests</h2>
        <button type="button" className="btn btn-secondary" onClick={loadList} title="Behind the scenes: GET /agent/status reloads the list of changes and their states.">
          Refresh
        </button>
      </div>
      {loading && <div className="loading">Loading…</div>}
      {error && <div className="error-msg">{error}</div>}
      {!loading && !error && changes.length === 0 && (
        <div className="empty-msg">
          No requests yet. Send a manifest to <code>POST /agent/manifest</code>.
        </div>
      )}
      {!loading && !error && changes.length > 0 && (
        <div className="table-wrap">
          <table className="table">
            <thead>
              <tr>
                <th>Change ID</th>
                <th>Status</th>
                <th>Updated</th>
                <th></th>
              </tr>
            </thead>
              <tbody>
                {changes.map((c) => (
                  <tr
                    key={c.changeId}
                    onClick={() => openDetail(c.changeId)}
                    role="button"
                    tabIndex={0}
                    onKeyDown={(e) => e.key === 'Enter' && openDetail(c.changeId)}
                    title="Click to open change detail"
                  >
                    <td><strong>{c.changeId}</strong></td>
                  <td><StateBadge state={c.state} /></td>
                  <td>{formatDate(c.updatedAt)}</td>
                  <td>
                    <button
                      type="button"
                      className="btn btn-primary btn-open"
                      onClick={(e) => {
                        e.stopPropagation()
                        openDetail(c.changeId)
                      }}
                      title="Behind the scenes: Navigates to detail page; loads state and artifacts via GET /agent/status/{changeId}."
                    >
                      Open →
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}
