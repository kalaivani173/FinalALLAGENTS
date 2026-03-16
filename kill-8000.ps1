$conn = Get-NetTCPConnection -LocalPort 8000 -State Listen -ErrorAction SilentlyContinue
if ($conn) {
  $procId = $conn.OwningProcess
  Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
  Write-Output "Killed process $procId"
} else {
  Write-Output "No process on 8000"
}
