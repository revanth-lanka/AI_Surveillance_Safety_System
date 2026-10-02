import time
import cv2
from ultralytics import YOLO
from .config import MODEL_NAME, CONFIDENCE, CROWD_THRESHOLD, ZONE, CAMERA_INDEX, VIDEO_SOURCE
from .state import STATE

VEHICLES = {"car", "motorcycle", "bus", "truck"}
ALERT_COOLDOWN = 8.0

class DetectionEngine:
    def __init__(self, store):
        self.store = store
        self.model = YOLO(MODEL_NAME)
        STATE.zone = dict(ZONE)
        STATE.crowd_threshold = CROWD_THRESHOLD
        STATE.confidence = CONFIDENCE
        STATE.update_stats(model=MODEL_NAME, status="READY")

    def _source(self):
        return VIDEO_SOURCE if VIDEO_SOURCE else CAMERA_INDEX

    def _should_emit(self, key):
        now = time.time()
        previous = STATE.last_event_times.get(key, 0)
        if now - previous >= ALERT_COOLDOWN:
            STATE.last_event_times[key] = now
            return True
        return False

    def _inside_zone(self, cx, cy):
        z = STATE.zone
        return z["x1"] <= cx <= z["x2"] and z["y1"] <= cy <= z["y2"]

    def _emit(self, event_type, object_type, confidence, message):
        event = {
            "event_type": event_type,
            "object_type": object_type,
            "confidence": round(float(confidence), 3) if confidence is not None else None,
            "message": message,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        self.store.add(event_type, object_type, event["confidence"], message)
        STATE.add_event_memory(event)

    def run(self):
        cap = cv2.VideoCapture(self._source())
        if not cap.isOpened():
            STATE.update_stats(status="CAMERA_ERROR")
            return

        prev = time.time()

        while STATE.running:
            ok, frame = cap.read()
            if not ok:
                if VIDEO_SOURCE:
                    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                    continue
                break

            start = time.time()

            try:
                results = self.model.track(
                    frame,
                    persist=True,
                    tracker="bytetrack.yaml",
                    conf=STATE.confidence,
                    verbose=False,
                )
                result = results[0]
                annotated = result.plot()

                people = 0
                vehicles = 0
                objects = 0
                restricted_alert = False

                boxes = result.boxes
                if boxes is not None:
                    for i in range(len(boxes)):
                        cls_id = int(boxes.cls[i].item())
                        conf = float(boxes.conf[i].item())
                        name = self.model.names.get(cls_id, str(cls_id))

                        objects += 1
                        if name == "person":
                            people += 1
                        if name in VEHICLES:
                            vehicles += 1

                        xyxy = boxes.xyxy[i].tolist()
                        x1, y1, x2, y2 = map(int, xyxy)
                        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2

                        if name == "person" and self._inside_zone(cx, cy):
                            restricted_alert = True
                            if self._should_emit("restricted_zone"):
                                self._emit(
                                    "RESTRICTED_ZONE",
                                    "person",
                                    conf,
                                    "Person detected inside restricted zone."
                                )

                if people >= STATE.crowd_threshold and self._should_emit("crowd"):
                    self._emit(
                        "CROWD_ALERT",
                        "person",
                        None,
                        f"Crowd threshold exceeded: {people} people detected."
                    )

                if restricted_alert:
                    cv2.putText(
                        annotated,
                        "RESTRICTED ZONE ALERT",
                        (20, 45),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        1.0,
                        (0, 0, 255),
                        3,
                    )

                z = STATE.zone
                cv2.rectangle(
                    annotated,
                    (z["x1"], z["y1"]),
                    (z["x2"], z["y2"]),
                    (0, 0, 255),
                    2,
                )
                cv2.putText(
                    annotated,
                    "RESTRICTED ZONE",
                    (z["x1"], max(25, z["y1"] - 10)),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.65,
                    (0, 0, 255),
                    2,
                )

                elapsed = max(time.time() - start, 1e-6)
                fps = 1.0 / elapsed

                STATE.update_stats(
                    people=people,
                    vehicles=vehicles,
                    objects=objects,
                    alerts=len(STATE.memory_events()),
                    fps=round(fps, 1),
                    status="LIVE",
                )

                ok_jpg, jpg = cv2.imencode(".jpg", annotated, [int(cv2.IMWRITE_JPEG_QUALITY), 82])
                if ok_jpg:
                    with STATE.lock:
                        STATE.latest_jpeg = jpg.tobytes()

            except Exception as exc:
                STATE.update_stats(status=f"INFERENCE_ERROR: {str(exc)[:80]}")

        cap.release()
        STATE.update_stats(status="STOPPED")
