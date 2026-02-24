import asyncio
import logging
import os
import json
import cv2
from aiohttp import web, WSMsgType

# Cloud / Local configuration
PORT = int(os.environ.get("PORT", 10000))
HOST = "0.0.0.0"

logging.basicConfig(level=logging.INFO, format="%(message)s")
log = logging.getLogger("WSServer")


class WSServer:
    def __init__(self):
        self.clients = set()
        self.cap = cv2.VideoCapture(0)  # USB Camera

        if not self.cap.isOpened():
            log.error("❌ Could not open USB camera")
        else:
            log.info("📷 USB Camera initialized")

    # =========================
    # WebSocket Handler
    # =========================
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

    # =========================
    # Health Check
    # =========================
    async def health_check(self, request):
        return web.json_response({
            "status": "healthy",
            "clients": len(self.clients),
            "service": "gesture-control-backend-camera"
        })

    # =========================
    # Video Stream (MJPEG)
    # =========================
    async def video_feed(self, request):
        async def stream():
            while True:
                ret, frame = self.cap.read()
                if not ret:
                    continue

                _, jpeg = cv2.imencode('.jpg', frame)
                frame_bytes = jpeg.tobytes()

                yield (
                    b'--frame\r\n'
                    b'Content-Type: image/jpeg\r\n\r\n' +
                    frame_bytes +
                    b'\r\n'
                )

                await asyncio.sleep(0.03)  # ~30 FPS

        return web.Response(
            body=stream(),
            headers={
                'Content-Type': 'multipart/x-mixed-replace; boundary=frame'
            }
        )


# =========================
# Main App
# =========================
async def main():
    server = WSServer()

    app = web.Application()

    # Routes
    app.router.add_get("/", lambda r: web.Response(text="Gesture Control Backend Running"))
    app.router.add_get("/health", server.health_check)
    app.router.add_get("/ws", server.websocket_handler)
    app.router.add_get("/video_feed", server.video_feed)

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