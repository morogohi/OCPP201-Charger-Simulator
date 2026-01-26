"""
OCPP 프로토콜 로깅 설정 및 유틸리티
"""
import logging
import os
import sys
from datetime import datetime

# 환경변수 기반 로깅 설정
PROTOCOL_DEBUG = os.getenv('OCPP_PROTOCOL_DEBUG', 'false').lower() == 'true'
LOG_LEVEL = os.getenv('OCPP_LOG_LEVEL', 'INFO').upper()
LOG_FILE = os.getenv('OCPP_LOG_FILE', None)


def setup_logging(
    level: str = 'INFO',
    enable_protocol_debug: bool = False,
    log_file: str = None
):
    """
    로깅 설정 함수
    
    Args:
        level: 로깅 레벨 (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_protocol_debug: 프로토콜 디버그 로깅 활성화 여부
        log_file: 로그 파일 경로 (None이면 콘솔만)
    
    Examples:
        # 프로토콜 디버그 로깅 활성화
        setup_logging(enable_protocol_debug=True)
        
        # 파일에 로깅
        setup_logging(level='DEBUG', log_file='ocpp.log')
        
        # 프로토콜 디버그 + 파일 로깅
        setup_logging(enable_protocol_debug=True, log_file='ocpp_debug.log')
    """
    
    # 환경변수 설정
    if enable_protocol_debug:
        os.environ['OCPP_PROTOCOL_DEBUG'] = 'true'
    
    if log_file:
        os.environ['OCPP_LOG_FILE'] = log_file
    
    # 로깅 포매터
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 루트 로거 설정
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # 콘솔 핸들러
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # 파일 핸들러 (선택사항)
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        print(f"로그 파일: {log_file}")
    
    print(f"로깅 레벨: {level}")
    if enable_protocol_debug:
        print("프로토콜 디버그: 활성화됨")


def get_protocol_debug_status() -> bool:
    """현재 프로토콜 디버그 상태 반환"""
    return os.getenv('OCPP_PROTOCOL_DEBUG', 'false').lower() == 'true'


def print_protocol_debug_help():
    """프로토콜 디버그 사용 방법 출력"""
    print("""
    ┌────────────────────────────────────────────────────────────┐
    │  OCPP 프로토콜 디버그 로깅 사용 방법                        │
    └────────────────────────────────────────────────────────────┘
    
    1️⃣  환경변수로 활성화 (권장)
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    Windows (PowerShell):
    $env:OCPP_PROTOCOL_DEBUG = 'true'
    python demo.py
    
    Windows (Command Prompt):
    set OCPP_PROTOCOL_DEBUG=true
    python demo.py
    
    Linux/Mac:
    export OCPP_PROTOCOL_DEBUG=true
    python demo.py
    
    
    2️⃣  로그 파일에 저장
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    $env:OCPP_PROTOCOL_DEBUG = 'true'
    $env:OCPP_LOG_FILE = 'ocpp_debug.log'
    python demo.py
    
    
    3️⃣  Python 코드에서 설정
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    from logging_config import setup_logging
    
    # 프로토콜 디버그 활성화
    setup_logging(enable_protocol_debug=True)
    
    # 또는 파일에 저장
    setup_logging(enable_protocol_debug=True, log_file='ocpp.log')
    
    
    프로토콜 로그 태그
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    [OCPP-CALL-SEND]        Call 메시지 전송
    [OCPP-PAYLOAD-SEND]     전송 페이로드
    [OCPP-CALLRESULT-SEND]  CallResult 전송
    [OCPP-RESPONSE-SEND]    응답 페이로드
    [OCPP-CALLERROR-SEND]   오류 메시지 전송
    [OCPP-ERROR-SEND]       오류 상세 정보
    
    [OCPP-CALL-RECV]        Call 메시지 수신
    [OCPP-PAYLOAD-RECV]     수신 페이로드
    [OCPP-CALLRESULT-RECV]  CallResult 수신
    [OCPP-RESPONSE-RECV]    응답 페이로드
    [OCPP-CALLERROR-RECV]   오류 메시지 수신
    [OCPP-ERROR-RECV]       오류 상세 정보
    [OCPP-RAW-RECV]         원본 메시지
    
    [CHARGER-SEND]          충전기 전송
    [CHARGER-RECV]          충전기 수신
    
    [SERVER-SEND]           서버 전송
    [SERVER-RECV]           서버 수신
    
    
    로그 필터링 예제
    ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    
    # 모든 Call 메시지만 보기 (PowerShell)
    Select-String "OCPP-CALL" ocpp_protocol_debug.log
    
    # TransactionEvent만 (PowerShell)
    Select-String "TransactionEvent" ocpp_protocol_debug.log
    
    # 오류만 (PowerShell)
    Select-String "ERROR" ocpp_protocol_debug.log
    
    
    자세한 가이드는 PROTOCOL_DEBUG_GUIDE.md 파일을 확인하세요.
    """)


if __name__ == "__main__":
    # 도움말 출력
    print_protocol_debug_help()
