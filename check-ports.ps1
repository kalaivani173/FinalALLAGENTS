$ports = @(9001,9002,9003,9004,5173,5174,5175,5176)
Get-NetTCPConnection -State Listen -ErrorAction SilentlyContinue | 
  Where-Object { $ports -contains $_.LocalPort } | 
  Select-Object LocalPort, OwningProcess | 
  Sort-Object LocalPort | 
  Format-Table -AutoSize
