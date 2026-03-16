$ports = @(8000, 3000, 9001, 9002, 9003, 9004, 5173, 5174, 5175, 5176)
foreach ($port in $ports) {
    $conn = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | Where-Object { $_.State -eq 'Listen' }
    if ($conn) {
        $procId = ($conn | Select-Object -First 1).OwningProcess
        Write-Host "Killing port $port (PID $procId)"
        Stop-Process -Id $procId -Force -ErrorAction SilentlyContinue
    }
}
Write-Host "Done."
