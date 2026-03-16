import { useState, useEffect, useCallback } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { fetchApi, formatDate } from '../api'
import StateBadge from '../components/StateBadge'
import DiffView from '../components/DiffView'

export default function ChangeDetailPage() {
  const { changeId } = useParams()
  const navigate = useNavigate()
  const [detail, setDetail] = useState(null)
  const [detailLoading, setDetailLoading] = useState(true)
  const [detailError, setDetailError] = useState(null)
  const [activeTab, setActiveTab] = useState('manifest')
  const [deploying, setDeploying] = useState(false)
  const [generating, setGenerating] = useState(false)
  const [approving, setApproving] = useState(false)
  const [runningTests, setRunningTests] = useState(false)
  const [generatingTests, setGeneratingTests] = useState(false)

  const loadDetail = useCallback(async () => {
    if (!changeId) return
    setDetailLoading(true)
    setDetailError(null)
    try {
      const data = await fetchApi(`/agent/status/${encodeURIComponent(changeId)}`)
      setDetail(data)
    } catch (err) {
      setDetailError(err.message || 'Failed to load request')
    } finally {
      setDetailLoading(false)
    }
  }, [changeId])

  useEffect(() => {
    loadDetail()
  }, [loadDetail])

  const goBack = () => {
    navigate('/')
  }

  const generate = useCallback(async () => {
    if (!changeId) return
    setGenerating(true)
    try {
      await fetchApi(`/agent/status/${encodeURIComponent(changeId)}/generate`, {
        method: 'POST',
      })
      await loadDetail()
      setActiveTab('diff')
    } catch (err) {
      alert(err.message || 'Generate failed')
    } finally {
      setGenerating(false)
    }
  }, [changeId, loadDetail])

  const approve = useCallback(async () => {
    if (!changeId) return
    setApproving(true)
    try {
      const data = await fetchApi(`/agent/status/${encodeURIComponent(changeId)}/approve`, {
        method: 'POST',
      })
      setDetail((d) => (d ? { ...d, state: data.state } : null))
    } catch (err) {
      alert(err.message || 'Approve failed')
    } finally {
      setApproving(false)
    }
  }, [changeId])

  const deploy = useCallback(async () => {
    if (!changeId) return
    setDeploying(true)
    try {
      const data = await fetchApi(`/agent/status/${encodeURIComponent(changeId)}/deploy`, {
        method: 'POST',
      })
      setDetail((d) => (d ? { ...d, state: data.state } : null))
    } catch (err) {
      alert(err.message || 'Deploy failed')
    } finally {
      setDeploying(false)
    }
  }, [changeId])

  const generateTests = useCallback(async () => {
    if (!changeId) return
    setGeneratingTests(true)
    try {
      const data = await fetchApi(`/agent/status/${encodeURIComponent(changeId)}/generate-tests`, {
        method: 'POST',
      })
      setDetail((d) => (d ? { ...d, state: data.state } : null))
      await loadDetail()
      setActiveTab('tests')
    } catch (err) {
      alert(err.message || 'Generate tests failed')
    } finally {
      setGeneratingTests(false)
    }
  }, [changeId, loadDetail])

  const testNow = useCallback(async () => {
    if (!changeId) return
    setRunningTests(true)
    try {
      const data = await fetchApi(`/agent/status/${encodeURIComponent(changeId)}/run-tests`, {
        method: 'POST',
      })
      setDetail((d) => (d ? { ...d, state: data.state } : null))
    } catch (err) {
      alert(err.message || 'Mark as tested failed')
    } finally {
      setRunningTests(false)
    }
  }, [changeId])

  const testEndToEnd = useCallback(async () => {
    // Single-click flow: generate tests, run tests, then return to list
    await generateTests()
    await testNow()
    goBack()
  }, [generateTests, testNow])

  const manifestJson = detail?.artifacts?.manifest
    ? JSON.stringify(detail.artifacts.manifest, null, 2)
    : 'No manifest stored for this request.'

  const patchContent = detail?.artifacts?.gitPatch ?? ''
  const artifactsJson = detail?.artifacts
    ? JSON.stringify(
        {
          gitPatch: detail.artifacts.gitPatch,
          xsd: detail.artifacts.xsd,
          tests: detail.artifacts.tests,
        },
        null,
        2
      )
    : 'No artifacts.'

  return (
    <section className="section detail-page">
      <div className="section-header detail-header">
        <button
          type="button"
          className="btn btn-back"
          onClick={goBack}
          aria-label="Back to list"
        >
          ← Back to list
        </button>
        <h2>Change Request: {changeId}</h2>
      </div>

      {detailLoading && <div className="loading">Loading…</div>}
      {detailError && <div className="error-msg">{detailError}</div>}

      {!detailLoading && !detailError && detail && (
        <>
          <div className="detail-meta">
            <p><strong>Change ID:</strong> {detail.changeId}</p>
            <p><strong>Status:</strong> <StateBadge state={detail.state} /></p>
            <p><strong>Updated:</strong> {formatDate(detail.updatedAt)}</p>
          </div>

          <div className="detail-actions">
            {(detail.state === 'RECEIVED' || detail.state === 'ACCEPTED') && !detail.artifacts?.gitPatch && (
              <button
                type="button"
                className="btn btn-primary"
                onClick={generate}
                disabled={generating}
              >
                {generating ? 'Generating…' : 'Generate'}
              </button>
            )}
            {['RECEIVED', 'ACCEPTED', 'TESTS_READY'].includes(detail.state) && detail.artifacts?.gitPatch && (
              <button
                type="button"
                className="btn btn-primary"
                onClick={testEndToEnd}
                disabled={generatingTests || runningTests}
              >
                {generatingTests || runningTests ? 'Running tests…' : 'Test & Mark Tested'}
              </button>
            )}
            {detail.state === 'TESTED' && detail.artifacts?.gitPatch && (
              <button
                type="button"
                className="btn btn-primary"
                onClick={approve}
                disabled={approving}
              >
                {approving ? 'Approving…' : 'Approve'}
              </button>
            )}
            {(detail.state === 'READY_FOR_DEPLOYMENT' || detail.state === 'APPLIED') && (
              <button
                type="button"
                className="btn btn-secondary"
                onClick={deploy}
                disabled={detail.state === 'DEPLOYED' || deploying}
              >
                {deploying ? 'Deploying…' : 'Deploy'}
              </button>
            )}
          </div>

          <div className="detail-tabs">
            <button
              type="button"
              className={`tab-btn ${activeTab === 'manifest' ? 'active' : ''}`}
              onClick={() => setActiveTab('manifest')}
            >
              Manifest
            </button>
            <button
              type="button"
              className={`tab-btn ${activeTab === 'diff' ? 'active' : ''}`}
              onClick={() => setActiveTab('diff')}
            >
              Diff
            </button>
            <button
              type="button"
              className={`tab-btn ${activeTab === 'tests' ? 'active' : ''}`}
              onClick={() => setActiveTab('tests')}
            >
              Tests
            </button>
            <button
              type="button"
              className={`tab-btn ${activeTab === 'artifacts' ? 'active' : ''}`}
              onClick={() => setActiveTab('artifacts')}
            >
              Artifacts
            </button>
          </div>

          <div className={`tab-panel ${activeTab === 'manifest' ? 'active' : ''}`}>
            <pre className="code-block">{manifestJson}</pre>
          </div>
          <div className={`tab-panel ${activeTab === 'diff' ? 'active' : ''}`}>
            <DiffView patchContent={patchContent} />
          </div>
          <div className={`tab-panel ${activeTab === 'tests' ? 'active' : ''}`}>
            <pre className="code-block test-output">
              {detail?.artifacts?.tests != null && String(detail.artifacts.tests).trim()
                ? detail.artifacts.tests
                : 'No test output yet. Click Test to generate unit tests.'}
            </pre>
          </div>
          <div className={`tab-panel ${activeTab === 'artifacts' ? 'active' : ''}`}>
            <pre className="code-block">{artifactsJson}</pre>
          </div>
        </>
      )}
    </section>
  )
}
