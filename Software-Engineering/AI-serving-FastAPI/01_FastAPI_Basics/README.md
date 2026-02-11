# [Day 01] AI 서빙 엔지니어링: 환경 구축부터 레이어드 아키텍처까지

## 1. FastAPI 핵심 개념 및 첫 서버
- **FastAPI**: 파이썬 타입 힌트를 기반으로 한 초고속 웹 프레임워크
- **Uvicorn**: 비동기 통신(ASGI)을 지원하는 실행 서버
- **Swagger UI (`/docs`)**: 코드 작성과 동시에 자동 생성되는 인터랙티브 API 명세서

### HTTP Methods (실무적 차이)
- **GET**: 데이터 조회용. 주소창에 정보가 노출됨
- **POST**: 데이터 생성/처리 요청용. 본문(Body)에 데이터를 숨겨 보냄. AI 모델 추론은 대부분 `POST`를 사용함.

</br>


## 2. 소프트웨어 설계: 레이어드 아키텍처 (Layered Architecture)
코드의 유지보수성과 확장성을 위해 역할을 세 가지로 분리함

- **`main.py` (Controller/Entrypoint)**: 서버의 입구. 요청을 받고 응답을 서빙함

- **`schemas.py` (Data Model)**: Pydantic `BaseModel`을 사용하여 데이터의 규격(Type, 기본값)을 정의함

- **`model.py` (Business Logic/Inference)**: 실제 AI 모델(MedSAM2, nnU-Net 등)의 추론 로직이 위치함

## 3. 코드 분석

### Get 요청

``` python
@app.get("/")
def read_root():
    """
    기본 접속 경로 확인을 위한 엔드포인트
    """
    return {"message": "AI Serving Server is Running!"}

@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "query": q}
```


- `@app.get("/")` : Decorator. `@`뒤에 있는 객체에게 명령. Root로 누군가 데이터를 GET 하러 오면 아래의 함수를 실행

- `@app.get("/items/{item_id}")` : 주소창에 숫자가 바뀔 때마다 대응할 수 있는 Dynamic Path. 중괄호 안에 있는 이름은 아래 함수의 파라미터 이름과 같아야 함

- `"""..."""` : Docstring. Swagger UI에서 노출되는 설명문

- `item_id: int` : Path Parameter. 주소창에서 온 값을 받는데, data type을 명시함.

    $\rightarrow$ 사용자의 입력이 올바른 data type이 아닐경우 FastAPI가 자동으로 에러 메시지를 출력함 (데이터 검증)

- `q: str = None` : Query Parameter. 주소 뒤에 `?q=hello` 처럼 붙는 옵션 값

- `return { ... }` : dictionary 형태를 return하면 FastAPI가 자동으로 JSON 형식으로 변환하여 웹 브라우저에 보내줌


### Post 요청

``` python
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
```

- `@app.post("/predict")` : 누군가 `/predict` 주소로 POST 요청을 보내면 아래 함수를 실행하라는 명령

- `response_model = PredictionResponse` : 함수가 반환하는 데이터가 `PredictionResonse` 규격에 맞는지 검사. 반환값에 불필요한 정보가 섞여 있어도, 이 모델에 정의된 필드만 골라내서 응답 (필터링)

- `request: PredictionRequest` : FastAPI가 Body에 들어있는 JSON 데이터를 `PredictionRequest` 형태로 변환해서 `request` 변수에 저장. 데이터 형식이 틀릴 경우 여기서 에러를 출력해 함수를 실행하지 못하게 함.

- `return { ... }` : FastAPI가 이 딕셔너리를 위에서 정의한 `response_model` 규격에 맞춰 JSON으로 자동 변환

</br>

## 4. 트러블슈팅 (Troubleshooting Log)

### Q1. `AttributeError: '_SpecialForm' object has no attribute 'replace'`
- **원인**: Python 3.9와 Pydantic v2 간의 라이브러리 내부 호환성 문제.
- **해결**: `uv python pin 3.12`를 통해 Python 버전을 3.12로 업그레이드하여 해결.

### Q2. `ModuleNotFoundError: No module named 'schemas'`
- **원인**: 파이썬 실행 경로(Root)와 모듈 탐색 경로의 불일치.
- **해결**: 상대 경로(`from .schemas import ...`) 사용.

</br>


---

### ✅ Day 01 학습 완료 체크리스트
- [x] 독립된 가상환경에서 파이썬 3.12 실행 가능
- [x] FastAPI 서버 구동 및 Swagger UI 접속 성공
- [x] GET/POST의 차이점 이해 및 POST 데이터 전송 실습
- [x] 파일 분리(main, schemas, services)를 통한 모듈화 구조 이해