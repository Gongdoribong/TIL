from fastapi import FastAPI # type: ignore
from .schemas import PredictionRequest, PredictionResponse
from .model import LiverSegmentationModel

# FastAPI 인스턴스 생성
app = FastAPI()

# 서버가 켜질 때 모델을 딱 한 번만 미리 로드해둡니다. (매번 로드하면 너무 느려요!)
model = LiverSegmentationModel()

#### Get 실습 ####

@app.get("/")
def read_root():
    """
    기본 접속 경로 확인을 위한 엔드포인트
    """
    return {"message": "AI Serving Server is Running!"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None): # type: ignore
    return {"item_id": item_id, "query": q}


#### Post 실습 ####

@app.post("/predict", response_model=PredictionResponse)
def predict_liver(request: PredictionRequest):
    # 1. 추론 요청
    result = model.predict(
        name=request.patient_name, 
        path=request.image_path, 
        threshold=request.threshold
    )
    
    # 2. 응답 구성
    return {
        "patient_name": request.patient_name,
        "is_ggo": result["is_ggo"],
        "confidence": result["confidence"],
        "message": f"{request.image_path} 분석이 완료되었습니다."
    }