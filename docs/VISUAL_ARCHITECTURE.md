# 🎨 시스템 아키텍처 시각화

## 📐 전체 시스템 흐름도

```mermaid
graph TB
    subgraph "사용자 영역"
        U[👤 사용자]
        W[🌐 웹 브라우저]
    end
    
    subgraph "프론트엔드"
        D[📊 대시보드<br/>localhost:8000]
    end
    
    subgraph "API 계층"
        API[⚡ FastAPI<br/>REST API]
    end
    
    subgraph "AI 두뇌 💰유료"
        C[🧠 Claude API<br/>의사결정 엔진]
    end
    
    subgraph "처리 엔진 🆓무료"
        WE[⚙️ 워크플로우 엔진]
        TQ[📋 작업 큐<br/>Celery]
        SC[⏰ 스케줄러]
    end
    
    subgraph "데이터 저장소 🆓무료"
        PG[(🗄️ PostgreSQL<br/>메인 DB)]
        RD[(⚡ Redis<br/>캐시/큐)]
    end
    
    subgraph "모니터링 🆓무료"
        GF[📈 Grafana]
        PR[📊 Prometheus]
        FL[🌻 Flower]
    end
    
    U --> W
    W --> D
    D --> API
    API --> WE
    WE <--> C
    WE --> TQ
    TQ --> SC
    WE --> PG
    WE --> RD
    API --> GF
    PR --> GF
    TQ --> FL
    
    style C fill:#ff6b6b,stroke:#ff0000,stroke-width:3px
    style PG fill:#90EE90
    style RD fill:#90EE90
    style TQ fill:#90EE90
    style GF fill:#90EE90
```

## 🔄 작업 처리 생명주기

```mermaid
stateDiagram-v2
    [*] --> 작업생성: 사용자/시스템 요청
    
    작업생성 --> Claude분석: 작업 내용 전송
    
    Claude분석 --> 우선순위결정: AI 판단
    note right of Claude분석
        💰 Claude API 호출
        - 작업 유형 파악
        - 위험도 평가
        - 실행 방법 결정
    end
    
    우선순위결정 --> 큐등록: 우선순위 할당
    
    큐등록 --> 자동실행: 낮은 위험도
    큐등록 --> 승인대기: 높은 위험도
    
    승인대기 --> 자동실행: 승인됨
    승인대기 --> 취소: 거부됨
    
    자동실행 --> 성공: 정상 완료
    자동실행 --> 실패: 오류 발생
    
    실패 --> Claude분석: 재시도
    실패 --> 수동처리: 최대 재시도 초과
    
    성공 --> 결과저장
    수동처리 --> 결과저장
    취소 --> 결과저장
    
    결과저장 --> [*]: 완료
```

## 💸 비용 최적화 플로우

```mermaid
flowchart LR
    subgraph "작업 입력"
        T1[작업 1]
        T2[작업 2]
        T3[작업 3]
        T4[작업 N]
    end
    
    subgraph "최적화 레이어"
        CA[🗂️ 캐시 확인]
        BA[📦 배치 수집]
        PR[🎯 우선순위 필터]
    end
    
    subgraph "Claude 호출"
        CL[🧠 Claude API<br/>💰 비용 발생]
    end
    
    subgraph "결과 처리"
        CS[💾 캐시 저장]
        EX[⚡ 실행]
    end
    
    T1 --> CA
    T2 --> CA
    T3 --> CA
    T4 --> CA
    
    CA -->|캐시 미스| BA
    CA -->|캐시 히트| EX
    
    BA -->|10개 수집| CL
    BA -->|긴급| CL
    
    PR --> CL
    
    CL --> CS
    CS --> EX
    
    style CL fill:#ff6b6b,stroke:#ff0000,stroke-width:3px
```

## 🏗️ 컴포넌트 상세 구조

```
ai-workflow-24h/
│
├── 🎯 Frontend (무료)
│   └── FastAPI + Jinja2 Templates
│       ├── 대시보드
│       ├── 작업 관리
│       └── 모니터링
│
├── 🧠 AI Layer (유료 - Claude)
│   └── Claude API Manager
│       ├── 프롬프트 엔지니어링
│       ├── 응답 파싱
│       ├── 캐싱 시스템
│       └── 비용 추적
│
├── ⚙️ Processing Layer (무료)
│   ├── Workflow Engine
│   │   ├── 작업 실행기
│   │   ├── 상태 관리
│   │   └── 오류 처리
│   │
│   ├── Celery Workers
│   │   ├── 비동기 처리
│   │   ├── 재시도 로직
│   │   └── 우선순위 큐
│   │
│   └── Scheduler
│       ├── Cron 작업
│       ├── 반복 작업
│       └── 지연 작업
│
├── 💾 Data Layer (무료)
│   ├── PostgreSQL
│   │   ├── 작업 테이블
│   │   ├── 로그 테이블
│   │   └── 설정 테이블
│   │
│   └── Redis
│       ├── 작업 큐
│       ├── 결과 캐시
│       └── 세션 저장소
│
└── 📊 Monitoring (무료)
    ├── Grafana 대시보드
    ├── Prometheus 메트릭
    └── Flower (Celery 모니터)
```

## 📈 데이터 흐름 시퀀스

```mermaid
sequenceDiagram
    participant U as 사용자
    participant API as FastAPI
    participant WE as 워크플로우엔진
    participant C as Claude API
    participant Q as 작업큐
    participant W as Worker
    participant DB as PostgreSQL
    
    U->>API: 작업 요청
    API->>WE: 작업 생성
    WE->>C: 분석 요청 💰
    C-->>WE: 우선순위/지시사항
    WE->>Q: 큐 등록
    Q->>W: 작업 할당
    W->>W: 작업 실행
    W->>DB: 결과 저장
    W-->>API: 완료 알림
    API-->>U: 결과 표시
```

## 🔐 보안 및 접근 제어

```mermaid
graph LR
    subgraph "외부"
        EX[🌍 인터넷]
    end
    
    subgraph "DMZ"
        NG[🛡️ Nginx<br/>리버스 프록시]
    end
    
    subgraph "애플리케이션"
        AUTH[🔐 인증 미들웨어]
        API[⚡ FastAPI]
    end
    
    subgraph "비밀 관리"
        ENV[🔑 .env 파일]
        CK[🗝️ Claude API Key]
    end
    
    EX -.->|차단| API
    EX -->|허용| NG
    NG --> AUTH
    AUTH --> API
    API --> ENV
    ENV --> CK
    
    style CK fill:#ffcccc
```

## 💡 핵심 포인트

### 🟢 무료 구성요소 (90%)
- 모든 인프라 (Docker)
- 처리 엔진 (Python)
- 데이터베이스 (PostgreSQL, Redis)
- 모니터링 (Grafana)

### 🔴 유료 구성요소 (10%)
- Claude API만 유료
- 월 $20-30 예상
- 캐싱으로 비용 최소화

### ⚡ 성능 최적화
- 배치 처리로 API 호출 감소
- 캐싱으로 중복 호출 방지
- 우선순위 기반 처리

### 🔄 확장 가능성
- 수평 확장 가능 (워커 추가)
- 다른 AI API 추가 가능
- 마이크로서비스로 전환 가능