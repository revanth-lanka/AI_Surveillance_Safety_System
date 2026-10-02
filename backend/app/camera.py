import time
from fastapi import WebSocket

def mjpeg_generator(state):
    while True:
        with state.lock:
            frame = state.latest_jpeg
            running = state.running

        if frame:
            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" +
                frame +
                b"\r\n"
            )
        elif not running:
            break
        time.sleep(0.04)

async def websocket_loop(websocket: WebSocket, state):
    await websocket.accept()
    try:
        while True:
            await websocket.send_json(state.snapshot())
            await __import__("asyncio").sleep(0.5)
    except Exception:
        return
