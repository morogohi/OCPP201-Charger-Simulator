#!/usr/bin/env python3
"""Run server and test together"""

import asyncio
import subprocess
import time
import sys

async def main():
    """Run server in subprocess and test in main process"""
    # Start server in subprocess
    print("Starting server...")
    server_process = subprocess.Popen(
        [sys.executable, "ocpp_server.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )
    
    # Wait for server to start
    print("Waiting for server to start...")
    time.sleep(2)
    
    # Run test
    print("\nRunning test...")
    test_process = subprocess.run(
        [sys.executable, "final_test.py"],
        capture_output=True,
        text=True
    )
    
    print(test_process.stdout)
    if test_process.stderr:
        print("Errors:", test_process.stderr)
    
    # Stop server
    print("\nStopping server...")
    server_process.terminate()
    server_process.wait(timeout=5)
    
    print("Done!")

if __name__ == "__main__":
    asyncio.run(main())
