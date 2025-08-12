# 로컬 개발 환경 설정 가이드

## 🎯 개발 원칙
- **100% 무료 도구만 사용**
- **로컬 환경에서 완전히 작동**
- **GitHub 기반 협업**
- **최소 리소스로 최대 효과**

## 📦 필요한 무료 도구

### 필수 설치
1. **Python 3.11+** - [python.org](https://python.org)
2. **Docker Desktop** - [docker.com](https://docker.com)
3. **Git** - [git-scm.com](https://git-scm.com)
4. **VS Code** - [code.visualstudio.com](https://code.visualstudio.com)

### 무료 AI 모델
- **Ollama** - 로컬 LLM 실행 (Llama 2, Mistral 등)
- **Hugging Face Models** - 무료 모델 다운로드
- **GPT4All** - 데스크톱용 무료 LLM

## 🚀 빠른 시작

### 1. 프로젝트 클론
```bash
git clone https://github.com/[your-username]/ai-workflow-24h.git
cd ai-workflow-24h
```

### 2. Python 가상환경 설정
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. Ollama 설치 및 모델 다운로드
```bash
# Ollama 설치 후
ollama pull llama2:7b
ollama pull mistral
```

### 5. 로컬 서비스 실행
```bash
docker-compose up -d
```

## 🏗️ 로컬 아키텍처

```
로컬 PC
├── Docker Container
│   ├── Redis (메모리 DB)
│   ├── PostgreSQL (데이터 저장)
│   └── RabbitMQ (메시지 큐)
├── Python App
│   ├── FastAPI (웹 서버)
│   ├── Celery (작업 큐)
│   └── Ollama (AI 모델)
└── 브라우저
    └── 로컬 대시보드 (localhost:8000)
```

## 💾 무료 데이터베이스 옵션

### 개발용 (Docker)
- **PostgreSQL**: 로컬 컨테이너
- **Redis**: 메모리 캐시
- **SQLite**: 파일 기반 DB (더 간단함)

### 프로덕션용 (무료 티어)
- **Supabase**: PostgreSQL 500MB 무료
- **Redis Cloud**: 30MB 무료
- **MongoDB Atlas**: 512MB 무료

## 🤖 무료 AI 모델 설정

### Ollama 통합
```python
# src/ai/ollama_client.py
import ollama

class LocalAI:
    def __init__(self):
        self.client = ollama.Client()
    
    def generate(self, prompt):
        response = self.client.generate(
            model='llama2:7b',
            prompt=prompt
        )
        return response['response']
```

### Hugging Face 통합
```python
# src/ai/huggingface_client.py
from transformers import pipeline

class HuggingFaceAI:
    def __init__(self):
        self.pipe = pipeline(
            "text-generation",
            model="microsoft/DialoGPT-small"
        )
    
    def generate(self, prompt):
        return self.pipe(prompt)[0]['generated_text']
```

## 🐳 Docker Compose 설정

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: workflow
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - ./data/postgres:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - ./data/redis:/data

  rabbitmq:
    image: rabbitmq:3-management-alpine
    ports:
      - "5672:5672"
      - "15672:15672"
    environment:
      RABBITMQ_DEFAULT_USER: admin
      RABBITMQ_DEFAULT_PASS: admin
```

## 🔧 개발 워크플로우

### 1. 기능 개발
```bash
# 새 브랜치 생성
git checkout -b feature/작업명

# 코드 작성
# 테스트 실행
pytest

# 커밋
git add .
git commit -m "feat: 기능 설명"
git push origin feature/작업명
```

### 2. GitHub Actions (무료)
```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - run: |
          pip install -r requirements.txt
          pytest
```

## 📊 모니터링 (무료)

### 로컬 모니터링
- **Prometheus**: 메트릭 수집
- **Grafana**: 시각화 (Docker)
- **Portainer**: Docker 관리 UI

### 로그 관리
```python
# 간단한 파일 로깅
import logging

logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
```

## 💡 메모리 절약 팁

### 1. 경량 모델 사용
- Llama 2 7B 대신 3B 모델
- Mistral 7B 대신 TinyLlama 1.1B

### 2. 배치 처리
- 작업을 모아서 한 번에 처리
- GPU 메모리 효율적 사용

### 3. 캐싱 전략
- Redis로 결과 캐싱
- 반복 계산 최소화

## 🚦 시작 명령어

### 전체 시스템 시작
```bash
# 1. Docker 서비스 시작
docker-compose up -d

# 2. Ollama 시작
ollama serve

# 3. Celery Worker 시작
celery -A src.worker worker --loglevel=info

# 4. FastAPI 서버 시작
uvicorn src.main:app --reload --port 8000
```

### 개발 서버 접속
- API: http://localhost:8000
- API 문서: http://localhost:8000/docs
- RabbitMQ 관리: http://localhost:15672
- 모니터링: http://localhost:3000 (Grafana)

## 🆓 완전 무료 스택 요약

| 구성 요소 | 무료 솔루션 |
|----------|------------|
| AI 모델 | Ollama (Llama2, Mistral) |
| 웹 프레임워크 | FastAPI |
| 작업 큐 | Celery + Redis |
| 데이터베이스 | PostgreSQL (Docker) |
| 메시지 브로커 | RabbitMQ |
| 모니터링 | Prometheus + Grafana |
| CI/CD | GitHub Actions |
| 컨테이너 | Docker |
| 코드 저장소 | GitHub |

## 📝 참고사항

- 최소 RAM 8GB 권장 (AI 모델 실행)
- SSD 사용 권장 (모델 로딩 속도)
- Windows는 WSL2 사용 권장
- Mac M1/M2는 ARM 버전 Docker 사용