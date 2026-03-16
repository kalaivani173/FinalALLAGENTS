# Start all four agent frontends (PayerPSP, PayeePSP, RemitterBank, BeneficiaryBank)
# Each runs in a new window. Close the window to stop that frontend.

$root = Split-Path -Parent (Split-Path -Parent $PSCommandPath)

$agents = @(
    @{ Name = "PayerPSP";     Path = "Payer-agent\frontend";     Port = 5173 },
    @{ Name = "BeneficiaryBank"; Path = "Beneficiary-agent\frontend"; Port = 5174 },
    @{ Name = "RemitterBank"; Path = "Remitter-agent\frontend";  Port = 5175 },
    @{ Name = "PayeePSP";     Path = "Payee-agent\frontend";    Port = 5176 }
)

foreach ($a in $agents) {
    $dir = Join-Path $root $a.Path
    if (-not (Test-Path $dir)) {
        Write-Warning "Skip $($a.Name): $dir not found"
        continue
    }
    $title = "Frontend: $($a.Name) :$($a.Port)"
    $cmd = "Set-Location '$dir'; npm run dev"
    Start-Process powershell -ArgumentList "-NoExit", "-Command", $cmd
    Write-Host "Started $title"
    Start-Sleep -Seconds 1
}

Write-Host "`nAll agent frontends launched in separate windows."
Write-Host "PayerPSP=5173, BeneficiaryBank=5174, RemitterBank=5175, PayeePSP=5176"
