"""
프로젝트 경로 설정
모든 Python 스크립트가 올바르게 모듈을 import할 수 있도록 함
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트 경로
PROJECT_ROOT = Path(__file__).parent.absolute()

# sys.path에 필수 경로 추가
PATHS_TO_ADD = [
    str(PROJECT_ROOT),
    str(PROJECT_ROOT / '4_PYTHON_SOURCE'),
    str(PROJECT_ROOT / '8_DATABASE'),
]

for path in PATHS_TO_ADD:
    if path not in sys.path:
        sys.path.insert(0, path)

# 환경 변수 기본값 설정
if 'DATABASE_URL' not in os.environ:
    os.environ['DATABASE_URL'] = 'postgresql://charger_user:admin@localhost:5432/charger_db'

if 'OCPP_PROTOCOL_DEBUG' not in os.environ:
    os.environ['OCPP_PROTOCOL_DEBUG'] = 'false'
