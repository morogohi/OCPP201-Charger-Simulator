"""
OCPP 서버 REST API (관리 및 모니터링용)
"""
from aiohttp import web
import asyncio
import logging
from ocpp_server import OCPPServer

logger = logging.getLogger(__name__)


class ServerAPI:
    """OCPP 서버 REST API"""

    def __init__(self, ocpp_server: OCPPServer, api_port: int = 8080):
        self.ocpp_server = ocpp_server
        self.api_port = api_port
        self.app = web.Application()
        self.setup_routes()

    def setup_routes(self):
        """라우트 설정"""
        self.app.router.add_get('/chargers', self.get_chargers)
        self.app.router.add_get('/chargers/{charger_id}', self.get_charger)
        self.app.router.add_post('/chargers/{charger_id}/start', self.start_transaction)
        self.app.router.add_post('/chargers/{charger_id}/stop', self.stop_transaction)
        self.app.router.add_get('/health', self.health_check)

    async def get_chargers(self, request):
        """모든 충전기 조회"""
        try:
            status = self.ocpp_server.get_charger_status()
            return web.json_response(status)
        except Exception as e:
            logger.error(f"충전기 목록 조회 실패: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def get_charger(self, request):
        """특정 충전기 조회"""
        charger_id = request.match_info['charger_id']
        try:
            status = self.ocpp_server.get_charger_status(charger_id)
            if "error" in status:
                return web.json_response(status, status=404)
            return web.json_response(status)
        except Exception as e:
            logger.error(f"충전기 조회 실패: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def start_transaction(self, request):
        """거래 시작"""
        charger_id = request.match_info['charger_id']
        try:
            data = await request.json()
            evse_id = data.get('evse_id', 1)
            connector_id = data.get('connector_id', 1)
            
            success = await self.ocpp_server.request_start_transaction(
                charger_id, evse_id, connector_id
            )
            
            if success:
                return web.json_response({"status": "success"})
            else:
                return web.json_response({"error": "Failed to start transaction"}, status=400)
        except Exception as e:
            logger.error(f"거래 시작 실패: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def stop_transaction(self, request):
        """거래 중지"""
        charger_id = request.match_info['charger_id']
        try:
            data = await request.json()
            transaction_id = data.get('transaction_id')
            
            success = await self.ocpp_server.request_stop_transaction(
                charger_id, transaction_id
            )
            
            if success:
                return web.json_response({"status": "success"})
            else:
                return web.json_response({"error": "Failed to stop transaction"}, status=400)
        except Exception as e:
            logger.error(f"거래 중지 실패: {e}")
            return web.json_response({"error": str(e)}, status=500)

    async def health_check(self, request):
        """헬스 체크"""
        return web.json_response({"status": "healthy"})

    async def start(self):
        """API 서버 시작"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner, '0.0.0.0', self.api_port)
        await site.start()
        logger.info(f"REST API 서버 시작: http://0.0.0.0:{self.api_port}")


async def run_server_with_api():
    """OCPP 서버와 REST API 동시 실행"""
    ocpp_server = OCPPServer(host="0.0.0.0", port=9000)
    api = ServerAPI(ocpp_server, api_port=8080)
    ocpp_task = asyncio.create_task(ocpp_server.start())
    api_task = asyncio.create_task(api.start())

    try:
        await asyncio.gather(ocpp_task, api_task)
    except (asyncio.CancelledError, KeyboardInterrupt):
        logger.info("종료 신호 수신, 서버 정리 중...")
        ocpp_server.shutdown_event.set()
    finally:
        # 웹소켓 서버를 멈추게 하기 위해 종료 이벤트 설정
        ocpp_server.shutdown_event.set()
        for task in (ocpp_task, api_task):
            if not task.done():
                task.cancel()


if __name__ == "__main__":
    asyncio.run(run_server_with_api())
