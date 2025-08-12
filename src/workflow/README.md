# 📚 웹소설 24시간 자동 생성 시스템

10개의 AI 에이전트가 협업하여 24시간 자동으로 웹소설을 생성, 검수, 개선하는 시스템

## 🎯 프로젝트 특징

- **24시간 자동 운영**: 에이전트들이 자동으로 웹소설 생성 및 검수
- **10개 전문 에이전트**: 각자의 역할을 가진 AI 에이전트 협업
- **Claude API 기반**: 고품질 텍스트 생성
- **자동 품질 관리**: 세계관, 역사, 문법, AI 화법 검사
- **독자 피드백 시뮬레이션**: 다양한 페르소나의 독자 평가

## 🏗️ 시스템 구조

```
메인 오케스트레이터
    ├── PM 에이전트 (감독)
    ├── 작가 에이전트 (집필)
    ├── 세계관 담당 (일관성 검증)
    ├── 역사 담당 (스토리 연속성)
    ├── 역사 개선 에이전트 (스토리 개선)
    ├── 문법 담당 (문장 품질)
    ├── AI 화법 감지 (자연스러움)
    ├── 독자 담당 × 5 (다양한 관점)
    └── QA 담당 (최종 검증)
```

## 🚀 빠른 시작

### 1. 요구사항
- Python 3.9+
- Claude API Key

### 2. 설치
```bash
# 클론
git clone https://github.com/yourusername/webnovel-automation.git
cd webnovel-automation

# 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 의존성 설치
pip install -r requirements.txt
```

### 3. 설정
```bash
# 환경변수 설정
cp .env.example .env
# .env 파일을 열어 CLAUDE_API_KEY 입력

# 설정 파일 수정 (선택사항)
# config/config.yaml 에서 웹소설 설정 변경
```

### 4. 실행
```bash
# 일반 실행
python main.py

# 테스트 모드 (샘플 에피소드 생성)
python main.py --test

# 도움말
python main.py --help
```

## 📁 폴더 구조

```
webnovel-automation/
├── agents/                 # 에이전트 모듈
│   ├── base_agent.py      # 베이스 클래스
│   ├── main_agent.py      # 메인 오케스트레이터
│   ├── writer_agent.py    # 작가 에이전트
│   └── ...                # 기타 에이전트들
├── documents/             # 문서 저장소
│   ├── drafts/           # 초안
│   ├── episodes/         # 완성 에피소드
│   ├── worldbuilding/    # 세계관 설정
│   └── history/          # 스토리 역사
├── config/               # 설정 파일
│   └── config.yaml      # 시스템 설정
├── logs/                # 로그 파일
└── memory/              # 에이전트 메모리
```

## 🔄 작동 방식

### Option A: 파일 감시 모드
1. `documents/drafts/` 폴더에 파일 생성/수정
2. 메인 에이전트가 자동 감지
3. 작업 유형 판단 후 적절한 에이전트에게 할당
4. 순차적 검수 진행
5. 완성된 에피소드는 `documents/episodes/`에 저장

### Option B: 스케줄 모드
1. 설정된 시간에 자동 실행
2. 작가 에이전트가 새 에피소드 생성
3. 검수 파이프라인 자동 진행
4. QA 통과시 자동 발행

## ⚙️ 설정 변경

`config/config.yaml` 파일에서 다양한 설정 변경 가능:

- **웹소설 설정**: 제목, 장르, 주인공 등
- **에이전트 설정**: 각 에이전트의 동작 방식
- **스케줄**: 생성 및 발행 시간
- **API 한도**: 일일 토큰 제한 등

## 📊 모니터링

- **로그 파일**: `logs/webnovel.log`
- **API 사용량**: `logs/api_usage.log`
- **에이전트 상태**: 콘솔에 실시간 표시

## 🤝 기여 방법

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📝 라이선스

MIT License

## ⚠️ 주의사항

- Claude API 사용량에 따라 비용 발생
- API Key는 절대 공개 저장소에 커밋하지 마세요
- 일일 토큰 한도 설정을 확인하세요

## 🆘 문제 해결

### API 한도 도달
- 설정에서 `retry_delay` 조정
- 일일 토큰 한도 증가

### 파일 감시 안됨
- `documents/drafts/` 폴더 권한 확인
- 파일 시스템 이벤트 지원 확인

### 에이전트 오류
- 개별 에이전트 로그 확인: `logs/agents/`
- 메모리 파일 초기화: `memory/` 폴더 정리

## 📞 연락처

문의사항이나 버그 리포트는 Issues 탭을 이용해주세요.