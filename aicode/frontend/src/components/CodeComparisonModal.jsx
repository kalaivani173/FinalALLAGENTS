import { useState, useEffect } from 'react'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { FileCode, CheckCircle2, XCircle, RefreshCw, FileText, ChevronRight, Download, Loader2 } from 'lucide-react'
import { changeRequestAPI, createAndStoreManifest, getManifestDownloadUrl, specApprove } from '@/lib/api'
import ReactDiffViewer from 'react-diff-viewer-continued'
import { useToast } from '@/contexts/ToastContext'

// Normalize file: support { oldCode, newCode }, { previousCode, currentCode }, and backend { diff, file }
function normalizeFile(f) {
  if (!f) return { oldCode: '', newCode: '', fileName: '', diff: '' }
  const diff = f.diff ?? ''
  const newCode = f.newCode ?? f.currentCode ?? diff
  return {
    ...f,
    oldCode: f.oldCode ?? f.previousCode ?? '',
    newCode,
    diff,
    fileName: f.fileName ?? f.filePath?.split(/[/\\]/).pop() ?? (f.file ?? 'file'),
  }
}

export default function CodeComparisonModal({ open, onOpenChange, changeRequest, onStatusUpdated, showApproveReject = true }) {
  const [selectedIndex, setSelectedIndex] = useState(0)
  const [comments, setComments] = useState('')
  const [submitting, setSubmitting] = useState(false)
  const toast = useToast()

  const rawFiles = changeRequest?.files || []
  const files = rawFiles.map(normalizeFile)
  const currentStatus = String(changeRequest?.currentStatus || '').trim()
  const isFinal = currentStatus === 'Approved' || currentStatus === 'Rejected' || currentStatus === 'Deployed'
  const canApproveReject = Boolean(showApproveReject) && !isFinal

  useEffect(() => {
    if (open && changeRequest) {
      setSelectedIndex(0)
      setComments('')
    }
  }, [open, changeRequest?.changeId])

  const selected = files[selectedIndex]

  const handleApprove = async () => {
    setSubmitting(true)
    try {
      // Approve the spec in the backend so getDevPatch returns code changes (CHANGE_STORE.approvalStatus = APPROVED)
      try {
        await specApprove(changeRequest.changeId)
      } catch (specErr) {
        console.warn('Spec approve (for patch generation):', specErr)
        // Continue — CR status update and manifest may still succeed
      }
      const res = await changeRequestAPI.updateChangeRequestStatus(changeRequest.changeId, {
        currentStatus: 'Approved',
        reviewComments: comments || undefined,
      })
      // Backend now attempts to create manifest automatically on approval.
      const manifestCreated = res?.data?.manifest?.created
      const manifestError = res?.data?.manifest?.error
      if (manifestCreated === false) {
        toast.warning('Approved, but manifest not created', String(manifestError || 'Please try creating/downloading the manifest again.'))
      } else if (manifestCreated === true) {
        toast.success('Manifest ready', 'Manifest was generated and is available to download/broadcast.')
      } else {
        // Fallback: try explicitly
        try {
          await createAndStoreManifest(changeRequest.changeId)
        } catch (manifestErr) {
          console.warn('Manifest create/store failed:', manifestErr)
          toast.warning('Approved, but manifest not created', 'Could not auto-generate manifest. Please retry from Publish tab.')
        }
      }
      toast.success('Approved', 'Change request approved successfully.')
      onStatusUpdated?.()
      onOpenChange(false)
    } catch (error) {
      console.error('Error approving change request:', error)
      toast.error('Approval failed', 'Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  const handleReject = async () => {
    setSubmitting(true)
    try {
      await changeRequestAPI.updateChangeRequestStatus(changeRequest.changeId, {
        currentStatus: 'Rejected',
        reviewComments: comments || undefined,
      })
      toast.warning('Rejected', 'Change request rejected.')
      onStatusUpdated?.()
      onOpenChange(false)
    } catch (error) {
      console.error('Error rejecting change request:', error)
      toast.error('Rejection failed', 'Please try again.')
    } finally {
      setSubmitting(false)
    }
  }

  if (!changeRequest) return null

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-[96vw] h-[90vh] w-full flex flex-col p-0 overflow-hidden gap-0">
        <DialogHeader className="px-6 pt-5 pb-3 flex-shrink-0 border-b bg-slate-50/80">
          <div className="flex items-start justify-between gap-3">
            <DialogTitle className="text-lg font-semibold flex items-center gap-2">
              <FileCode className="h-5 w-5 text-[#2F888A]" />
              Code Changes — {changeRequest.changeId}
            </DialogTitle>
            {currentStatus === 'Approved' && (
              <Button variant="outline" size="sm" asChild>
                <a href={getManifestDownloadUrl(changeRequest.changeId)} download={`${changeRequest.changeId}.json`}>
                  <Download className="mr-2 h-4 w-4" />
                  Download manifest
                </a>
              </Button>
            )}
          </div>
          <DialogDescription className="text-sm text-slate-600">
            {changeRequest?.loading ? 'Fetching code changes…' : (changeRequest?.description || 'Compare original and updated Java files from UPIVerse')}
          </DialogDescription>
        </DialogHeader>

        {changeRequest?.loading ? (
          <div className="flex-1 flex flex-col items-center justify-center py-16 px-6">
            <Loader2 className="h-12 w-12 text-[#2F888A] animate-spin mb-4" />
            <p className="text-slate-600 font-medium">Loading code changes...</p>
            <p className="text-sm text-slate-500 mt-1">This may take a few seconds</p>
          </div>
        ) : (
        <div className="flex-1 flex min-h-0 overflow-hidden">
          {/* Left: File list */}
          <div className="w-56 flex-shrink-0 border-r bg-slate-50/50 flex flex-col overflow-hidden">
            <div className="px-3 py-2 border-b bg-slate-100/80 text-xs font-medium text-slate-600 uppercase tracking-wider">
              Changed files
            </div>
            <div className="flex-1 overflow-y-auto py-2">
              {files.length === 0 ? (
                <div className="px-3 py-6 text-center text-slate-400 text-sm">
                  No code changes
                </div>
              ) : (
                files.map((f, i) => (
                  <button
                    key={i}
                    type="button"
                    onClick={() => setSelectedIndex(i)}
                    className={`w-full text-left px-3 py-2.5 flex items-center gap-2 transition-colors ${
                      selectedIndex === i
                        ? 'bg-[#2F888A]/15 text-[#2F888A] border-l-2 border-[#2F888A]'
                        : 'hover:bg-slate-100 text-slate-700'
                    }`}
                  >
                    <FileText className="h-4 w-4 flex-shrink-0 text-slate-500" />
                    <span className="truncate text-sm font-medium">{f.fileName}</span>
                    <ChevronRight className={`h-4 w-4 flex-shrink-0 ml-auto ${selectedIndex === i ? 'text-[#2F888A]' : 'text-slate-300'}`} />
                  </button>
                ))
              )}
            </div>
          </div>

          {/* Right: Split diff view */}
          <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
            {files.length === 0 ? (
              <div className="flex-1 flex items-center justify-center text-slate-600">
                <div className="text-center max-w-md px-4">
                  <FileCode className="h-14 w-14 mx-auto mb-3 opacity-40" />
                  <p className="font-medium">No code changes to display</p>
                  {changeRequest?.patchError ? (
                    <p className="text-sm mt-2 text-amber-700 bg-amber-50 border border-amber-200 rounded-lg p-3">
                      {changeRequest.patchError}
                    </p>
                  ) : (
                    <p className="text-sm mt-1">Ensure the change was submitted by Product (Generate XSD → Submit) and the spec was approved. Then open this change again to load code changes.</p>
                  )}
                </div>
              </div>
            ) : selected ? (
              <>
                <div className="flex items-center justify-between px-4 py-2 border-b bg-white">
                  <span className="text-sm font-mono text-slate-700 truncate" title={selected.relativePath || selected.fileName}>
                    {selected.relativePath || selected.fileName}
                  </span>
                  <div className="flex items-center gap-2 text-xs text-slate-500">
                    <span className="px-2 py-0.5 rounded bg-rose-50 text-rose-700">Current (left)</span>
                    <span className="px-2 py-0.5 rounded bg-emerald-50 text-emerald-700">New (right)</span>
                  </div>
                </div>
                <div className="flex-1 overflow-auto">
                  <ReactDiffViewer
                    oldValue={selected.oldCode ?? ''}
                    newValue={selected.newCode ?? selected.diff ?? ''}
                    splitView
                    leftTitle="Current code"
                    rightTitle="New code"
                    useDarkTheme={false}
                    showDiffOnly={false}
                    styles={{
                      variables: {
                        light: {
                          diffViewerBackground: '#fafafa',
                          diffViewerColor: '#1e293b',
                          addedBackground: '#dcfce7',
                          addedColor: '#166534',
                          removedBackground: '#fee2e2',
                          removedColor: '#991b1b',
                          wordAddedBackground: '#bbf7d0',
                          wordRemovedBackground: '#fecaca',
                        },
                      },
                      line: { padding: '4px 8px' },
                    }}
                  />
                </div>
              </>
            ) : null}
          </div>
        </div>
        )}

        {/* Approve/Reject (only when showApproveReject and not loading) */}
        {!changeRequest?.loading && canApproveReject && (
          <div className="px-6 py-4 border-t bg-slate-50 flex-shrink-0">
            <div className="space-y-3">
              <Label htmlFor="comments" className="text-sm font-medium">
                Comments <span className="text-slate-500 font-normal">(optional)</span>
              </Label>
              <Textarea
                id="comments"
                placeholder="Comments for approval or rejection..."
                value={comments}
                onChange={(e) => setComments(e.target.value)}
                rows={2}
                className="resize-none"
              />
              <div className="flex justify-end gap-3">
                <Button variant="outline" onClick={() => onOpenChange(false)} disabled={submitting}>
                  Cancel
                </Button>
                <Button
                  onClick={handleReject}
                  disabled={submitting}
                  variant="destructive"
                  className="min-w-[100px]"
                >
                  {submitting ? <RefreshCw className="h-4 w-4 animate-spin" /> : <XCircle className="mr-2 h-4 w-4" />}
                  Reject
                </Button>
                <Button
                  onClick={handleApprove}
                  disabled={submitting}
                  className="min-w-[100px] bg-emerald-600 hover:bg-emerald-700"
                >
                  {submitting ? <RefreshCw className="h-4 w-4 animate-spin" /> : <CheckCircle2 className="mr-2 h-4 w-4" />}
                  Approve
                </Button>
              </div>
            </div>
          </div>
        )}

        {!changeRequest?.loading && !canApproveReject && (
          <div className="px-6 py-3 border-t bg-slate-50 flex-shrink-0 flex justify-end">
            <Button variant="outline" onClick={() => onOpenChange(false)}>
              Close
            </Button>
          </div>
        )}
      </DialogContent>
    </Dialog>
  )
}
