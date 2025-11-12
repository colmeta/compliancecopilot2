# Test Data Entry Functionality
Write-Host "=== Testing Data Entry Domain ===" -ForegroundColor Cyan

# Test 1: Check if data-entry is in domains list
Write-Host "`n1. Testing /instant/domains endpoint..." -ForegroundColor Yellow
try {
    $domains = Invoke-RestMethod -Uri "https://veritas-engine-zae0.onrender.com/instant/domains"
    $dataEntry = $domains.domains | Where-Object { $_.id -eq "data-entry" }
    if ($dataEntry) {
        Write-Host "✅ Data Entry domain found!" -ForegroundColor Green
        Write-Host "   Name: $($dataEntry.name)" -ForegroundColor White
        Write-Host "   Description: $($dataEntry.description)" -ForegroundColor White
    } else {
        Write-Host "❌ Data Entry domain NOT found" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
}

# Test 2: Test instant analyze with data-entry domain
Write-Host "`n2. Testing /instant/analyze with data-entry domain..." -ForegroundColor Yellow
try {
    $body = @{
        directive = "Extract invoice data from this document"
        domain = "data-entry"
    } | ConvertTo-Json
    
    $result = Invoke-RestMethod -Uri "https://veritas-engine-zae0.onrender.com/instant/analyze" `
        -Method Post `
        -Headers @{"Content-Type"="application/json"} `
        -Body $body
    
    if ($result.success) {
        Write-Host "✅ Data Entry analysis successful!" -ForegroundColor Green
        Write-Host "   Task ID: $($result.task_id)" -ForegroundColor White
        Write-Host "   Domain: $($result.domain)" -ForegroundColor White
        Write-Host "   Status: $($result.status)" -ForegroundColor White
        Write-Host "   Summary: $($result.analysis.summary)" -ForegroundColor White
        Write-Host "   Confidence: $($result.analysis.confidence)" -ForegroundColor White
        Write-Host "   Findings:" -ForegroundColor White
        foreach ($finding in $result.analysis.findings) {
            Write-Host "     - $finding" -ForegroundColor Gray
        }
    } else {
        Write-Host "❌ Analysis failed: $($result.error)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
    if ($_.Exception.Response) {
        $reader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream())
        $responseBody = $reader.ReadToEnd()
        Write-Host "   Response: $responseBody" -ForegroundColor Red
    }
}

# Test 3: Check real AI health
Write-Host "`n3. Testing Real AI Engine health..." -ForegroundColor Yellow
try {
    $health = Invoke-RestMethod -Uri "https://veritas-engine-zae0.onrender.com/real/health"
    if ($health.ready) {
        Write-Host "✅ Real AI Engine is ready!" -ForegroundColor Green
        Write-Host "   Model: $($health.model)" -ForegroundColor White
        Write-Host "   Status: $($health.status)" -ForegroundColor White
    } else {
        Write-Host "❌ Real AI Engine not ready: $($health.message)" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
}

# Test 4: Check if data-entry is in real domains
Write-Host "`n4. Testing /real/domains endpoint..." -ForegroundColor Yellow
try {
    $realDomains = Invoke-RestMethod -Uri "https://veritas-engine-zae0.onrender.com/real/domains"
    $dataEntryReal = $realDomains.domains | Where-Object { $_.id -eq "data-entry" }
    if ($dataEntryReal) {
        Write-Host "✅ Data Entry in Real AI domains!" -ForegroundColor Green
        Write-Host "   Example: $($dataEntryReal.example)" -ForegroundColor White
        Write-Host "   AI Powered: $($dataEntryReal.ai_powered)" -ForegroundColor White
    } else {
        Write-Host "❌ Data Entry NOT in Real AI domains" -ForegroundColor Red
    }
} catch {
    Write-Host "❌ Error: $_" -ForegroundColor Red
}

Write-Host "`n=== Test Complete ===" -ForegroundColor Cyan


