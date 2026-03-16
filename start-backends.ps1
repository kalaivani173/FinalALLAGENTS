# start-backends.ps1
$root = "C:\Users\kalai\OneDrive\Desktop\TechConclave\Allagents"

# Aicode (orchestrator) backend - 8000
Start-Process powershell -ArgumentList @"
cd "$root\aicode"
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
"@

# Payer-agent backend - 9001
Start-Process powershell -ArgumentList @"
cd "$root\Payer-agent"
python -m uvicorn app:app --reload --host 127.0.0.1 --port 9001
"@

# Beneficiary-agent backend - 9002
Start-Process powershell -ArgumentList @"
cd "$root\Beneficiary-agent"
python -m uvicorn app:app --reload --host 127.0.0.1 --port 9002
"@

# Remitter-agent backend - 9003
Start-Process powershell -ArgumentList @"
cd "$root\Remitter-agent"
python -m uvicorn app:app --reload --host 127.0.0.1 --port 9003
"@

# Payee-agent backend - 9004
Start-Process powershell -ArgumentList @"
cd "$root\Payee-agent"
python -m uvicorn app:app --reload --host 127.0.0.1 --port 9004
"@