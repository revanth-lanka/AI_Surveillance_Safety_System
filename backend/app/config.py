import os
from dotenv import load_dotenv

load_dotenv()

CAMERA_INDEX = int(os.getenv("CAMERA_INDEX", "0"))
VIDEO_SOURCE = os.getenv("VIDEO_SOURCE", "").strip()
MODEL_NAME = os.getenv("MODEL_NAME", "yolo26n.pt")
CONFIDENCE = float(os.getenv("CONFIDENCE", "0.45"))
CROWD_THRESHOLD = int(os.getenv("CROWD_THRESHOLD", "8"))

DATABASE_MODE = os.getenv("DATABASE_MODE", "sqlite").lower()
SQLITE_PATH = os.getenv("SQLITE_PATH", "surveillance.db")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "ai_surveillance")

ZONE = {
    "x1": int(os.getenv("RESTRICTED_X1", "180")),
    "y1": int(os.getenv("RESTRICTED_Y1", "100")),
    "x2": int(os.getenv("RESTRICTED_X2", "620")),
    "y2": int(os.getenv("RESTRICTED_Y2", "420")),
}
