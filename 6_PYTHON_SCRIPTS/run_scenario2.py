#!/usr/bin/env python3
"""Run server and test scenario 2"""

import asyncio
import subprocess
import time
import sys

async def main():
    """Run server and test scenario 2"""
    # Start server
    print("="*80)
    print("OCPP 2.0.1 서버 및 테스트 시나리오 2 실행")
    print("="*80)
    print("\n[1] 서버 시작 중...")
    
    server = subprocess.Popen(
        [sys.executable, "ocpp_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Wait for server to start
    print("[2] 서버 준비 중...")
    time.sleep(3)
    
    # Run scenario 2
    print("\n[3] 시나리오 2 실행 중...\n")
    test = subprocess.run(
        [sys.executable, "test_csharp_integration.py", "2"],
        capture_output=True,
        text=True,
        timeout=60
    )
    
    print(test.stdout)
    if test.stderr:
        # Filter out deprecation warnings
        for line in test.stderr.split('\n'):
            if 'DeprecationWarning' not in line and line.strip():
                print(f"[ERROR] {line}")
    
    # Stop server
    print("\n[4] 서버 종료 중...")
    server.terminate()
    try:
        server.wait(timeout=5)
    except subprocess.TimeoutExpired:
        server.kill()
        server.wait()
    
    print("\n" + "="*80)
    print("테스트 완료!")
    print("="*80)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
