#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
실행 중인 API 서버 테스트 스크립트
"""

import sys
import os
import time
import requests
from datetime import datetime

# Windows UTF-8 설정
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', write_through=True)
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', write_through=True)


def print_section(title):
    """섹션 제목 출력"""
    print(f"\n{'='*70}")
    print(f"📋 {title}")
    print(f"{'='*70}")


def test_endpoint(method, endpoint, description=""):
    """엔드포인트 테스트"""
    url = f"http://localhost:8000{endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        else:
            response = requests.post(url, timeout=5)
        
        status_code = response.status_code
        is_success = status_code < 400
        
        icon = "✅" if is_success else "⚠️"
        
        print(f"\n{icon} {method} {endpoint}")
        print(f"   Status: {status_code}")
        
        if description:
            print(f"   설명: {description}")
        
        # 응답 크기 표시
        try:
            json_data = response.json()
            if isinstance(json_data, list):
                print(f"   응답: {len(json_data)} 개의 항목")
                if len(json_data) > 0:
                    print(f"   첫 번째 항목 키: {list(json_data[0].keys())[:5]}")
            elif isinstance(json_data, dict):
                print(f"   응답 키: {list(json_data.keys())[:5]}")
            else:
                print(f"   응답 타입: {type(json_data).__name__}")
        except:
            print(f"   응답 길이: {len(response.text)} bytes")
        
        return is_success
    
    except requests.exceptions.ConnectionError as e:
        print(f"❌ {method} {endpoint}")
        print(f"   에러: 서버 연결 불가")
        return False
    except requests.exceptions.Timeout:
        print(f"❌ {method} {endpoint}")
        print(f"   에러: 타임아웃")
        return False
    except Exception as e:
        print(f"❌ {method} {endpoint}")
        print(f"   에러: {str(e)}")
        return False


def main():
    """메인 테스트 함수"""
    print("\n" + "="*70)
    print("🚀 GIS 대시보드 API 실행 중인 서버 테스트")
    print(f"   시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # 테스트 대기
    print("\n⏳ API 서버 준비 대기 중 (2초)...")
    time.sleep(2)
    
    # 기본 헬스 체크
    print_section("1. 기본 헬스 체크")
    test_endpoint("GET", "/health", "API 서버 상태 확인")
    
    # 충전소 관련 엔드포인트
    print_section("2. 충전소(Station) 엔드포인트")
    test_endpoint("GET", "/stations", "모든 충전소 조회")
    test_endpoint("GET", "/stations/1", "특정 충전소 조회")
    
    # 충전기 관련 엔드포인트
    print_section("3. 충전기(Charger) 엔드포인트")
    test_endpoint("GET", "/chargers/status/AVAILABLE", "이용 가능한 충전기 조회")
    test_endpoint("GET", "/chargers/status/IN_USE", "사용 중인 충전기 조회")
    test_endpoint("GET", "/chargers/status/FAULT", "고장난 충전기 조회")
    
    # GIS 관련 엔드포인트
    print_section("4. GIS 지도 관련 엔드포인트")
    test_endpoint("GET", "/geo/chargers", "모든 충전기의 지리 정보")
    test_endpoint("GET", "/geo/heatmap", "사용 현황 히트맵 데이터")
    
    # 통계 관련 엔드포인트
    print_section("5. 통계 관련 엔드포인트")
    test_endpoint("GET", "/statistics/dashboard", "대시보드 통계")
    test_endpoint("GET", "/statistics/charger/1/daily", "충전기 일일 통계")
    
    print_section("6. 최종 결과")
    print("\n✅ API 서버 테스트 완료")
    print("\n다음 URL로 대시보드에 접속할 수 있습니다:")
    print("   📊 GIS 대시보드: http://localhost:8000")
    print("   📋 API 문서: http://localhost:8000/docs")
    print("   🔧 ReDoc: http://localhost:8000/redoc")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
