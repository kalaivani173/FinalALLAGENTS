import * as XLSX from 'xlsx'

/**
 * Build a workbook from sheet data and trigger download.
 * @param {Array<Array<string>>} rows - Array of rows (each row is array of cell values).
 * @param {string} sheetName - Name of the sheet.
 * @param {string} filename - Download filename (without extension).
 */
export function downloadExcel(rows, sheetName = 'Sheet1', filename = 'export') {
  const ws = XLSX.utils.aoa_to_sheet(rows)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, sheetName)
  XLSX.writeFile(wb, `${filename}.xlsx`)
}

/**
 * Export "By Change Request" view: flat list with CHG_ID, BANK-Name, Status (one row per change + bank + status).
 * @param {Record<string, Record<string, string>>} orchestratorState - { changeId: { agent: status } }
 */
export function exportByChangeRequest(orchestratorState) {
  const header = ['CHG_ID', 'BANK-Name', 'Status']
  const rows = [header]
  const changeIds = Object.keys(orchestratorState).sort()
  for (const cid of changeIds) {
    const agentsMap = orchestratorState[cid] || {}
    const agents = Object.keys(agentsMap).sort()
    for (const agent of agents) {
      const status = agentsMap[agent] || '—'
      rows.push([cid, agent, status])
    }
  }
  downloadExcel(rows, 'By Change Request', 'status-by-change-request')
}

/**
 * Export "By Partner" view: one row per (partner, CR) with delivery status and orchestrator status.
 * @param {Record<string, Record<string, { statusCode: number, response: string }>>} partnerCrStatus - delivery status
 * @param {Record<string, Record<string, string>>} orchestratorStatus - orchestrator status
 */
export function exportByPartner(partnerCrStatus, orchestratorStatus) {
  const header = ['Partner', 'Change ID', 'Delivery Status', 'Response / Party Status']
  const rows = [header]
  const partnerEntries = Object.entries(partnerCrStatus || {}).sort(([a], [b]) => a.localeCompare(b))
  for (const [partnerId, crMap] of partnerEntries) {
    const crEntries = Object.entries(crMap || {}).sort(([a], [b]) => (a || '').localeCompare(b || ''))
    for (const [crId, result] of crEntries) {
      const code = result?.statusCode
      const deliveryStatus = code === 200 || code === '200' ? 'Sent' : code === 0 || code === '0' ? 'Error/Timeout' : String(code ?? '')
      const agentsMap = orchestratorStatus?.[crId]
      const partyStatusStr = agentsMap && typeof agentsMap === 'object'
        ? Object.entries(agentsMap).map(([agent, status]) => `${agent}: ${status}`).join('; ')
        : (result?.response ?? '')
      rows.push([partnerId, crId, deliveryStatus, partyStatusStr || result?.response || '—'])
    }
  }
  downloadExcel(rows, 'By Partner', 'status-by-partner')
}

/**
 * Export "Find Change ID" list: Change Request Number, Summary.
 * @param {Array<{ changeId: string, description?: string }>} list
 */
export function exportFindChangeIdList(list) {
  const header = ['Change Request Number', 'Summary']
  const rows = [header, ...(list || []).map((row) => [row.changeId || '', row.description || '—'])]
  downloadExcel(rows, 'Find Change ID', 'find-change-id-list')
}
