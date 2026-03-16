import axios from 'axios'

const isDevelopment = import.meta.env.DEV
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ||
  (isDevelopment ? '' : 'http://localhost:8000')

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000, // 60s - avoid infinite loading when backend is slow or unreachable
  headers: {
    'Content-Type': 'application/json',
  },
})

// FormData: don't set Content-Type so browser sends multipart/form-data; boundary=...
api.interceptors.request.use((config) => {
  if (config.data instanceof FormData) {
    delete config.headers['Content-Type']
  }
  return config
})

// Proxy both /agent and /npciswitch in dev (vite proxy)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response) {
      console.error('API Error:', error.response.data)
    } else if (error.request) {
      console.error('Network Error: Backend server may not be running')
    } else {
      console.error('Error:', error.message)
    }
    return Promise.reject(error)
  }
)

// ---- CR ID for Api Addition: "CHG-3digit" (001–999) ----
export const generateCrId3digit = () =>
  'CHG-' + String(Math.floor(1 + Math.random() * 999)).padStart(3, '0')

// ---- Backend-backed APIs (main.py) ----

/** POST /agent/artifact/upload - supports mapped artifact types (samples/specs/xsd/etc). */
export const uploadArtifact = async (changeId, artifactType, file, apiName) => {
  const formData = new FormData()
  formData.append('changeId', changeId)
  formData.append('artifactType', artifactType)
  formData.append('file', file)
  if (apiName) formData.append('apiName', apiName)
  return api.post('/agent/artifact/upload', formData)
}

/** POST /npciswitch/spec/generate - payload matches ChangeRequest (change_id, apiName, changeType, description, ...) */
export const specGenerate = async (payload) => {
  return api.post('/npciswitch/spec/generate', payload)
}

/** POST /npciswitch/spec/approve/{changeId} */
export const specApprove = async (changeId) => {
  return api.post(`/npciswitch/spec/approve/${changeId}`)
}

/** GET /npciswitch/dev/patch/{changeId} - returns { changeId, results: [{ type, file, diff }], ... } */
export const getDevPatch = async (changeId) => {
  return api.get(`/npciswitch/dev/patch/${changeId}`)
}

/** GET /npciswitch/change-requests - list all (for Developer dashboard) */
export const listChangeRequestsFromBackend = async () => {
  return api.get('/npciswitch/change-requests')
}

/** GET /npciswitch/change-requests/{changeId} */
export const getChangeRequestFromBackend = async (changeId) => {
  return api.get(`/npciswitch/change-requests/${changeId}`)
}

/** POST /npciswitch/change-requests - create/update (after Product submits for approval) */
export const saveChangeRequestToBackend = async (payload) => {
  return api.post('/npciswitch/change-requests', payload)
}

/** POST /npciswitch/change-requests/clear - clear all change requests (Change Management list) */
export const clearChangeRequestsFromBackend = async () => {
  return api.post('/npciswitch/change-requests/clear')
}

/** PATCH /npciswitch/change-requests/{changeId} - update status/review */
export const updateChangeRequestOnBackend = async (changeId, payload) => {
  return api.patch(`/npciswitch/change-requests/${changeId}`, payload)
}

// ---- Manifest / partners (Publish Changes tab) ----
/** GET /npciswitch/partners - returns { partnerId: { endpoint }, ... } */
export const listPartners = async () => {
  const res = await api.get('/npciswitch/partners')
  return res?.data ?? {}
}

/** POST /npciswitch/manifest/upload - changeId + file (FormData) */
export const uploadManifest = async (changeId, file) => {
  const formData = new FormData()
  formData.append('changeId', changeId)
  formData.append('file', file)
  return api.post('/npciswitch/manifest/upload', formData)
}

/** POST /npciswitch/manifest/broadcast/{changeId} */
export const broadcastManifest = async (changeId) => {
  return api.post(`/npciswitch/manifest/broadcast/${changeId}`)
}

/** POST /npciswitch/manifest/send/{changeId}/{partnerId} */
export const sendManifestToPartner = async (changeId, partnerId) => {
  return api.post(`/npciswitch/manifest/send/${changeId}/${partnerId}`)
}

/** GET /npciswitch/manifest/delivery-status - persisted { partnerId: { changeId: { statusCode, response } } } */
export const getManifestDeliveryStatus = async () => {
  const res = await api.get('/npciswitch/manifest/delivery-status')
  return res?.data ?? {}
}

/** POST /npciswitch/manifest/create/{changeId} - create partner manifest and store (after Developer approves) */
export const createAndStoreManifest = async (changeId) => {
  return api.post(`/npciswitch/manifest/create/${changeId}`)
}

/** GET /npciswitch/manifest/{changeId} - get stored manifest JSON (for viewing). Returns { manifest, signature } or { error: 'MANIFEST_NOT_FOUND' }. */
export const getManifest = async (changeId) => {
  const res = await api.get(`/npciswitch/manifest/${changeId}`)
  return res?.data
}

/** URL to download manifest file (GET /npciswitch/manifest/{changeId}/download) */
export const getManifestDownloadUrl = (changeId) => {
  const base = api.defaults.baseURL || ''
  return `${base}/npciswitch/manifest/${changeId}/download`
}

