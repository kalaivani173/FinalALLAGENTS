# Start all four agent backends (PayerPSP, PayeePSP, RemitterBank, BeneficiaryBank)
# Each runs in a new window. Close the window to stop that backend.

$root = Split-Path -Parent (Split-Path -Parent $PSCommandPath)

$agents = @(
    @{ Name = "PayerPSP";     Path = "Payer-agent";     Port = 9001 },
    @{ Name = "BeneficiaryBank"; Path = "Beneficiary-agent"; Port = 9002 },
    @{ Name = "RemitterBank"; Path = "Remitter-agent";  Port = 9003 },
    @{ Name = "PayeePSP";     Path = "Payee-agent";    Port = 9004 }
)

foreach ($a in $agents) {
    $dir = Join-Path $root $a.Path
    if (-not (Test-Path $dir)) {
        Write-Warning "Skip $($a.Name): $dir not found"
        continue
    }
    $title = "Backend: $($a.Name) :$($a.Port)"
    $cmd = "Set-Location '$dir'; python -m uvicorn app:app --reload --host 127.0.0.1 --port $($a.Port)"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $cmd
    Write-Host "Started $title"
    Start-Sleep -Seconds 1
}

Write-Host "`nAll agent backends launched in separate windows."
Write-Host "PayerPSP=9001, BeneficiaryBank=9002, RemitterBank=9003, PayeePSP=9004"
