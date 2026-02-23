import asyncio
import logging
import os
import json
from aiohttp import web, WSMsgType

# Cloud deployment configuration
PORT = int(os.environ.get("PORT", 10000))
HOST = "0.0.0.0"

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("WSServer")


class WSServer:
    def __init__(self):
        self.clients = set()

    async def websocket_handler(self, request):
        ws = web.WebSocketResponse()
        await ws.prepare(request)

        self.clients.add(ws)
        log.info("✅ Client connected")

        try:
            async for msg in ws:
                if msg.type == WSMsgType.TEXT:
                    log.info(f"📩 Received: {msg.data}")

                    # Broadcast to all other clients
                    for client in list(self.clients):
                        if client != ws:
                            await client.send_str(msg.data)

                elif msg.type == WSMsgType.ERROR:
                    log.error(f"❌ WebSocket error: {ws.exception()}")

        finally:
            self.clients.remove(ws)
            log.info("❌ Client disconnected")

        return ws

    async def health_check(self, request):
        return web.json_response({
            "status": "healthy",
            "clients": len(self.clients),
            "service": "gesture-control-backend-camera"
        })


async def main():
    server = WSServer()

    app = web.Application()

    # Routes
    app.router.add_get("/", lambda r: web.Response(text="Gesture Control Backend Running"))
    app.router.add_get("/health", server.health_check)
    app.router.add_get("/ws", server.websocket_handler)

    log.info(f"🚀 Starting server on {HOST}:{PORT}")

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, HOST, PORT)
    await site.start()

    # Run forever
    while True:
        await asyncio.sleep(3600)


if __name__ == "__main__":
    asyncio.run(main())