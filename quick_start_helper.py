#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCPP 2.0.1 통합 시스템 실행 헬퍼
PowerShell/CMD 없이 Python으로 직접 실행합니다.
"""

import sys
import os
import subprocess
from pathlib import Path

# Windows 한글 인코딩 설정
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', write_through=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', write_through=True)

def print_header(text):
    """헤더 출력"""
    print("\n" + "=" * 80)
    print(text.center(80))
    print("=" * 80 + "\n")

def print_step(num, text):
    """단계 출력"""
    print(f"[{num}/5] {text}")

def print_success(text):
    """성공 메시지"""
    print(f"✅ {text}")

def print_error(text):
    """오류 메시지"""
    print(f"❌ {text}")

def print_info(text):
    """정보 메시지"""
    print(f"ℹ️  {text}")

def main():
    print_header("OCPP 2.0.1 통합 시스템 실행 헬퍼")
    
    # 1단계: 경로 확인
    print_step(1, "프로젝트 경로 확인")
    project_root = Path(__file__).parent.absolute()
    print(f"  경로: {project_root}")
    
    # 프로젝트 폴더에 있는지 확인
    if not (project_root / "4_PYTHON_SOURCE").exists():
        print_error("4_PYTHON_SOURCE 폴더를 찾을 수 없습니다")
        print_info("이 스크립트를 프로젝트 루트에서 실행하세요:")
        print(f"  cd {project_root}")
        return False
    
    print_success("프로젝트 폴더 확인됨")
    
    # 2단계: 가상환경 확인
    print_step(2, "가상환경 확인")
    venv_path = project_root / ".venv" / "Scripts" / "python.exe"
    
    if not venv_path.exists():
        print_error("가상환경을 찾을 수 없습니다")
        print_info("생성 중...")
        try:
            subprocess.run([sys.executable, "-m", "venv", ".venv"], cwd=project_root, check=True)
            print_success("가상환경 생성 완료")
        except Exception as e:
            print_error(f"가상환경 생성 실패: {e}")
            return False
    else:
        print_success("가상환경 확인됨")
    
    # 3단계: 환경변수 설정
    print_step(3, "환경변수 설정")
    os.environ['DATABASE_URL'] = 'postgresql://charger_user:admin@localhost:5432/charger_db'
    os.environ['OCPP_PROTOCOL_DEBUG'] = 'false'
    print_success("DATABASE_URL 설정됨")
    print_success("OCPP_PROTOCOL_DEBUG 설정됨")
    
    # 4단계: 설정 검증
    print_step(4, "설정 검증")
    sys.path.insert(0, str(project_root / '8_DATABASE'))
    sys.path.insert(0, str(project_root / '4_PYTHON_SOURCE'))
    
    try:
        from database.models_postgresql import DatabaseManager
        from database.services import ChargerService
        from ocpp_messages import OCPPMessage
        from ocpp_server import OCPPServer
        from charger_simulator import ChargerSimulator
        
        print_success("모든 모듈 import 성공")
        
        # 데이터베이스 연결 테스트
        try:
            db = DatabaseManager()
            db.initialize()
            session = db.get_session()
            
            # 현재 존재하는 충전기 수 조회
            from sqlalchemy import text
            result = session.execute(text("SELECT COUNT(*) FROM charger_info"))
            count = result.scalar()
            session.close()
            
            print_success(f"데이터베이스 연결 성공 ({count}개 충전기)")
        except Exception as e:
            print_error(f"데이터베이스 연결 실패: {e}")
            print_info("PostgreSQL이 실행 중인지 확인하세요")
            return False
            
    except ImportError as e:
        print_error(f"모듈 import 실패: {e}")
        return False
    
    # 5단계: 다음 단계 안내
    print_step(5, "실행 방법 안내")
    
    print("\n" + "=" * 80)
    print("✅ 모든 설정이 완료되었습니다!".center(80))
    print("=" * 80)
    
    print("\n다음 명령어로 서비스를 시작할 수 있습니다:\n")
    
    print("[Terminal 1] OCPP 서버 (Port 9000):")
    print("  python 4_PYTHON_SOURCE\\ocpp_server.py")
    print()
    
    print("[Terminal 2] GIS 대시보드 (Port 8000):")
    print("  python 4_PYTHON_SOURCE\\gis_dashboard_api.py")
    print()
    
    print("[Terminal 3] Python 시뮬레이터:")
    print("  python 6_PYTHON_SCRIPTS\\test_simulator.py")
    print()
    print("  또는:")
    print("  python -c \"")
    print("import asyncio, sys")
    print("sys.path.insert(0, '4_PYTHON_SOURCE')")
    print("sys.path.insert(0, '8_DATABASE')")
    print("from charger_simulator import ChargerSimulator")
    print()
    print("async def main():")
    print("    sim = ChargerSimulator('TEST_001', 'ws://localhost:9000')")
    print("    await sim.connect()")
    print("    await asyncio.sleep(30)")
    print("    await sim.disconnect()")
    print()
    print("asyncio.run(main())")
    print("\"")
    print()
    
    print("[Terminal 4 선택] 실시간 모니터링:")
    print("  python monitor_realtime.py")
    print()
    
    print("[브라우저] GIS 대시보드:")
    print("  http://localhost:8000")
    print()
    
    print("=" * 80)
    print("📖 더 자세한 정보는 다음 파일을 참고하세요:")
    print("=" * 80)
    print("  - QUICK_START_INTEGRATED.md")
    print("  - STEP_BY_STEP_GUIDE.md")
    print("  - 1_GUIDES_SERVER/INTEGRATED_EXECUTION_GUIDE.md")
    print()
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ 실행 중단됨")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
        sys.exit(1)
