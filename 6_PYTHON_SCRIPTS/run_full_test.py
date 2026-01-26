#!/usr/bin/env python3
"""Run OCPP server and test together"""

import asyncio
import subprocess
import time
import sys

async def main():
    """Run server in subprocess and test in main process"""
    # Start server in subprocess
    print("Starting OCPP server...")
    server_process = subprocess.Popen(
        [sys.executable, "ocpp_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Wait for server to start
    print("Waiting for server to start...")
    time.sleep(3)
    
    # Run test scenario 1
    print("\n" + "="*80)
    print("Running test scenario 1...")
    print("="*80 + "\n")
    test_process = subprocess.run(
        [sys.executable, "test_csharp_integration.py", "1"],
        capture_output=True,
        text=True
    )
    
    print(test_process.stdout)
    if test_process.stderr:
        print("Errors:", test_process.stderr)
    
    # Stop server
    print("\nStopping server...")
    server_process.terminate()
    try:
        server_process.wait(timeout=5)
    except subprocess.TimeoutExpired:
        server_process.kill()
        server_process.wait()
    
    print("Test completed!")

if __name__ == "__main__":
    asyncio.run(main())
