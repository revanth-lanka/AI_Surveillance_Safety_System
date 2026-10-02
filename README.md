# Real-Time AI Surveillance & Safety System

A full-stack computer-vision project for real-time object detection, tracking, people counting, restricted-zone alerts, crowd alerts, event logging, and a live React dashboard.

## Features

- YOLO real-time object detection
- Persistent object tracking with ByteTrack
- People and vehicle counting
- Configurable restricted zone
- Crowd threshold alert
- Event history
- Live MJPEG camera stream
- WebSocket live statistics
- React dashboard
- SQLite event storage by default
- Optional MongoDB support
- REST API
- Windows start scripts

## Tech Stack

- Python 3.10+
- FastAPI
- Ultralytics YOLO
- OpenCV
- WebSockets
- React + Vite
- SQLite / optional MongoDB
- Recharts

## Project Structure

```text
AI-Surveillance-Safety-System/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── state.py
│   │   ├── database.py
│   │   ├── detector.py
│   │   ├── camera.py
│   │   └── schemas.py
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── App.jsx
│   │   ├── api.js
│   │   ├── main.jsx
│   │   └── styles.css
│   ├── package.json
│   └── vite.config.js
├── run_backend.bat
├── run_frontend.bat
├── .gitignore
└── README.md
```

## 1. Backend setup

Open PowerShell in the project directory:

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` if you want custom settings.

Start the backend:

```powershell
uvicorn app.main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

API docs:

```text
http://127.0.0.1:8000/docs
```

On first model use, Ultralytics downloads the configured YOLO model automatically.

## 2. Frontend setup

Open a second PowerShell:

```powershell
cd frontend
npm install
npm run dev
```

Open the URL printed by Vite, normally:

```text
http://localhost:5173
```

## 3. Camera

The backend defaults to webcam index `0`.

Change `CAMERA_INDEX` in `.env` if you have another camera.

You can also set:

```env
VIDEO_SOURCE=path/to/video.mp4
```

for a prerecorded video.

## 4. MongoDB (optional)

The project works out of the box with SQLite. To use MongoDB, set:

```env
DATABASE_MODE=mongodb
MONGO_URI=mongodb://localhost:27017
MONGO_DB=ai_surveillance
```

## 5. Important notes

This is a portfolio/educational project. It is not a certified security system.

For commercial deployment, review the current Ultralytics licensing terms. The project uses Ultralytics YOLO for inference/tracking.

## Suggested next upgrades

- User authentication and roles
- Multiple camera streams
- Email/Telegram alerts
- Snapshot storage
- Abandoned-object detection
- Heatmaps
- Docker deployment
- Cloud deployment
