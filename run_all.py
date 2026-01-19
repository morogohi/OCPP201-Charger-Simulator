"""
OCPP 서버와 시뮬레이터를 함께 실행하는 스크립트
"""
import asyncio
import logging
import sys
from ocpp_server import OCPPServer
from server_api import ServerAPI
from charger_simulator import ChargerSimulator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def run_all():
    """모든 구성 요소 실행"""
    
    # OCPP 서버 생성
    ocpp_server = OCPPServer(host="0.0.0.0", port=9000)
    
    # REST API 생성
    api = ServerAPI(ocpp_server, api_port=8080)
    
    # 충전기 시뮬레이터들
    chargers = [
        ChargerSimulator(
            charger_id=f"charger_{i:03d}",
            server_url="ws://localhost:9000",
            charger_model="EVBox Home" if i % 2 == 0 else "Tesla Supercharger",
            charger_vendor="EVBox" if i % 2 == 0 else "Tesla"
        )
        for i in range(1, 4)
    ]
    
    async def run_chargers():
        """충전기 시뮬레이터 실행"""
        try:
            # 서버가 준비될 때까지 대기
            await asyncio.sleep(2)
            
            # 모든 충전기 연결
            for charger in chargers:
                try:
                    await charger.connect()
                except Exception as e:
                    logger.error(f"충전기 연결 실패: {e}")
            
            # 시뮬레이터 실행 유지
            while True:
                await asyncio.sleep(1)
        
        except KeyboardInterrupt:
            logger.info("충전기 시뮬레이터 종료 중...")
        finally:
            for charger in chargers:
                await charger.disconnect()
    
    try:
        logger.info("=" * 50)
        logger.info("OCPP 2.0.1 완전 시스템 시작")
        logger.info("=" * 50)
        logger.info("OCPP 서버: ws://localhost:9000")
        logger.info("REST API: http://localhost:8080")
        logger.info("충전기 시뮬레이터: 3대")
        logger.info("=" * 50)
        
        # 모든 구성 요소 동시 실행
        await asyncio.gather(
            ocpp_server.start(),
            api.start(),
            run_chargers(),
            return_exceptions=True
        )
    
    except KeyboardInterrupt:
        logger.info("시스템 종료 중...")


async def run_server_only():
    """서버만 실행"""
    ocpp_server = OCPPServer(host="0.0.0.0", port=9000)
    api = ServerAPI(ocpp_server, api_port=8080)
    
    logger.info("=" * 50)
    logger.info("OCPP 2.0.1 서버 실행 (시뮬레이터 없음)")
    logger.info("=" * 50)
    logger.info("OCPP 서버: ws://localhost:9000")
    logger.info("REST API: http://localhost:8080")
    logger.info("=" * 50)
    
    try:
        await asyncio.gather(
            ocpp_server.start(),
            api.start()
        )
    except KeyboardInterrupt:
        logger.info("서버 종료 중...")


async def run_simulator_only():
    """시뮬레이터만 실행"""
    chargers = [
        ChargerSimulator(
            charger_id=f"charger_{i:03d}",
            server_url="ws://localhost:9000"
        )
        for i in range(1, 4)
    ]
    
    logger.info("=" * 50)
    logger.info("OCPP 2.0.1 충전기 시뮬레이터 실행")
    logger.info("=" * 50)
    logger.info(f"충전기 수: {len(chargers)}")
    logger.info("서버 주소: ws://localhost:9000")
    logger.info("=" * 50)
    
    try:
        for charger in chargers:
            await charger.connect()
        
        while True:
            await asyncio.sleep(1)
    
    except KeyboardInterrupt:
        logger.info("시뮬레이터 종료 중...")
    finally:
        for charger in chargers:
            await charger.disconnect()


def main():
    """메인 함수"""
    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
        if mode == "server":
            asyncio.run(run_server_only())
        elif mode == "charger":
            asyncio.run(run_simulator_only())
        elif mode == "all":
            asyncio.run(run_all())
        else:
            print("Usage: python run_all.py [all|server|charger]")
            print("  all     - 서버와 시뮬레이터 함께 실행 (기본값)")
            print("  server  - 서버만 실행")
            print("  charger - 시뮬레이터만 실행")
    else:
        asyncio.run(run_all())


if __name__ == "__main__":
    main()
