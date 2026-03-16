# Stop processes listening on backend and frontend ports
$backendPorts = @(8000, 9001, 9002, 9003, 9004)
$frontendPorts = @(5173, 5174, 5175, 5176, 5177, 5178, 3000, 3001)
$allPorts = $backendPorts + $frontendPorts

foreach ($port in $allPorts) {
    $conns = Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue
    $pids = $conns | Select-Object -ExpandProperty OwningProcess -Unique
    foreach ($procId in $pids) {
        try {
            Stop-Process -Id $procId -Force -ErrorAction Stop
            Write-Host "Stopped process $procId (port $port)"
        } catch {
            # ignore
        }
    }
}
Write-Host "Done."
