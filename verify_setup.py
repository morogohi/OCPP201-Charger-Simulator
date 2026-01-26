#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
프로젝트 오류 검사 및 검증
"""

import sys
import os
from pathlib import Path

# Windows 환경에서 UTF-8 설정
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 경로 설정
project_root = str(Path(__file__).parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, '8_DATABASE'))
sys.path.insert(0, os.path.join(project_root, '4_PYTHON_SOURCE'))

def check_imports():
    """모든 모듈 import 체크"""
    
    tests = [
        ("database.models_postgresql", ["DatabaseManager", "ChargerTypeEnum", "ChargerStatusEnum"]),
        ("database.services", ["StationService", "ChargerService", "UsageLogService"]),
        ("database.models", ["StationInfo", "ChargerInfo"]),
        ("ocpp_messages", ["OCPPMessage", "OCPPv201RequestBuilder"]),
        ("ocpp_models", ["BootReasonEnum", "GenericStatusEnum"]),
        ("ocpp_server", ["OCPPServer"]),
        ("charger_simulator", ["ChargerSimulator"]),
        # gis_dashboard_api는 FastAPI 앱 시작 시 stdout을 변경하므로 skip
    ]
    
    print("=" * 70)
    print("프로젝트 오류 검사 (모듈 import)")
    print("=" * 70)
    print()
    
    passed = 0
    failed = 0
    
    for module_name, items in tests:
        try:
            module = __import__(module_name, fromlist=items)
            for item in items:
                if not hasattr(module, item):
                    print(f"[FAIL] {module_name}.{item} - 속성 없음")
                    failed += 1
                else:
                    print(f"[PASS] {module_name}.{item}")
                    passed += 1
        except ImportError as e:
            print(f"[FAIL] {module_name} - {str(e)}")
            failed += 1
        except Exception as e:
            print(f"[FAIL] {module_name} - {str(e)}")
            failed += 1
    
    print()
    print("=" * 70)
    print(f"결과: {passed} 성공 / {failed} 실패")
    print("=" * 70)
    
    return failed == 0

def check_file_structure():
    """파일 구조 체크"""
    
    print()
    print("=" * 70)
    print("파일 구조 검사")
    print("=" * 70)
    print()
    
    required_files = [
        "4_PYTHON_SOURCE/ocpp_server.py",
        "4_PYTHON_SOURCE/ocpp_messages.py",
        "4_PYTHON_SOURCE/ocpp_models.py",
        "4_PYTHON_SOURCE/charger_simulator.py",
        "4_PYTHON_SOURCE/gis_dashboard_api.py",
        "8_DATABASE/database/__init__.py",
        "8_DATABASE/database/models_postgresql.py",
        "8_DATABASE/database/models.py",
        "8_DATABASE/database/services.py",
        "6_PYTHON_SCRIPTS/init_jeju_chargers.py",
    ]
    
    passed = 0
    failed = 0
    
    for filepath in required_files:
        full_path = os.path.join(project_root, filepath)
        if os.path.exists(full_path):
            print(f"[PASS] {filepath}")
            passed += 1
        else:
            print(f"[FAIL] {filepath} - 파일 없음")
            failed += 1
    
    print()
    print("=" * 70)
    print(f"결과: {passed} 파일 존재 / {failed} 파일 부재")
    print("=" * 70)
    
    return failed == 0

if __name__ == "__main__":
    result1 = check_imports()
    result2 = check_file_structure()
    
    print()
    print("=" * 70)
    if result1 and result2:
        print("✅ 모든 검사 통과!")
        sys.exit(0)
    else:
        print("❌ 일부 검사 실패")
        sys.exit(1)
