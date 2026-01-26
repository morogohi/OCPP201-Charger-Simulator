#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
간단한 테스트 API 서버
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI(title="Test API")

@app.get("/")
async def root():
    return {"message": "API Server is running!"}

@app.get("/health")
async def health():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=5000, log_level="info")
