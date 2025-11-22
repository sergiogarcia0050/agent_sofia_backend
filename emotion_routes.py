from fastapi import APIRouter, HTTPException, status
from fastapi.concurrency import run_in_threadpool

from emotion_models import EmotionRequest, EmotionResponse
from emotion_service import (
    EmotionServiceError,
    FERModelNotLoadedError,
    InvalidImageFormatError,
    NoFaceDetectedError,
    get_emotion_service,
)

router = APIRouter(
    prefix="/api/emotions",
    tags=["emotions"],
)


@router.post("/analyze", response_model=EmotionResponse)
async def analyze_emotions(payload: EmotionRequest) -> EmotionResponse:
    """
    Analyze emotions in a single video frame encoded as base64.

    Returns a list of detected faces with their dominant emotion and
    full emotion distribution.
    """
    service = get_emotion_service()

    try:
        # FER is CPU-heavy; run in a threadpool so we don't block the event loop.
        results = await run_in_threadpool(service.analyze_frame, payload.frame)
        return EmotionResponse(results=results)

    except InvalidImageFormatError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except NoFaceDetectedError as exc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc

    except FERModelNotLoadedError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc

    except EmotionServiceError as exc:
        # Generic EmotionServiceError or any subclasses not handled above
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Emotion analysis failed",
        ) from exc