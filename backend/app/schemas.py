from pydantic import BaseModel, Field

class ZoneUpdate(BaseModel):
    x1: int = Field(ge=0)
    y1: int = Field(ge=0)
    x2: int = Field(gt=0)
    y2: int = Field(gt=0)

class SettingsUpdate(BaseModel):
    crowd_threshold: int = Field(ge=1, le=500)
    confidence: float = Field(ge=0.05, le=0.99)
