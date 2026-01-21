#!/usr/bin/env python3
"""Run all OCPP tests"""

import asyncio
import subprocess
import time
import sys

async def main():
    """Run server and all tests"""
    # Start server
    print("Starting OCPP server...")
    server_process = subprocess.Popen(
        [sys.executable, "ocpp_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Wait for server
    print("Waiting for server to start...")
    time.sleep(3)
    
    # Run all scenarios
    for scenario in ["1", "2", "3"]:
        print("\n" + "="*80)
        print(f"Running scenario {scenario}...")
        print("="*80 + "\n")
        
        test_process = subprocess.run(
            [sys.executable, "test_csharp_integration.py", scenario],
            capture_output=True,
            text=True,
            timeout=60
        )
        
        print(test_process.stdout)
        if test_process.stderr:
            print("Errors:", test_process.stderr)
        
        time.sleep(2)
    
    # Stop server
    print("\nStopping server...")
    server_process.terminate()
    try:
        server_process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        server_process.kill()
        server_process.wait()
    
    print("\nAll tests completed!")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except Exception as e:
        print(f"Error: {e}")
