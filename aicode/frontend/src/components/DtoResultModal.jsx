import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Button } from '@/components/ui/button'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs'
import { Copy, Download, Check, FileCode } from 'lucide-react'

export default function DtoResultModal({ open, onOpenChange, result }) {
  const success = result?.success === true
  const hasCode = !!result?.updatedCode
  const hasDiff = !!(result?.diff || result?.diffHtml)

  const handleCopyCode = async () => {
    if (!result?.updatedCode) return
    try {
      await navigator.clipboard.writeText(result.updatedCode)
      // could add a brief "Copied!" toast; for now we rely on native behavior
    } catch (e) {
      console.error('Copy failed:', e)
    }
  }

  const handleDownload = () => {
    if (!result?.updatedCode) return
    const name = result?.dtoFilePath?.split(/[/\\]/).pop() || 'Dto.java'
    const blob = new Blob([result.updatedCode], { type: 'text/plain' })
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = name
    a.click()
    URL.revokeObjectURL(a.href)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="max-w-[95vw] w-full max-h-[90vh] flex flex-col overflow-hidden">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2">
            <FileCode className="h-5 w-5" />
            {success ? 'Java DTO Updated' : 'DTO Generation'}
          </DialogTitle>
          <DialogDescription>
            {success
              ? 'Updated code and diff from XSD. Copy or download to apply in UPIVerse.'
              : 'Review any errors below.'}
          </DialogDescription>
        </DialogHeader>

        {!success && (result?.error || result?.detail) && (
          <div className="rounded-lg bg-red-50 border border-red-200 p-4 text-sm text-red-800">
            {result?.error || result?.detail}
          </div>
        )}

        {success && (hasCode || hasDiff) && (
          <Tabs defaultValue={hasCode ? 'code' : 'diff'} className="flex-1 min-h-0 flex flex-col">
            <TabsList>
              {hasCode && <TabsTrigger value="code">Updated Code</TabsTrigger>}
              {hasDiff && <TabsTrigger value="diff">Diff</TabsTrigger>}
            </TabsList>
            {hasCode && (
              <TabsContent value="code" className="flex-1 min-h-0 mt-3 flex flex-col">
                <div className="flex items-center justify-between gap-2 mb-2">
                  {result?.dtoFilePath && (
                    <span className="text-xs text-muted-foreground truncate" title={result.dtoFilePath}>
                      {result.dtoFilePath}
                    </span>
                  )}
                  <div className="flex gap-2">
                    <Button variant="outline" size="sm" onClick={handleCopyCode}>
                      <Copy className="h-4 w-4 mr-1" />
                      Copy
                    </Button>
                    <Button variant="outline" size="sm" onClick={handleDownload}>
                      <Download className="h-4 w-4 mr-1" />
                      Download
                    </Button>
                  </div>
                </div>
                <pre className="flex-1 overflow-auto rounded border bg-muted/50 p-4 text-xs font-mono overflow-x-auto">
                  <code>{result.updatedCode}</code>
                </pre>
              </TabsContent>
            )}
            {hasDiff && (
              <TabsContent value="diff" className="flex-1 min-h-0 mt-3">
                {result?.diffSummary && (
                  <p className="text-xs text-muted-foreground mb-2">{result.diffSummary}</p>
                )}
                <div
                  className="dto-diff overflow-auto rounded border bg-muted/50 p-4 text-xs font-mono max-h-[50vh]"
                  dangerouslySetInnerHTML={result.diffHtml ? { __html: result.diffHtml } : undefined}
                />
                {!result.diffHtml && result.diff && (
                  <pre className="overflow-auto rounded border bg-muted/50 p-4 text-xs font-mono max-h-[50vh] whitespace-pre-wrap">
                    {result.diff}
                  </pre>
                )}
              </TabsContent>
            )}
          </Tabs>
        )}

        {success && !hasCode && !hasDiff && (
          <p className="text-sm text-muted-foreground">No code or diff returned.</p>
        )}
      </DialogContent>
    </Dialog>
  )
}
