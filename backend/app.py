from __future__ import annotations

import atexit
from typing import Any, Dict

from flask import Flask, jsonify

try:
    # When running as a package (e.g., --app backend.app)
    from .detector import ParkingDetector
except Exception:
    # When running from the backend directory (e.g., --app app)
    from detector import ParkingDetector


detector = ParkingDetector()
detector.start()


def _shutdown() -> None:
    detector.stop()


atexit.register(_shutdown)

app = Flask(__name__)


@app.get("/health")
def health() -> Any:
    st = detector.state
    return jsonify({
        "ok": True,
        "camera_ok": st.camera_ok,
        "last_frame_ts": st.last_frame_ts,
        "last_post_time": st.last_post_time,
        "error": st.error,
    })


@app.get("/status")
def status() -> Any:
    st = detector.state
    data: Dict[str, Any] = {
        "slots": st.last_status,
    }
    return jsonify(data)


if __name__ == "__main__":
    # For local development only
    app.run(host="0.0.0.0", port=5001, debug=True)


