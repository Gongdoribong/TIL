import time

class LiverSegmentationModel:
    def __init__(self):
        # 실무에서는 여기서 모델 가중치를 로드합니다.
        # self.model = load_medsam2_weights("model.pth")
        print("AI Model Loaded Successfully!")

    def predict(self, name: str, path: str, threshold: float):
        # 1. 이미지 읽기 & 전처리 (Preprocessing)
        # 2. 모델 추론 (Inference)
        time.sleep(1)  # 딥러닝 모델이 돌아가는 척...
        
        # 3. 결과 반환
        return {
            "is_ggo": True,
            "confidence": 0.98
        }