import ReactDiffViewer from 'react-diff-viewer-continued'

/** Parse unified diff and extract old/new content for ReactDiffViewer. */
function unifiedDiffToOldNew(raw) {
  if (!raw || typeof raw !== 'string') return { oldValue: '', newValue: '' }
  let text = raw.trim()
  if (text.startsWith('```diff')) text = text.slice(7)
  if (text.startsWith('```')) text = text.slice(3)
  if (text.endsWith('```')) text = text.slice(0, -3)
  text = text.trim()
  const lines = text.split(/\r?\n/)
  const oldLines = []
  const newLines = []
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    const first = line.charAt(0)
    const rest = line.slice(1) || ''
    if (line.startsWith('--- ') || line.startsWith('+++ ')) continue
    if (line.startsWith('@@')) continue
    if (first === ' ') {
      oldLines.push(rest)
      newLines.push(rest)
    } else if (first === '-') {
      oldLines.push(rest)
    } else if (first === '+') {
      newLines.push(rest)
    }
  }
  return {
    oldValue: oldLines.join('\n'),
    newValue: newLines.join('\n'),
  }
}

/** Diff view using react-diff-viewer-continued (same setup as aicode developer portal). */
export default function DiffView({ patchContent }) {
  const { oldValue, newValue } = unifiedDiffToOldNew(patchContent)
  if (!patchContent || !patchContent.trim()) {
    return <pre className="code-block diff-block">No diff yet. Click Generate to create code changes.</pre>
  }
  return (
    <div className="diff-view-wrap diff-viewer-modern">
      <ReactDiffViewer
        oldValue={oldValue}
        newValue={newValue}
        splitView
        leftTitle="Current code"
        rightTitle="Code changes"
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
  )
}
