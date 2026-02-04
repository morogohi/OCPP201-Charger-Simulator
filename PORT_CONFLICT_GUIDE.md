# 포트 충돌 문제 해결 가이드

## 문제 증상

```
OSError: [Errno 10048] error while attempting to bind on address ('127.0.0.1', 9000)
[winerror 10048] 각 소켓 주소(프로토콜/네트워크 주소/포트)는 하나만 사용할 수 있습니다
```

이 오류는 포트 9000(또는 8000)이 이미 다른 프로세스에 의해 점유되고 있을 때 발생합니다.

## 원인

1. **이전 서버 프로세스 미종료**: 이전 실행한 OCPP 서버가 여전히 포트를 점유 중
2. **TIME_WAIT 상태**: 최근에 종료된 프로세스의 소켓이 OS 수준에서 아직 해제되지 않음 (보통 30초~2분)
3. **다른 애플리케이션**: 같은 포트를 사용하는 다른 프로그램 실행 중

## 빠른 해결 방법

### 방법 1: 포트 해제 스크립트 사용 (권장)

```powershell
# 포트 9000 해제
.\kill_port.ps1 -Port 9000

# 포트 8000 해제
.\kill_port.ps1 -Port 8000
```

### 방법 2: 수동으로 프로세스 종료

```powershell
# 포트 9000 사용 프로세스 확인
netstat -ano | findstr "9000"

# 출력 예시: TCP  127.0.0.1:9000  0.0.0.0:0  LISTENING  12345
# PID 12345 프로세스 강제 종료
taskkill /PID 12345 /F
```

### 방법 3: 시스템 대기 (TIME_WAIT 해제)

포트가 TIME_WAIT 상태인 경우 30초~2분 정도 기다렸다가 다시 시도하세요.

## 근본적인 해결 방법

### Windows에서 SO_REUSEADDR 활성화

Windows는 기본적으로 TIME_WAIT 상태의 포트를 재사용하지 않습니다. 다음 레지스트리 설정으로 이를 완화할 수 있습니다:

```powershell
# PowerShell (관리자 권한 필요)

# TIME_WAIT 상태 시간 단축 (기본: 240초, 30초로 변경)
REG ADD HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters /v TcpTimedWaitDelay /t REG_DWORD /d 30 /f

# 설정 확인
REG QUERY HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Services\Tcpip\Parameters /v TcpTimedWaitDelay

# 재부팅이 필요할 수 있습니다
```

### 다른 포트 사용하기

기본 포트를 변경하고 싶으면 환경변수로 포트 번호를 지정할 수 있도록 수정할 수 있습니다.

## 예방 방법

1. **정상 종료**: 서버를 중지할 때는 `Ctrl+C` 사용 (강제 종료 피하기)
2. **포트 확인**: 서버 시작 전에 `.\kill_port.ps1`로 포트 점유 확인
3. **자동 재시작**: `run_integrated.ps1` 스크립트에서 포트 확인 로직 추가

## 확인 방법

포트가 제대로 해제되었는지 확인:

```powershell
# 포트 9000 상태 확인 (아무 출력도 없어야 함)
netstat -ano | findstr "9000"

# 포트 8000 상태 확인 (아무 출력도 없어야 함)
netstat -ano | findstr "8000"
```

## 추가 정보

- OCPP 서버: 기본 포트 9000
- GIS 대시보드: 기본 포트 8000
- 포트 확인 명령: `netstat -ano | findstr "<포트번호>"`
- 프로세스 강제 종료: `taskkill /PID <PID> /F`
