import threading
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from .state import STATE
from .database import EventStore
from .detector import DetectionEngine
from .camera import mjpeg_generator, websocket_loop
from .schemas import ZoneUpdate, SettingsUpdate

app = FastAPI(
    title="AI Surveillance & Safety API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

store = EventStore()
engine = DetectionEngine(store)
thread = None

@app.on_event("startup")
def startup():
    global thread
    thread = threading.Thread(target=engine.run, daemon=True)
    thread.start()

@app.on_event("shutdown")
def shutdown():
    STATE.running = False

@app.get("/api/health")
def health():
    return {"status": "ok", "database": store.mode}

@app.get("/api/stats")
def stats():
    return STATE.snapshot()

@app.get("/api/events")
def events(limit: int = 50):
    return store.list(limit)

@app.delete("/api/events")
def clear_events():
    store.clear()
    return {"message": "Events cleared"}

@app.get("/api/settings")
def settings():
    return {
        "crowd_threshold": STATE.crowd_threshold,
        "confidence": STATE.confidence,
        "zone": STATE.zone,
    }

@app.put("/api/settings")
def update_settings(payload: SettingsUpdate):
    STATE.crowd_threshold = payload.crowd_threshold
    STATE.confidence = payload.confidence
    return {
        "crowd_threshold": STATE.crowd_threshold,
        "confidence": STATE.confidence,
    }

@app.put("/api/zone")
def update_zone(payload: ZoneUpdate):
    if payload.x2 <= payload.x1 or payload.y2 <= payload.y1:
        return {"error": "x2 must be greater than x1 and y2 greater than y1"}
    STATE.zone = payload.model_dump()
    return {"zone": STATE.zone}

@app.get("/video_feed")
def video_feed():
    return StreamingResponse(
        mjpeg_generator(STATE),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_loop(websocket, STATE)
