# Smart Parking System (OpenCV + ThingSpeak + GitHub Pages)

This project provides a minimal end-to-end setup:
- Python + OpenCV detects cars in predefined boxes from a webcam.
- Status (1 = occupied, 0 = available) is pushed to ThingSpeak every 15 seconds.
- A static frontend (GitHub Pages) reads ThingSpeak and shows slot states.

## Structure

```
backend/
  app.py               # Flask app exposing /health and /status
  detector.py          # OpenCV detection loop, ThingSpeak posting
  config.py            # Config via env vars (keys, boxes, thresholds)
  requirements.txt     # Python dependencies
frontend/
  index.html
  script.js
  styles.css
```

## Prerequisites
- Python 3.10+
- A webcam
- A ThingSpeak channel with 4 fields (field1..field4)
- ThingSpeak Write API key (kept local/private)

## Backend: Run locally

1) Create and activate a virtual environment (recommended).

Windows PowerShell:
```powershell
cd backend
python -m venv .venv
. .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2) Set environment variables. At minimum set your write key.
```powershell
$env:THINGSPEAK_WRITE_API = "YOUR_WRITE_KEY"
# Optional tweaks:
# $env:CAMERA_INDEX = "0"
# $env:FILLED_THRESHOLD = "0.4"
# $env:THINGSPEAK_MIN_INTERVAL = "15"
# $env:SHOW_WINDOW = "1"   # to show annotated preview window
```

3) Run the Flask app (which starts the detector in a background thread):
```powershell
python -m flask --app app run --host 0.0.0.0 --port 5001 --debug
```

Endpoints:
- http://localhost:5001/health
- http://localhost:5001/status

The detector posts to ThingSpeak no more than once every THINGSPEAK_MIN_INTERVAL seconds.

## Frontend: GitHub Pages

- Put the `frontend/` directory contents into a GitHub repository root (or a `docs/` folder configured for Pages).
- In `frontend/script.js`, set your `CHANNEL_ID` and (if needed) `READ_API_KEY`.
- Enable GitHub Pages (Settings → Pages) and point to the branch/folder.

The dashboard polls every 5 seconds and repaints the four slots.

## Adjusting Parking Boxes

Edit `backend/config.py` → `SLOT_BOXES` and restart the backend. Coordinates are `(x1, y1, x2, y2)` in pixels relative to the camera frame.

## Notes
- ThingSpeak free tier requires ≥15s between updates.
- Write keys should never be published to the frontend; only read keys are safe for public dashboards.

## Future Enhancements
- Replace static thresholding with background subtraction/contour filtering.
- Add timestamps/durations to extra ThingSpeak fields.
- Live charts and historical graphs.
- “Edit Box Mode” in the frontend to reconfigure boxes visually.
- Switch to Firebase Realtime Database for instant updates.


