import base64
import logging
from functools import lru_cache
from typing import List

import cv2
import numpy as np
from fer import FER

from emotion_models import EmotionResult

logger = logging.getLogger(__name__)


class EmotionServiceError(Exception):
    """Base class for emotion service errors."""


class InvalidImageFormatError(EmotionServiceError):
    """Raised when the input image cannot be decoded."""


class NoFaceDetectedError(EmotionServiceError):
    """Raised when no faces are detected in the frame."""


class FERModelNotLoadedError(EmotionServiceError):
    """Raised when the FER model is not available or fails."""


class EmotionService:
    """
    Service responsible for loading the FER detector and running inference
    over single frames.

    Initialization is intentionally heavy and should be done once per process.
    """

    def __init__(self, use_mtcnn: bool = True) -> None:
        try:
            logger.info("Initializing FER detector (mtcnn=%s)...", use_mtcnn)
            self._detector = FER(mtcnn=use_mtcnn)
        except Exception as exc:  # noqa: BLE001
            logger.exception("Failed to initialize FER detector")
            self._detector = None
            raise FERModelNotLoadedError("FER model could not be initialized") from exc

    def close(self) -> None:
        """
        Cleanup hook.

        FER currently does not require explicit cleanup, but this method is
        provided to support future resource management if needed.
        """
        logger.info("EmotionService cleanup called")
        # No-op for now; kept for symmetry / future resources.

    def _decode_base64_image(self, image_data: str) -> np.ndarray:
        """
        Decode a base64 image string into an RGB numpy array.

        Supports optional data URL prefixes like 'data:image/jpeg;base64,...'.
        """
        try:
            # Strip optional data URL prefix
            _, _, b64_data = image_data.partition(",")
            if not b64_data:
                b64_data = image_data

            img_bytes = base64.b64decode(b64_data, validate=True)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to base64-decode frame")
            raise InvalidImageFormatError("Invalid base64 image data") from exc

        nparr = np.frombuffer(img_bytes, np.uint8)
        img_bgr = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img_bgr is None:
            logger.warning("cv2.imdecode returned None for frame")
            raise InvalidImageFormatError("Could not decode image bytes")

        # Convert BGR (OpenCV default) to RGB for FER
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB)
        return img_rgb

    def analyze_frame(self, image_data: str) -> List[EmotionResult]:
        """
        Run FER on a single frame and return a list of EmotionResult objects.
        """
        if self._detector is None:
            logger.error("FER detector is not loaded")
            raise FERModelNotLoadedError("FER detector is not loaded")

        img_rgb = self._decode_base64_image(image_data)

        try:
            detections = self._detector.detect_emotions(img_rgb)
        except Exception as exc:  # noqa: BLE001
            logger.exception("FER detection failed")
            raise FERModelNotLoadedError("FER model failed during detection") from exc

        if not detections:
            logger.info("No faces detected in frame")
            raise NoFaceDetectedError("No faces detected in the frame")

        results: List[EmotionResult] = []
        for idx, det in enumerate(detections):
            box = det.get("box") or []
            emotions = det.get("emotions") or {}

            if not emotions:
                # Skip if we for some reason don't have scores
                logger.debug("Skipping detection with empty emotions: %s", det)
                continue

            dominant_emotion = max(emotions, key=emotions.get)
            dominant_score = float(emotions[dominant_emotion])

            results.append(
                EmotionResult(
                    face_id=idx,
                    box=box,
                    dominant_emotion=dominant_emotion,
                    dominant_score=domin_score,
                    emotions={k: float(v) for k, v in emotions.items()},
                )
            )

        if not results:
            logger.info("Detections present but no valid emotion results")
            raise NoFaceDetectedError("No valid faces with emotions detected")

        return results


@lru_cache
def get_emotion_service() -> EmotionService:
    """
    FastAPI-friendly dependency factory that returns a singleton EmotionService.

    Using @lru_cache ensures the FER model is loaded only once per process.
    """
    return EmotionService()