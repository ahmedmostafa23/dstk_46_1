from pydantic import BaseModel

class ModelInferenceResponseSchema(BaseModel):
    pred: str
    confidence: float