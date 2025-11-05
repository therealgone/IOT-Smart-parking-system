from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field
from typing import List, Tuple, Optional

import cv2
import requests

try:
    from . import config
except Exception:
    import config


Box = Tuple[int, int, int, int]


@dataclass
class DetectionState:
    last_status: List[int] = field(default_factory=lambda: [0, 0, 0, 0])
    last_post_time: float = 0.0
    last_frame_ts: float = 0.0
    camera_ok: bool = False
    error: Optional[str] = None


class ParkingDetector:
    def __init__(self, slot_boxes: List[Box] | None = None) -> None:
        self.slot_boxes: List[Box] = slot_boxes or list(config.SLOT_BOXES)
        self.state = DetectionState()
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._cam: Optional[cv2.VideoCapture] = None

    def start(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run_loop, name="ParkingDetector", daemon=True)
        self._thread.start()

    def stop(self) -> None:
        self._stop_event.set()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)
        if self._cam is not None:
            self._cam.release()
            self._cam = None
        if config.SHOW_WINDOW:
            try:
                cv2.destroyAllWindows()
            except Exception:
                pass

    def _open_camera(self) -> bool:
        try:
            self._cam = cv2.VideoCapture(config.CAMERA_INDEX)
            return bool(self._cam is not None and self._cam.isOpened())
        except Exception as exc:  # pragma: no cover
            self.state.error = f"Camera error: {exc}"
            return False

    def _run_loop(self) -> None:
        if not self._open_camera():
            self.state.camera_ok = False
            return
        self.state.camera_ok = True

        while not self._stop_event.is_set():
            ok, frame = self._cam.read() if self._cam is not None else (False, None)
            now = time.time()
            if not ok or frame is None:
                self.state.camera_ok = False
                time.sleep(1.0)
                continue

            self.state.camera_ok = True
            self.state.last_frame_ts = now

            status = self._detect_slots(frame)
            self.state.last_status = status

            # Visualization
            if config.SHOW_WINDOW:
                vis = frame.copy()
                for (x1, y1, x2, y2), occ in zip(self.slot_boxes, status):
                    color = (0, 0, 255) if occ else (0, 255, 0)
                    cv2.rectangle(vis, (x1, y1), (x2, y2), color, 2)
                cv2.imshow("Parking Detection", vis)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.stop()
                    break

            # Post to ThingSpeak no more than once per THINGSPEAK_MIN_INTERVAL seconds
            if now - self.state.last_post_time >= config.THINGSPEAK_MIN_INTERVAL:
                self._post_to_thingspeak(status)
                self.state.last_post_time = now

            time.sleep(max(0.0, config.DETECT_INTERVAL))

    def _detect_slots(self, frame) -> List[int]:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Simple static threshold — can be replaced with background subtraction or contours
        _, thresh = cv2.threshold(gray, 100, 255, cv2.THRESH_BINARY)
        statuses: List[int] = []
        for (x1, y1, x2, y2) in self.slot_boxes:
            roi = thresh[y1:y2, x1:x2]
            if roi.size == 0:
                statuses.append(0)
                continue
            white_pixels = cv2.countNonZero(roi)
            total_pixels = roi.size
            filled_ratio = white_pixels / float(total_pixels)
            occupied = 1 if filled_ratio > config.FILLED_THRESHOLD else 0
            statuses.append(occupied)
        return statuses

    def _post_to_thingspeak(self, status: List[int]) -> None:
        try:
            payload = {
                "api_key": config.THINGSPEAK_WRITE_API,
                "field1": status[0] if len(status) > 0 else 0,
                "field2": status[1] if len(status) > 1 else 0,
                "field3": status[2] if len(status) > 2 else 0,
                "field4": status[3] if len(status) > 3 else 0,
            }
            requests.post(config.THINGSPEAK_URL, data=payload, timeout=5)
        except Exception as exc:  # pragma: no cover
            self.state.error = f"ThingSpeak post error: {exc}"


