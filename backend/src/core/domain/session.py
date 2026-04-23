from pydantic import BaseModel, Enum

class SessionType(str, Enum):
    EVALUATION = "evaluation"
    MODEL_EDITING = "model_editing"

class Session(BaseModel):
    sessionId: str
    sessionType: SessionType

