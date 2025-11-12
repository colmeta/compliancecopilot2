# Test Deployment - Verify Everything Works
# Run this script after deployment to verify fixes

Write-Host "🧪 Testing CLARITY Deployment..." -ForegroundColor Cyan
Write-Host ""

$BACKEND_URL = "https://veritas-engine-zae0.onrender.com"
$FRONTEND_URL = "https://clarity-engine-auto.vercel.app"

# Test 1: Backend Health
Write-Host "1️⃣ Testing Backend Health..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod -Uri "$BACKEND_URL/health" -Method GET -TimeoutSec 10
    Write-Host "   ✅ Backend is UP!" -ForegroundColor Green
    Write-Host "   Response: $($response | ConvertTo-Json -Compress)" -ForegroundColor Gray
} catch {
    Write-Host "   ❌ Backend is DOWN or hibernating" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   💡 If hibernating, wait 30-60 seconds and try again" -ForegroundColor Yellow
}

Write-Host ""

# Test 2: CORS Configuration
Write-Host "2️⃣ Testing CORS Configuration..." -ForegroundColor Yellow
try {
    $headers = @{
        "Origin" = "https://clarity-engine-auto.vercel.app"
        "Access-Control-Request-Method" = "POST"
    }
    $response = Invoke-WebRequest -Uri "$BACKEND_URL/instant/analyze" -Method OPTIONS -Headers $headers -TimeoutSec 10
    if ($response.Headers["Access-Control-Allow-Origin"]) {
        Write-Host "   ✅ CORS is configured!" -ForegroundColor Green
        Write-Host "   Allow-Origin: $($response.Headers['Access-Control-Allow-Origin'])" -ForegroundColor Gray
    } else {
        Write-Host "   ⚠️  CORS headers not found" -ForegroundColor Yellow
    }
} catch {
    Write-Host "   ⚠️  CORS test failed (may be normal)" -ForegroundColor Yellow
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Gray
}

Write-Host ""

# Test 3: Instant Analyze Endpoint
Write-Host "3️⃣ Testing Instant Analyze Endpoint..." -ForegroundColor Yellow
try {
    $body = @{
        directive = "Test legal analysis"
        domain = "legal"
    } | ConvertTo-Json

    $response = Invoke-RestMethod -Uri "$BACKEND_URL/instant/analyze" -Method POST -Body $body -ContentType "application/json" -TimeoutSec 30
    
    if ($response.success) {
        Write-Host "   ✅ Analysis endpoint works!" -ForegroundColor Green
        Write-Host "   Task ID: $($response.task_id)" -ForegroundColor Gray
    } else {
        Write-Host "   ⚠️  Analysis returned error" -ForegroundColor Yellow
        Write-Host "   Error: $($response.error)" -ForegroundColor Gray
    }
} catch {
    Write-Host "   ❌ Analysis endpoint failed" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "   💡 Backend may be hibernating - wait 30-60 seconds" -ForegroundColor Yellow
}

Write-Host ""

# Test 4: Frontend URL
Write-Host "4️⃣ Testing Frontend URL..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri $FRONTEND_URL -Method GET -TimeoutSec 10
    if ($response.StatusCode -eq 200) {
        Write-Host "   ✅ Frontend is accessible!" -ForegroundColor Green
        Write-Host "   URL: $FRONTEND_URL" -ForegroundColor Gray
    }
} catch {
    Write-Host "   ⚠️  Frontend may not be deployed yet" -ForegroundColor Yellow
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Gray
}

Write-Host ""
Write-Host "📊 Test Summary" -ForegroundColor Cyan
Write-Host "================" -ForegroundColor Cyan
Write-Host ""
Write-Host "✅ If all tests pass: Deployment successful!" -ForegroundColor Green
Write-Host "⚠️  If backend tests fail: Backend may be hibernating (normal on free tier)" -ForegroundColor Yellow
Write-Host "💡 Solution: Set up keep-alive service (see KEEP_ALIVE_SETUP.md)" -ForegroundColor Cyan
Write-Host ""

