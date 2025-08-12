# 🤖 AI 24/7 워크플로우 자동화 시스템

> 100% 무료 도구로 구축하는 24시간 무중단 AI 워크플로우 시스템

## 🎯 프로젝트 소개

로컬 환경에서 **완전 무료**로 구동되는 24시간 AI 자동화 시스템입니다. 
GitHub 기반 협업과 무료 AI 모델(Ollama, Hugging Face)을 활용합니다.

### 핵심 특징
- ✅ **100% 무료** - 모든 구성요소가 오픈소스/무료
- ✅ **로컬 실행** - 클라우드 비용 없음  
- ✅ **AI 통합** - Ollama로 로컬 LLM 실행
- ✅ **24/7 작동** - 무중단 자동화
- ✅ **GitHub 기반** - 버전 관리 및 CI/CD

## 🚀 빠른 시작

### 1. 필수 설치
```bash
# Python 3.11+
https://python.org

# Docker Desktop  
https://docker.com

# Git
https://git-scm.com

# Ollama (AI 모델)
https://ollama.ai
```

### 2. 프로젝트 설정
```bash
# 클론
git clone https://github.com/[your-username]/ai-workflow-24h
cd ai-workflow-24h

# 환경 설정
cp .env.example .env

# 의존성 설치
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt

# Ollama 모델 설치
ollama pull llama2:7b
```

### 3. 실행
```bash
# Docker 서비스 시작
docker-compose up -d

# FastAPI 서버 시작
uvicorn src.main:app --reload

# 접속
http://localhost:8000
http://localhost:8000/docs (API 문서)
```

## 📁 프로젝트 구조
```
ai-workflow-24h/
├── docs/           # 프로젝트 문서
├── src/
│   ├── ai/        # AI 모델 통합
│   ├── workflow/  # 워크플로우 엔진  
│   └── main.py    # FastAPI 앱
├── config/        # 설정 파일
├── tests/         # 테스트
├── docker-compose.yml
└── requirements.txt
```

## 🛠 기술 스택 (모두 무료!)

| 구성 | 기술 | 용도 |
|------|------|------|
| AI 모델 | Ollama (Llama2) | 로컬 LLM |
| 백엔드 | FastAPI | REST API |
| 작업 큐 | Celery + Redis | 비동기 처리 |
| DB | PostgreSQL | 데이터 저장 |
| 모니터링 | Grafana | 대시보드 |
| CI/CD | GitHub Actions | 자동화 |

## 💡 주요 기능

### 1. 자동 작업 처리
```python
# API로 작업 생성
POST /tasks
{
  "name": "데이터 처리",
  "type": "data_processing",
  "payload": {"count": 1000}
}
```

### 2. AI 우선순위 결정
- AI가 작업 중요도 자동 판단
- 긴급 작업 우선 처리

### 3. 24시간 모니터링
- http://localhost:3000 (Grafana)
- 실시간 상태 확인

## 📊 모니터링 URL

| 서비스 | URL | 설명 |
|--------|-----|------|
| API | http://localhost:8000 | 메인 API |
| API 문서 | http://localhost:8000/docs | Swagger UI |
| Grafana | http://localhost:3000 | 모니터링 (admin/admin) |
| Flower | http://localhost:5555 | Celery 모니터링 |
| RabbitMQ | http://localhost:15672 | 큐 관리 (admin/admin) |

## 🧪 테스트

```bash
# 단위 테스트
pytest tests/

# 대량 작업 테스트
curl -X POST http://localhost:8000/tasks/bulk?count=100
```

## 🔧 개발 명령어

```bash
make help        # 도움말
make install     # 설치
make dev        # 개발 서버
make test       # 테스트
make docker-up  # Docker 시작
make docker-down # Docker 중지
```

## 📈 확장 가능성

### 무료 클라우드 옵션
- **Supabase**: PostgreSQL 500MB 무료
- **Redis Cloud**: 30MB 무료  
- **Railway**: 월 $5 크레딧
- **Render**: 무료 웹 서비스

### 더 작은 AI 모델
```bash
# 메모리 절약형 모델
ollama pull tinyllama:1.1b  # 638MB
ollama pull phi:2.7b        # 1.6GB
```

## 🤝 기여 방법

1. Fork 하기
2. Feature 브랜치 생성 (`git checkout -b feature/AmazingFeature`)
3. 커밋 (`git commit -m 'Add AmazingFeature'`)
4. Push (`git push origin feature/AmazingFeature`)
5. Pull Request 생성

## 📝 라이센스

MIT License - 자유롭게 사용하세요!

## 💬 문의

Issues: https://github.com/[your-username]/ai-workflow-24h/issues

---

**Made with ❤️ using 100% free tools**