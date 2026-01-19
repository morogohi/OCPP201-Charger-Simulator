"""
OCPP 2.0.1 완전 시스템 데모
서버와 충전기를 함께 실행하고 테스트합니다.
"""
import asyncio
import logging
from ocpp_server import OCPPServer
from charger_simulator import ChargerSimulator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def main():
    """메인 데모 함수"""
    
    # 서버 생성 및 시작
    server = OCPPServer(host="localhost", port=9000)
    server_task = asyncio.create_task(server.start())
    
    # 서버가 시작될 때까지 대기
    await asyncio.sleep(1)
    
    logger.info("=" * 60)
    logger.info("OCPP 2.0.1 충전기 시뮬레이터 및 서버 데모")
    logger.info("=" * 60)
    
    # 3개의 충전기 생성
    chargers = [
        ChargerSimulator(
            charger_id=f"charger_{i:03d}",
            server_url="ws://localhost:9000",
            charger_model="EVBox Home" if i % 2 == 0 else "Tesla Supercharger",
            charger_vendor="EVBox" if i % 2 == 0 else "Tesla"
        )
        for i in range(1, 4)
    ]
    
    try:
        # 모든 충전기 연결
        logger.info("\n[1단계] 충전기 연결 중...")
        for charger in chargers:
            try:
                await charger.connect()
            except Exception as e:
                logger.error(f"충전기 연결 실패: {e}")
        
        # 부팅 알림 수신 대기
        await asyncio.sleep(3)
        
        logger.info(f"\n[2단계] 현재 연결된 충전기: {len(server.chargers)}")
        for charger_id, charger in server.chargers.items():
            logger.info(f"  - {charger_id}: Boot={charger.boot_status}, Connected={charger.connected}")
        
        # 첫 번째 충전기에서 거래 시작
        logger.info("\n[3단계] 첫 번째 충전기 거래 시작...")
        first_charger_id = f"charger_001"
        await server.request_start_transaction(first_charger_id, evse_id=1, connector_id=1)
        
        await asyncio.sleep(3)
        
        # 거래 상태 확인
        logger.info(f"\n[4단계] 거래 상태 확인...")
        chargers[0].is_charging = True
        logger.info(f"  - {first_charger_id}: 충전 중 (에너지: {chargers[0].meter_value:.2f} kWh)")
        
        await asyncio.sleep(5)
        
        # 거래 중지
        logger.info(f"\n[5단계] 거래 중지...")
        await server.request_stop_transaction(first_charger_id)
        chargers[0].is_charging = False
        
        await asyncio.sleep(2)
        
        # 최종 상태
        logger.info(f"\n[6단계] 최종 상태:")
        for charger_id, charger in server.chargers.items():
            logger.info(f"  - {charger_id}: 연결됨={charger.connected}")
        
        logger.info("\n" + "=" * 60)
        logger.info("데모 완료!")
        logger.info("=" * 60)
        
    except KeyboardInterrupt:
        logger.info("\n사용자가 중단함")
    
    except Exception as e:
        logger.error(f"오류 발생: {e}", exc_info=True)
    
    finally:
        logger.info("\n정리 중...")
        for charger in chargers:
            await charger.disconnect()
        logger.info("프로그램 종료")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("프로그램 중단됨")
