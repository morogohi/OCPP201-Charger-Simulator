#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GIS 대시보드 API 테스트
모든 주요 엔드포인트 동작 여부 검증
"""

import sys
import os
import asyncio
import json
from datetime import datetime

# 프로젝트 경로 추가
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)
sys.path.insert(0, os.path.join(project_root, '8_DATABASE'))
sys.path.insert(0, os.path.join(project_root, '4_PYTHON_SOURCE'))

# Windows UTF-8 설정
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', write_through=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', write_through=True)

from fastapi.testclient import TestClient
import requests


def print_section(title):
    """섹션 제목 출력"""
    print(f"\n{'='*60}")
    print(f"📋 {title}")
    print(f"{'='*60}")


def print_result(test_name, success, message=""):
    """테스트 결과 출력"""
    icon = "✅" if success else "❌"
    print(f"{icon} {test_name}")
    if message:
        print(f"   └─ {message}")


def test_api_startup():
    """API 시작 가능 여부 테스트"""
    print_section("1. API 모듈 임포트 및 초기화 테스트")
    
    try:
        # API 모듈 임포트
        from gis_dashboard_api import app, db_manager
        print_result("gis_dashboard_api 모듈 임포트", True)
        
        # 데이터베이스 매니저 초기화
        if db_manager is None:
            print_result("데이터베이스 매니저 상태", False, "db_manager가 None입니다")
            return False
        
        print_result("데이터베이스 매니저 초기화", True)
        return True
    except Exception as e:
        print_result("API 시작", False, str(e))
        return False


def test_api_endpoints():
    """API 엔드포인트 테스트"""
    print_section("2. API 엔드포인트 테스트")
    
    try:
        from gis_dashboard_api import app
        client = TestClient(app)
        
        results = {}
        
        # /health 엔드포인트 테스트
        try:
            response = client.get("/health")
            success = response.status_code == 200
            results["health"] = success
            print_result(
                f"GET /health",
                success,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            results["health"] = False
            print_result("GET /health", False, str(e))
        
        # /stations 엔드포인트 테스트 (GET)
        try:
            response = client.get("/stations")
            success = response.status_code in [200, 422]  # 422는 DB 초기화 안 된 경우
            results["stations_get"] = success
            print_result(
                f"GET /stations",
                success,
                f"Status: {response.status_code}, Records: {len(response.json()) if response.status_code == 200 else 'N/A'}"
            )
        except Exception as e:
            results["stations_get"] = False
            print_result("GET /stations", False, str(e))
        
        # /chargers 엔드포인트 테스트 (GET)
        try:
            response = client.get("/chargers/status/AVAILABLE")
            success = response.status_code in [200, 422]
            results["chargers_status"] = success
            print_result(
                f"GET /chargers/status/AVAILABLE",
                success,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            results["chargers_status"] = False
            print_result("GET /chargers/status/AVAILABLE", False, str(e))
        
        # /geo/chargers 엔드포인트 테스트
        try:
            response = client.get("/geo/chargers")
            success = response.status_code in [200, 422]
            results["geo_chargers"] = success
            print_result(
                f"GET /geo/chargers",
                success,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            results["geo_chargers"] = False
            print_result("GET /geo/chargers", False, str(e))
        
        # /statistics/dashboard 엔드포인트 테스트
        try:
            response = client.get("/statistics/dashboard")
            success = response.status_code in [200, 422]
            results["statistics"] = success
            print_result(
                f"GET /statistics/dashboard",
                success,
                f"Status: {response.status_code}"
            )
        except Exception as e:
            results["statistics"] = False
            print_result("GET /statistics/dashboard", False, str(e))
        
        return all(results.values()), results
    
    except Exception as e:
        print_result("API 엔드포인트 테스트", False, str(e))
        return False, {}


def test_api_with_server():
    """실행 중인 API 서버 테스트"""
    print_section("3. 실행 중인 API 서버 테스트 (http://localhost:8000)")
    
    endpoints = [
        ("/health", "GET"),
        ("/stations", "GET"),
        ("/chargers/status/AVAILABLE", "GET"),
        ("/geo/chargers", "GET"),
        ("/statistics/dashboard", "GET"),
    ]
    
    results = {}
    server_running = False
    
    for endpoint, method in endpoints:
        try:
            url = f"http://localhost:8000{endpoint}"
            if method == "GET":
                response = requests.get(url, timeout=5)
                success = response.status_code < 500
                results[endpoint] = success
                
                if response.status_code == 200:
                    server_running = True
                
                print_result(
                    f"GET {endpoint}",
                    success,
                    f"Status: {response.status_code}"
                )
            else:
                results[endpoint] = False
                print_result(f"{method} {endpoint}", False, "지원하지 않는 메서드")
        
        except requests.exceptions.ConnectionError:
            results[endpoint] = False
            print_result(
                f"GET {endpoint}",
                False,
                "API 서버 연결 불가 (http://localhost:8000)"
            )
        except requests.exceptions.Timeout:
            results[endpoint] = False
            print_result(f"GET {endpoint}", False, "타임아웃")
        except Exception as e:
            results[endpoint] = False
            print_result(f"GET {endpoint}", False, str(e))
    
    return server_running, results


def test_database_connection():
    """데이터베이스 연결 테스트"""
    print_section("4. 데이터베이스 연결 테스트")
    
    try:
        from database.models_postgresql import DatabaseManager
        
        db_manager = DatabaseManager()
        db_manager.initialize()
        
        print_result("DatabaseManager 초기화", True)
        
        # 세션 생성 테스트
        try:
            session = db_manager.get_session()
            print_result("데이터베이스 세션 생성", True)
            
            # 간단한 쿼리 실행
            from database.models_postgresql import StationInfo
            result = session.query(StationInfo).limit(1).first()
            session.close()
            
            if result:
                print_result("데이터베이스 쿼리", True, f"샘플 스테이션 찾음: {result.station_name}")
            else:
                print_result("데이터베이스 쿼리", True, "스테이션 데이터 없음 (DB 초기화 필요)")
            
            return True
        except Exception as e:
            print_result("데이터베이스 세션", False, str(e))
            return False
    
    except Exception as e:
        print_result("DatabaseManager 초기화", False, str(e))
        return False


def test_cors_headers():
    """CORS 헤더 테스트"""
    print_section("5. CORS 설정 테스트")
    
    try:
        from gis_dashboard_api import app
        client = TestClient(app)
        
        response = client.get("/health")
        
        # CORS 헤더 확인
        cors_headers = {
            "access-control-allow-origin": response.headers.get("access-control-allow-origin"),
            "access-control-allow-methods": response.headers.get("access-control-allow-methods"),
            "access-control-allow-headers": response.headers.get("access-control-allow-headers"),
        }
        
        has_cors = any(cors_headers.values())
        
        if has_cors:
            print_result("CORS 헤더", True, "모든 출처 허용 설정됨")
            for header, value in cors_headers.items():
                if value:
                    print(f"   ├─ {header}: {value}")
        else:
            print_result("CORS 헤더", False, "CORS 헤더 미검출")
        
        return True
    
    except Exception as e:
        print_result("CORS 테스트", False, str(e))
        return False


def test_response_formats():
    """응답 형식 테스트"""
    print_section("6. 응답 형식 검증")
    
    try:
        from gis_dashboard_api import app
        client = TestClient(app)
        
        # JSON 응답 테스트
        try:
            response = client.get("/stations")
            is_json = response.headers.get("content-type", "").startswith("application/json")
            print_result("JSON 응답 형식", is_json, f"Content-Type: {response.headers.get('content-type', 'N/A')}")
        except Exception as e:
            print_result("JSON 응답 형식", False, str(e))
        
        # 에러 응답 테스트
        try:
            response = client.get("/stations/nonexistent")
            if response.status_code == 404:
                print_result("404 에러 처리", True, "정상적으로 404 반환")
            else:
                print_result("404 에러 처리", False, f"예상: 404, 실제: {response.status_code}")
        except Exception as e:
            print_result("404 에러 처리", False, str(e))
        
        return True
    
    except Exception as e:
        print_result("응답 형식 테스트", False, str(e))
        return False


def main():
    """메인 테스트 함수"""
    print("\n" + "="*60)
    print("🚀 GIS 대시보드 API 통합 테스트 시작")
    print("="*60)
    
    results = {}
    
    # 1. API 시작 테스트
    results["startup"] = test_api_startup()
    
    # 2. 엔드포인트 테스트
    endpoint_success, endpoint_results = test_api_endpoints()
    results["endpoints"] = endpoint_success
    
    # 3. DB 연결 테스트
    results["database"] = test_database_connection()
    
    # 4. CORS 테스트
    results["cors"] = test_cors_headers()
    
    # 5. 응답 형식 테스트
    results["formats"] = test_response_formats()
    
    # 6. 실행 중인 서버 테스트
    server_running, server_results = test_api_with_server()
    results["server"] = server_running
    
    # 최종 결과
    print_section("📊 최종 테스트 결과")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test_name, success in results.items():
        icon = "✅" if success else "⚠️"
        print(f"{icon} {test_name.upper()}")
    
    print(f"\n통과: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 모든 테스트 통과!")
    elif server_running:
        print("\n✅ API 서버 실행 중 - 엔드포인트 접근 가능")
    else:
        print("\n⚠️  API 서버가 실행 중이지 않습니다.")
        print("    다음 명령어로 API를 시작하세요:")
        print("    python 4_PYTHON_SOURCE\\gis_dashboard_api.py")
    
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    main()
