"""
충전기 시뮬레이터 테스트
"""
import asyncio
import logging
from charger_simulator import ChargerSimulator

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_single_charger():
    """단일 충전기 테스트"""
    charger = ChargerSimulator(
        charger_id="charger_001",
        server_url="ws://localhost:9000",
        charger_model="EVBox Home",
        charger_vendor="EVBox"
    )
    
    try:
        await charger.connect()
        
        # 10초 대기
        for i in range(10):
            await asyncio.sleep(1)
            logger.info(f"실행 중... ({i+1}초)")
        
        # 충전 시뮬레이션 시작
        charger.is_charging = True
        logger.info("충전 시뮬레이션 시작")
        
        for i in range(10):
            await asyncio.sleep(1)
            logger.info(f"충전 중... (에너지: {charger.meter_value:.2f} kWh)")
        
        # 충전 종료
        charger.is_charging = False
        logger.info("충전 시뮬레이션 종료")
        
        await asyncio.sleep(5)
        
    except Exception as e:
        logger.error(f"테스트 실패: {e}")
    finally:
        await charger.disconnect()


async def test_multiple_chargers():
    """다중 충전기 테스트"""
    chargers = [
        ChargerSimulator(
            charger_id=f"charger_{i:03d}",
            server_url="ws://localhost:9000",
            charger_model="EVBox Home",
            charger_vendor="EVBox"
        )
        for i in range(3)
    ]
    
    try:
        # 모든 충전기 연결
        for charger in chargers:
            await charger.connect()
        
        # 30초 실행
        for i in range(30):
            await asyncio.sleep(1)
            logger.info(f"실행 중... ({i+1}초)")
        
    except Exception as e:
        logger.error(f"테스트 실패: {e}")
    finally:
        for charger in chargers:
            await charger.disconnect()


async def main():
    """메인 테스트"""
    logger.info("충전기 시뮬레이터 테스트 시작")
    
    # 단일 충전기 테스트
    logger.info("=== 단일 충전기 테스트 ===")
    await test_single_charger()
    
    # 잠깐 대기
    await asyncio.sleep(2)
    
    # 다중 충전기 테스트
    logger.info("=== 다중 충전기 테스트 ===")
    await test_multiple_chargers()
    
    logger.info("테스트 완료")


if __name__ == "__main__":
    asyncio.run(main())
