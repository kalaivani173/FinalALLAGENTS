# start-frontends.ps1
$root = "C:\Users\kalai\OneDrive\Desktop\TechConclave\Allagents"

# Aicode frontend - 3000
Start-Process powershell -ArgumentList @"
cd "$root\aicode\frontend"
npm install
npm run dev -- --port 3000
"@

# Payer-agent frontend - 5173
Start-Process powershell -ArgumentList @"
cd "$root\Payer-agent\frontend"
npm install
npm run dev -- --port 5173
"@

# Beneficiary-agent frontend - 5174
Start-Process powershell -ArgumentList @"
cd "$root\Beneficiary-agent\frontend"
npm install
npm run dev -- --port 5174
"@

# Remitter-agent frontend - 5175
Start-Process powershell -ArgumentList @"
cd "$root\Remitter-agent\frontend"
npm install
npm run dev -- --port 5175
"@

# Payee-agent frontend - 5176
Start-Process powershell -ArgumentList @"
cd "$root\Payee-agent\frontend"
npm install
npm run dev -- --port 5176
"@