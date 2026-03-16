$conn = Get-NetTCPConnection -LocalPort 3000 -State Listen -ErrorAction SilentlyContinue
if ($conn) {
  $p = $conn.OwningProcess
  Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
  Write-Output "Killed process $p"
} else {
  Write-Output "No process on 3000"
}
