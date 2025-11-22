from typing import Dict, List
from pydantic import BaseModel, Field


class EmotionRequest(BaseModel):
    frame: str = Field(
        ...,
        description=(
            "Base64-encoded image data. You can optionally use a data URL "
            "prefix like 'data:image/jpeg;base64,...'."
        ),
    )


class EmotionResult(BaseModel):
    face_id: int = Field(..., description="Index of the detected face in the frame.")
    box: List[int] = Field(
        ..., description="Bounding box [x, y, width, height] from FER."
    )
    dominant_emotion: str = Field(..., description="Most likely emotion label.")
    dominant_score: float = Field(..., description="Probability of dominant emotion.")
    emotions: Dict[str, float] = Field(
        ..., description="Full probability distribution per emotion."
    )


class EmotionResponse(BaseModel):
    results: List[EmotionResult]