// ---- Orchestrator: party status (Payer, Payee, Banks) after receiving manifest ----
/** GET /orchestrator/status - returns { changeId: { agent: status, ... }, ... } */
export const getOrchestratorStatus = async () => {
  const res = await api.get('/orchestrator/status')
  return res?.data ?? {}
}

/** GET /orchestrator/change/{changeId} - returns { changeId, agents: { agent: status, ... } } */
export const getOrchestratorChangeStatus = async (changeId) => {
  const res = await api.get(`/orchestrator/change/${changeId}`)
  return res?.data ?? { changeId, agents: {} }
}

// ---- Deploy to javacoderepo (Field Addition only) ----
/** GET /npciswitch/deploy/eligibility/{changeId} - { eligible, reason, crStatus, changeType, agents } */
export const getDeployEligibility = async (changeId) => {
  const res = await api.get(`/npciswitch/deploy/eligibility/${changeId}`)
  return res?.data ?? { eligible: false, reason: 'Unknown' }
}

/** POST /npciswitch/deploy/{changeId} - deploy approved code to javacoderepo */
export const deployToJavacoderepo = async (changeId) => {
  return api.post(`/npciswitch/deploy/${changeId}`)
}

// ---- Local persistence (fallback / merge with backend) ----
const STORAGE_KEY = 'npci_change_requests'

export const getLocalChangeRequests = () => {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : []
  } catch {
    return []
  }
}

export const setLocalChangeRequest = (item) => {
  const list = getLocalChangeRequests()
  const idx = list.findIndex((r) => r.changeId === item.changeId)
  if (idx >= 0) {
    list[idx] = { ...list[idx], ...item }
  } else {
    list.unshift(item)
  }
  sessionStorage.setItem(STORAGE_KEY, JSON.stringify(list))
}

export const getLocalChangeRequest = (changeId) => {
  return getLocalChangeRequests().find((r) => r.changeId === changeId) || null
}

// ---- Unified changeRequestAPI for components (backend + local) ----

export const changeRequestAPI = {
  uploadArtifact,

  /** Create is local + upload + spec generate. Callers do: create local, upload samples, then specGenerate. */
  createChangeRequest: async (payload) => {
    const changeId = `CHG-${Date.now()}`
    setLocalChangeRequest({
      changeId,
      description: payload.description,
      changeType: payload.changeType,
      apiName: payload.apiName,
      currentStatus: 'Pending',
      receivedDate: new Date().toISOString(),
      updatedOn: new Date().toISOString(),
    })
    return { data: { changeId, ...payload } }
  },

  /** List: backend only (same source for Status Center and Developer dashboard). Falls back to local only if backend fails (e.g. server down). */
  getAllChangeRequests: async () => {
    try {
      const res = await listChangeRequestsFromBackend()
      const fromBackend = Array.isArray(res?.data?.data) ? res.data.data : []
      const sorted = fromBackend.slice().sort((a, b) => (b.updatedOn || b.receivedDate || '').localeCompare(a.updatedOn || a.receivedDate || ''))
      return { data: sorted }
    } catch {
      return { data: getLocalChangeRequests() }
    }
  },

  /** Clear all change requests (backend store + local sessionStorage). */
  clearAllChangeRequests: async () => {
    try {
      await clearChangeRequestsFromBackend()
    } catch (_) {}
    try {
      sessionStorage.setItem(STORAGE_KEY, '[]')
    } catch (_) {}
    return { data: [] }
  },

  getChangeRequestDetails: async (changeId) => {
    try {
      const res = await getChangeRequestFromBackend(changeId)
      if (res?.data?.data) return { data: res.data.data }
    } catch (_) {}
    const local = getLocalChangeRequest(changeId)
    return { data: local ?? null }
  },

  updateChangeRequestStatus: async (changeId, { currentStatus, reviewComments }) => {
    try {
      await updateChangeRequestOnBackend(changeId, { currentStatus, reviewComments })
    } catch (_) {}
    const item = getLocalChangeRequest(changeId)
    if (item) {
      setLocalChangeRequest({
        ...item,
        changeId,
        currentStatus: currentStatus ?? item.currentStatus,
        reviewComments: reviewComments ?? item.reviewComments,
        updatedOn: new Date().toISOString(),
      })
    }
    return { data: { changeId, currentStatus } }
  },

  /** Persist CR to backend so it appears on Developer dashboard */
  saveChangeRequestToBackend,

  // Backend spec/patch (used by flow)
  specGenerate,
  specApprove,
  getDevPatch,

  // Stubs so existing UI doesn’t break (no backend for these)
  analyzeChange: async () => ({ data: {} }),
  generatePatch: async () => ({ data: {} }),
  generateXsd: async () => ({ data: {} }),
  fetchXsdByApiName: async () => ({ data: {} }),
  applyXsdToJava: async () => ({ data: { success: false, files: [] } }),
  generateDto: async () => ({ data: { success: false } }),

  /** POST /agent/xsd/convert-sample-xml (multipart) -> { xsd } */
  convertSampleXmlToXsd: async (file) => {
    const form = new FormData()
    form.append('file', file)
    return api.post('/agent/xsd/convert-sample-xml', form)
  },
}

export default api
