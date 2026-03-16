import { useState, useEffect } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table'
import { Button } from '@/components/ui/button'
import { RefreshCw, Search, FileCode, Upload } from 'lucide-react'
import { changeRequestAPI, specApprove, deployToJavacoderepo } from '@/lib/api'
import { useToast } from '@/contexts/ToastContext'
import CodeComparisonModal from './CodeComparisonModal'

const STATUS_COLORS = {
  'Pending': 'bg-yellow-100 text-yellow-800',
  'In Progress': 'bg-[#2F888A]/15 text-[#2F888A]',
  'Completed': 'bg-green-100 text-green-800',
  'Approved': 'bg-green-100 text-green-800',
  'Deployed': 'bg-emerald-100 text-emerald-800',
  'Rejected': 'bg-red-100 text-red-800',
  'Under Review': 'bg-purple-100 text-purple-800',
  'In Review': 'bg-purple-100 text-purple-800',
  'Waiting for Developer Approval': 'bg-amber-100 text-amber-800',
}

export default function DeveloperChangeRequestsTab({ isActive }) {
  const toast = useToast()
  const [changeRequests, setChangeRequests] = useState([])
  const [loading, setLoading] = useState(false)
  const [selectedChangeRequest, setSelectedChangeRequest] = useState(null)
  const [isModalOpen, setIsModalOpen] = useState(false)
  const [patchLoading, setPatchLoading] = useState(false)
  const [deployingChangeId, setDeployingChangeId] = useState(null)

  const fetchChangeRequests = async () => {
    setLoading(true)
    try {
      const response = await changeRequestAPI.getAllChangeRequests()
      setChangeRequests(Array.isArray(response.data) ? response.data : [])
    } catch (error) {
      console.error('Error fetching change requests:', error)
      setChangeRequests([])
    } finally {
      setLoading(false)
    }
  }

  // Format changeType from 'field-addition' to 'Field Addition'
  const formatChangeType = (v) => {
    if (!v) return ''
    return v.split('-').map(s => s.charAt(0).toUpperCase() + s.slice(1)).join(' ')
  }

  // Refetch when tab becomes active so list matches backend (same source as Status Center)
  useEffect(() => {
    if (isActive) fetchChangeRequests()
  }, [isActive])

  const handleChangeRequestClick = async (changeId) => {
    // Open modal immediately with loader so user isn't left waiting
    setSelectedChangeRequest({ changeId, files: [], patchError: null, loading: true })
    setIsModalOpen(true)

    try {
      const response = await changeRequestAPI.getChangeRequestDetails(changeId)
      const cr = response?.data ?? response
      if (cr) {
        let files = Array.isArray(cr.files) ? cr.files : []
        let patchError = null
        if (files.length === 0) {
          setPatchLoading(true)
          try {
            const patchRes = await changeRequestAPI.getDevPatch(changeId)
            const data = patchRes?.data ?? patchRes
            if (data?.error) {
              if (data.error === 'SPEC_NOT_APPROVED') {
                // CR may already be Approved in UI but spec was never approved in backend — try approving spec now
                const crApproved = (cr?.currentStatus || '').toLowerCase() === 'approved'
                if (crApproved) {
                  try {
                    await specApprove(changeId)
                    const retryRes = await changeRequestAPI.getDevPatch(changeId)
                    const retryData = retryRes?.data ?? retryRes
                    if (!retryData?.error && Array.isArray(retryData?.results)) {
                      files = retryData.results.map((r) => ({
                        fileName: r.file || 'file',
                        filePath: r.file,
                        oldCode: r.oldCode ?? '',
                        newCode: (r.newCode ?? r.diff) || '',
                        diff: r.diff || '',
                      }))
                      patchError = null
                    }
                  } catch (_) {
                    // leave patchError set below
                  }
                }
                if (files.length === 0) {
                  patchError = 'Code changes will appear after the spec is approved. Ask Product to click "Approve Spec" in the Change Requests tab.'
                }
              } else if (data.error === 'INVALID_CHANGE_ID') {
                patchError = 'This change request is not yet registered for patch generation.'
              } else {
                patchError = data.message || data.error || 'Patch could not be loaded.'
              }
            } else {
              const results = data?.results || []
              files = results.map((r) => ({
                fileName: r.file || 'file',
                filePath: r.file,
                oldCode: r.oldCode ?? '',
                newCode: (r.newCode ?? r.diff) || '',
                diff: r.diff || '',
              }))
              if (files.length === 0) {
                patchError = 'No code changes were generated. Ensure the change was submitted by Product (Create Change Request → Generate XSD → Submit) and the spec was approved. If the backend was restarted, Product may need to resubmit.'
              }
            }
          } catch (err) {
            const status = err?.response?.status
            const detail = err?.response?.data?.detail ?? err?.response?.data?.error ?? err?.message
            patchError = status === 404
              ? 'Patch endpoint not available. Restart the backend and try again.'
              : (detail ? `Failed to load code changes: ${detail}` : 'Failed to load code changes. Ensure the spec has been approved.')
          } finally {
            setPatchLoading(false)
          }
        }
        setSelectedChangeRequest({ ...cr, files, patchError, loading: false })
        return
      }

      const changeRequest = changeRequests.find((c) => c.changeId === changeId)
      if (changeRequest) {
        setSelectedChangeRequest({ ...changeRequest, loading: false })
        setIsModalOpen(true)
      } else {
        setSelectedChangeRequest({ changeId, files: [], patchError: 'Change request not found.', loading: false })
      }
    } catch (error) {
      console.error('Error fetching change request details:', error)
      setSelectedChangeRequest((prev) => (prev ? { ...prev, patchError: 'Failed to load change request.', loading: false } : { changeId, files: [], patchError: 'Failed to load change request.', loading: false }))
    }
  }

  const handleDeploy = async (changeId) => {
    if (!window.confirm('Deploy approved code to javacoderepo? Existing files will be renamed with _old extension.')) return
    setDeployingChangeId(changeId)
    try {
      const res = await deployToJavacoderepo(changeId)
      const data = res?.data ?? res
      if (data?.success) {
        toast.success('Deployed', `${(data.deployedFiles || []).length} file(s) deployed to javacoderepo.`)
        fetchChangeRequests()
      } else {
        const errMsg = (data?.errors || []).join(' ') || data?.detail || 'Deploy failed'
        toast.error('Deploy failed', errMsg)
      }
    } catch (err) {
      const msg = err?.response?.data?.detail ?? err?.response?.data?.error ?? err?.message ?? 'Deploy failed'
      toast.error('Deploy failed', String(msg))
    } finally {
      setDeployingChangeId(null)
    }
  }

  const formatDate = (dateString) => {
    if (!dateString) return 'N/A'
    try {
      const date = new Date(dateString)
      return date.toLocaleDateString('en-IN', { 
        year: 'numeric', 
        month: 'short', 
        day: 'numeric',
        timeZone: 'Asia/Kolkata'
      })
    } catch {
      return dateString
    }
  }

  return (
    <>
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle>Change Requests</CardTitle>
              <CardDescription>
                View and review change requests sent by Product team
              </CardDescription>
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={fetchChangeRequests}
              disabled={loading}
              title="Behind the scenes: GET /npciswitch/change-requests reloads the CR list."
            >
              <RefreshCw className={`mr-2 h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center py-12">
              <RefreshCw className="h-8 w-8 animate-spin text-gray-400" />
              <span className="ml-2 text-gray-600">Loading change requests...</span>
            </div>
          ) : changeRequests.length === 0 ? (
            <div className="text-center py-12 text-gray-500">
              <Search className="h-12 w-12 mx-auto mb-4 opacity-50" />
              <p>No change requests found</p>
            </div>
          ) : (
            <div className="border rounded-lg overflow-hidden">
              <Table>
                <TableHeader>
                  <TableRow>
                    <TableHead>Change Request ID</TableHead>
                    <TableHead>Description</TableHead>
                    <TableHead>Change Type</TableHead>
                    <TableHead>Received Date</TableHead>
                    <TableHead>Current Status</TableHead>
                    <TableHead>Updated On</TableHead>
                    <TableHead className="w-[120px]">Actions</TableHead>
                  </TableRow>
                </TableHeader>
                <TableBody>
                  {changeRequests.map((request, index) => (
                    <TableRow 
                      key={index}
                      className="cursor-pointer hover:bg-gray-50"
                      onClick={(e) => {
                        // Only trigger if clicking directly on the row, not on the link
                        if (e.target.tagName !== 'BUTTON' && e.target.tagName !== 'A') {
                          handleChangeRequestClick(request.changeId)
                        }
                      }}
                    >
                      <TableCell>
                        <button
                          onClick={(e) => {
                            e.stopPropagation()
                            handleChangeRequestClick(request.changeId)
                          }}
                          className="text-[#2F888A] hover:text-[#2F888A]/90 hover:underline font-medium cursor-pointer"
                        >
                          {request.changeId}
                        </button>
                      </TableCell>
                      <TableCell className="max-w-md">
                        <div className="truncate" title={request.description}>
                          {request.description}
                        </div>
                      </TableCell>
                      <TableCell>{formatChangeType(request.changeType)}</TableCell>
                      <TableCell>{formatDate(request.receivedDate)}</TableCell>
                      <TableCell>
                        <span
                          className={`px-2 py-1 rounded-full text-xs font-medium ${
                            STATUS_COLORS[request.currentStatus] || 'bg-gray-100 text-gray-800'
                          }`}
                        >
                          {request.currentStatus}
                        </span>
                      </TableCell>
                      <TableCell>{request.updatedOn || formatDate(request.receivedDate)}</TableCell>
                      <TableCell>
                        <div className="flex items-center gap-2 flex-wrap">
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={(e) => {
                              e.stopPropagation()
                              handleChangeRequestClick(request.changeId)
                            }}
                            disabled={patchLoading}
                            className="text-[#2F888A] hover:text-[#2F888A]/90 hover:bg-[#2F888A]/10"
                            title="Behind the scenes: GET change-requests/{id} → if no code, GET dev/patch/{id} generates Java DTO patch. Opens Code Comparison modal."
                          >
                            <FileCode className="h-4 w-4 mr-1.5 inline" />
                            {patchLoading ? 'Loading…' : 'View code'}
                          </Button>
                          {(request.changeType || '').toLowerCase() === 'field-addition' &&
                           (request.currentStatus || '').toLowerCase() === 'approved' && (
                            <Button
                              variant="default"
                              size="sm"
                              onClick={(e) => {
                                e.stopPropagation()
                                handleDeploy(request.changeId)
                              }}
                              disabled={deployingChangeId === request.changeId}
                              className="bg-emerald-600 hover:bg-emerald-700"
                              title="Behind the scenes: Deploys approved Java changes to javacoderepo; existing files renamed with _old extension."
                            >
                              <Upload className="h-4 w-4 mr-1.5 inline" />
                              {deployingChangeId === request.changeId ? 'Deploying…' : 'Deploy'}
                            </Button>
                          )}
                        </div>
                      </TableCell>
                    </TableRow>
                  ))}
                </TableBody>
              </Table>
            </div>
          )}
        </CardContent>
      </Card>

      <CodeComparisonModal
        open={isModalOpen}
        onOpenChange={setIsModalOpen}
        changeRequest={selectedChangeRequest}
        onStatusUpdated={fetchChangeRequests}
      />
    </>
  )
}
