#!/usr/bin/env powershell
<#
.SYNOPSIS
포트 점유 프로세스 종료 스크립트

.DESCRIPTION
지정된 포트를 사용 중인 프로세스를 찾아 종료합니다.

.PARAMETER Port
해제할 포트 번호 (기본값: 9000)

.EXAMPLE
.\kill_port.ps1
.\kill_port.ps1 -Port 8000

#>

param(
    [int]$Port = 9000
)

Write-Host ""
Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host "포트 점유 프로세스 종료" -ForegroundColor Cyan
Write-Host ("=" * 80) -ForegroundColor Cyan
Write-Host ""

# 포트 사용 현황 확인
$connections = netstat -ano | Select-String ":$Port "
if (-not $connections) {
    Write-Host "✅ 포트 $Port 는 사용 중이지 않습니다." -ForegroundColor Green
    exit 0
}

Write-Host "포트 $Port 를 사용 중인 프로세스:" -ForegroundColor Yellow
Write-Host ""
Write-Host $connections
Write-Host ""

# PID 추출
$pids = @()
foreach ($line in $connections) {
    $parts = $line -split '\s+' | Where-Object { $_ }
    if ($parts.Count -ge 5) {
        $pid = $parts[-1]
        if ($pid -match '^\d+$') {
            $pids += $pid
        }
    }
}

if ($pids.Count -eq 0) {
    Write-Host "❌ PID를 추출할 수 없습니다." -ForegroundColor Red
    exit 1
}

# 프로세스 정보 표시
Write-Host "강제 종료할 프로세스:" -ForegroundColor Yellow
foreach ($pid in $pids) {
    $process = Get-Process -Id $pid -ErrorAction SilentlyContinue
    if ($process) {
        Write-Host "  PID: $pid, 프로세스: $($process.ProcessName)" -ForegroundColor Yellow
    }
}
Write-Host ""

# 사용자 확인
$confirm = Read-Host "위 프로세스를 종료하시겠습니까? (Y/N)"
if ($confirm -ne 'Y' -and $confirm -ne 'y') {
    Write-Host "취소되었습니다." -ForegroundColor Yellow
    exit 0
}

# 프로세스 종료
Write-Host ""
foreach ($pid in $pids) {
    try {
        taskkill /PID $pid /F | Out-Null
        Write-Host "✅ PID $pid 종료 성공" -ForegroundColor Green
    } catch {
        Write-Host "❌ PID $pid 종료 실패: $_" -ForegroundColor Red
    }
}

# 잠시 기다린 후 포트 재확인
Start-Sleep -Seconds 2

$connections = netstat -ano | Select-String ":$Port "
if ($connections) {
    Write-Host ""
    Write-Host "⚠️  포트 $Port 는 여전히 사용 중입니다:" -ForegroundColor Yellow
    Write-Host $connections
} else {
    Write-Host ""
    Write-Host "✅ 포트 $Port 가 성공적으로 해제되었습니다." -ForegroundColor Green
}

Write-Host ""
