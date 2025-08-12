# Leave Management System API Testing Script
# Run this script to test all API endpoints

Write-Host "🚀 Testing Leave Management System APIs" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green

$baseUrl = "http://localhost:8000"

# Test 1: Create Employee
Write-Host "`n1️⃣ Testing Employee Creation..." -ForegroundColor Yellow
$employeeData = @{
    name = "John Doe"
    email = "john.doe@company.com"
    department = "Engineering"
    joining_date = "2024-01-15"
} | ConvertTo-Json

try {
    $employee = Invoke-RestMethod -Uri "$baseUrl/employees/" -Method POST -ContentType "application/json" -Body $employeeData
    Write-Host "✅ Employee created successfully!" -ForegroundColor Green
    Write-Host "Employee ID: $($employee.id)" -ForegroundColor Cyan
    Write-Host "Leave Balance: $($employee.leave_balance)" -ForegroundColor Cyan
    $employeeId = $employee.id
} catch {
    Write-Host "❌ Failed to create employee: $($_.Exception.Message)" -ForegroundColor Red
    exit 1
}

# Test 2: Check Employee Balance
Write-Host "`n2️⃣ Testing Balance Check..." -ForegroundColor Yellow
try {
    $balance = Invoke-RestMethod -Uri "$baseUrl/employees/$employeeId/balance" -Method GET
    Write-Host "✅ Balance retrieved successfully!" -ForegroundColor Green
    Write-Host "Current Balance: $($balance.balance) days" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Failed to get balance: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 3: Apply for Leave (Valid Request)
Write-Host "`n3️⃣ Testing Valid Leave Application..." -ForegroundColor Yellow
$leaveData = @{
    employee_id = $employeeId
    start_date = "2024-08-15"
    end_date = "2024-08-17"
} | ConvertTo-Json

try {
    $leave = Invoke-RestMethod -Uri "$baseUrl/leaves/" -Method POST -ContentType "application/json" -Body $leaveData
    Write-Host "✅ Leave application successful!" -ForegroundColor Green
    Write-Host "Leave ID: $($leave.id)" -ForegroundColor Cyan
    Write-Host "Days Requested: $($leave.days)" -ForegroundColor Cyan
    Write-Host "Status: $($leave.status)" -ForegroundColor Cyan
    $leaveId = $leave.id
} catch {
    Write-Host "❌ Failed to apply for leave: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 4: Approve Leave
Write-Host "`n4️⃣ Testing Leave Approval..." -ForegroundColor Yellow
try {
    $approval = Invoke-RestMethod -Uri "$baseUrl/leaves/$leaveId/approve" -Method POST
    Write-Host "✅ Leave approved successfully!" -ForegroundColor Green
    Write-Host "Status: $($approval.status)" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Failed to approve leave: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 5: Check Updated Balance
Write-Host "`n5️⃣ Testing Updated Balance..." -ForegroundColor Yellow
try {
    $updatedBalance = Invoke-RestMethod -Uri "$baseUrl/employees/$employeeId/balance" -Method GET
    Write-Host "✅ Updated balance retrieved!" -ForegroundColor Green
    Write-Host "New Balance: $($updatedBalance.balance) days" -ForegroundColor Cyan
} catch {
    Write-Host "❌ Failed to get updated balance: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 6: Edge Case - Leave before joining date
Write-Host "`n6️⃣ Testing Edge Case: Leave Before Joining Date..." -ForegroundColor Yellow
$invalidLeaveData = @{
    employee_id = $employeeId
    start_date = "2023-12-01"
    end_date = "2023-12-03"
} | ConvertTo-Json

try {
    $invalidLeave = Invoke-RestMethod -Uri "$baseUrl/leaves/" -Method POST -ContentType "application/json" -Body $invalidLeaveData
    Write-Host "❌ Should have failed but didn't!" -ForegroundColor Red
} catch {
    Write-Host "✅ Correctly rejected leave before joining date!" -ForegroundColor Green
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Cyan
}

# Test 7: Edge Case - Insufficient Balance
Write-Host "`n7️⃣ Testing Edge Case: Insufficient Balance..." -ForegroundColor Yellow
$excessiveLeaveData = @{
    employee_id = $employeeId
    start_date = "2024-09-01"
    end_date = "2024-09-30"
} | ConvertTo-Json

try {
    $excessiveLeave = Invoke-RestMethod -Uri "$baseUrl/leaves/" -Method POST -ContentType "application/json" -Body $excessiveLeaveData
    Write-Host "❌ Should have failed but didn't!" -ForegroundColor Red
} catch {
    Write-Host "✅ Correctly rejected excessive leave request!" -ForegroundColor Green
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Cyan
}

# Test 8: Edge Case - Employee Not Found
Write-Host "`n8️⃣ Testing Edge Case: Employee Not Found..." -ForegroundColor Yellow
try {
    $nonExistentBalance = Invoke-RestMethod -Uri "$baseUrl/employees/999/balance" -Method GET
    Write-Host "❌ Should have failed but didn't!" -ForegroundColor Red
} catch {
    Write-Host "✅ Correctly handled non-existent employee!" -ForegroundColor Green
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Cyan
}

Write-Host "`n🎉 API Testing Complete!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Green
