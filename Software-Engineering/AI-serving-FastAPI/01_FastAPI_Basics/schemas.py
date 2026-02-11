from pydantic import BaseModel # type: ignore

# 웹팀이 보낼 데이터 규격
class PredictionRequest(BaseModel):
    patient_name: str
    image_path: str
    threshold: float = 0.5  # 기본값 설정

# 서버가 응답할 데이터 규격
class PredictionResponse(BaseModel):
    patient_name: str
    is_ggo: bool
    confidence: float
    message: str