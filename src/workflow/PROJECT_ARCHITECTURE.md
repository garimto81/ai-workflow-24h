# 📚 24시간 웹소설 자동 생성 프로젝트

## 🎯 프로젝트 개요
10개의 AI 에이전트가 협업하여 24시간 자동으로 웹소설을 생성, 검수, 개선하는 시스템

---

## 🏗️ 시스템 아키텍처

```
┌──────────────────────────────────────────────┐
│              📁 문서 감시 시스템                │
│         (파일 변경 감지 & 트리거)              │
└────────────────┬─────────────────────────────┘
                 │
    ┌────────────▼────────────┐
    │   🎯 메인 에이전트        │
    │   (작업 할당 & 조정)      │
    └────┬──────────────┬──────┘
         │              │
    ┌────▼────┐    ┌───▼────┐
    │ PM 에이전트│    │작업 큐  │
    │ (감독)    │    │        │
    └─────────┘    └────┬────┘
                        │
    ┌───────────────────┼───────────────────┐
    │                   │                   │
┌───▼───┐  ┌───────┐  ┌▼──────┐  ┌────────┐
│작가    │  │세계관  │  │역사    │  │역사개선 │
│에이전트│  │담당    │  │담당    │  │에이전트 │
└───┬───┘  └───┬───┘  └───┬───┘  └────┬───┘
    │          │           │            │
    └──────────┼───────────┼────────────┘
               │           │
    ┌──────────┼───────────┼──────────┐
    │          │           │          │
┌───▼───┐  ┌──▼───┐  ┌───▼───┐  ┌───▼───┐
│문법    │  │AI화법 │  │독자    │  │QA     │
│담당    │  │감지   │  │담당×N  │  │담당   │
└───────┘  └──────┘  └───────┘  └───────┘
```

---

## 📋 에이전트 상세 명세

### 1. 🎯 메인 에이전트 (Main Orchestrator)
```python
class MainAgent:
    """전체 워크플로우 관리"""
    
    역할:
    - 문서 변경 감지 및 읽기
    - 작업 유형 판단
    - 적절한 에이전트에게 작업 할당
    - 결과 수집 및 다음 단계 결정
    
    처리 플로우:
    1. 문서 변경/생성 감지
    2. 문서 내용 분석
    3. 작업 큐 생성
    4. 에이전트별 작업 할당
    5. 결과 통합
```

### 2. 📊 PM 에이전트 (Project Manager)
```python
class PMAgent:
    """작업 진행 상황 감독"""
    
    역할:
    - 각 에이전트 작업 상태 모니터링
    - 지연/문제 발생시 메인에게 보고
    - 작업 우선순위 조정 제안
    - 품질 기준 충족 여부 확인
```

### 3. ✍️ 작가 에이전트 (Writer)
```python
class WriterAgent:
    """웹소설 집필"""
    
    입력:
    - 이전 화 내용
    - 세계관 설정
    - 독자 피드백
    
    출력:
    - 새로운 에피소드 (3000자)
    - 챕터 요약
    - 다음 화 예고
```

### 4. 🌍 세계관 담당 에이전트 (Worldbuilding)
```python
class WorldbuildingAgent:
    """세계관 일관성 검증"""
    
    메모리:
    - 전체 세계관 문서
    - 캐릭터 설정
    - 지역/마법 체계
    
    검수 항목:
    - 설정 충돌 여부
    - 캐릭터 일관성
    - 세계관 규칙 위반
```

### 5. 📜 역사 담당 에이전트 (History)
```python
class HistoryAgent:
    """스토리 역사 일관성 검증"""
    
    메모리:
    - 모든 이전 에피소드
    - 주요 사건 타임라인
    - 캐릭터 행적
    
    검수 항목:
    - 시간선 모순
    - 사건 인과관계
    - 캐릭터 기억/경험
```

### 6. 🔄 역사 개선 에이전트 (History Improver)
```python
class HistoryImproverAgent:
    """역사 vs 신규 내용 비교 및 개선"""
    
    판단 기준:
    - 스토리 개연성
    - 독자 몰입도
    - 전개 자연스러움
    
    권한:
    - 기존 역사 수정 제안
    - 설정 변경 승인
```

### 7. 📝 문법 담당 에이전트 (Grammar)
```python
class GrammarAgent:
    """문장 품질 검수"""
    
    검사 항목:
    - 맞춤법/띄어쓰기
    - 문장 자연스러움
    - 가독성
    - 문단 구성
```

### 8. 🤖 AI 화법 감지 에이전트 (AI Detection)
```python
class AIDetectionAgent:
    """AI 특유 문체 감지"""
    
    감지 패턴:
    - 짧은 설명문 나열
    - 과도한 부사 사용
    - 반복적 문장 구조
    - 감정 표현 부족
    
    출력:
    - 수정 필요 부분 표시
    - 개선 제안
```

### 9. 👥 독자 담당 에이전트 (Reader) × N명
```python
class ReaderAgent:
    """독자 관점 평가"""
    
    페르소나:
    - 연령대 (10대/20대/30대)
    - 선호 장르
    - 읽기 스타일
    
    평가 항목:
    - 재미도 (1-10점)
    - 몰입도
    - 다음 화 기대감
    - 개선 요청사항
```

### 10. ✅ QA 담당 에이전트 (Quality Assurance)
```python
class QAAgent:
    """최종 품질 검증"""
    
    체크리스트:
    - 모든 검수 통과 여부
    - 전체 완성도 점수
    - 발행 가능 여부
    - 개선 우선순위
```

---

## 🔄 작업 플로우

### Option A: 파일 감시 기반
```python
async def file_watch_workflow():
    """파일 변경 감지 → 처리"""
    
    while True:
        # 1. 파일 변경 감지
        if file_changed("drafts/"):
            
            # 2. 메인 에이전트 활성화
            content = main_agent.read_file()
            
            # 3. 작업 유형 판단
            task_type = main_agent.analyze(content)
            
            # 4. 에이전트 할당
            if task_type == "new_episode":
                await process_new_episode(content)
            elif task_type == "revision":
                await process_revision(content)
        
        await asyncio.sleep(1)  # 1초마다 체크
```

### Option B: 에이전트 체인 기반
```python
async def agent_chain_workflow():
    """에이전트 순차 처리"""
    
    # 1. 작가 에이전트
    episode = await writer_agent.create()
    
    # 2. 세계관 검수
    world_check = await worldbuilding_agent.verify(episode)
    
    # 3. 역사 검수
    history_check = await history_agent.verify(episode)
    
    # 4. 역사 개선 판단
    if history_improver.should_update(episode, history):
        history = await history_improver.update()
    
    # 5. 문법 검수
    grammar_check = await grammar_agent.check(episode)
    
    # 6. AI 화법 검사
    ai_detection = await ai_detection_agent.scan(episode)
    
    # 7. 독자 평가 (병렬)
    reader_reviews = await asyncio.gather(
        *[reader.review(episode) for reader in reader_agents]
    )
    
    # 8. QA 최종 검증
    final_result = await qa_agent.validate_all()
    
    # 9. 메인 에이전트에게 보고
    await main_agent.receive_results(final_result)
```

---

## 📁 폴더 구조

```
webnovel-automation/
│
├── agents/                 # 에이전트 코드
│   ├── main_agent.py
│   ├── pm_agent.py
│   ├── writer_agent.py
│   ├── worldbuilding_agent.py
│   ├── history_agent.py
│   ├── grammar_agent.py
│   ├── ai_detection_agent.py
│   ├── reader_agent.py
│   └── qa_agent.py
│
├── documents/             # 문서 저장소
│   ├── worldbuilding/    # 세계관 설정
│   ├── history/          # 역사/타임라인
│   ├── episodes/         # 완성된 에피소드
│   ├── drafts/           # 작업 중 초안
│   └── reviews/          # 리뷰/피드백
│
├── memory/               # 에이전트 메모리
│   ├── world_memory.json
│   ├── history_memory.json
│   └── character_memory.json
│
├── config/              # 설정 파일
│   ├── agents.yaml     # 에이전트 설정
│   ├── workflow.yaml   # 워크플로우 설정
│   └── api_keys.env    # API 키
│
└── logs/               # 로그 파일
    ├── agent_logs/
    └── api_usage.log
```

---

## 🔑 Claude API 한도 관리

```python
class ClaudeAPIManager:
    """API 사용량 관리"""
    
    def __init__(self):
        self.daily_limit = 1000000  # 토큰
        self.used_today = 0
        self.rate_limit = 50  # 요청/분
        
    async def request(self, prompt):
        """API 요청 with 한도 체크"""
        
        # 1. 일일 한도 체크
        if self.used_today >= self.daily_limit:
            await self.wait_until_tomorrow()
        
        # 2. 분당 한도 체크
        if self.current_rate >= self.rate_limit:
            await asyncio.sleep(60)
        
        # 3. 요청 실행
        try:
            response = await claude_api.complete(prompt)
            self.used_today += count_tokens(response)
            return response
            
        except RateLimitError:
            # 한도 도달시 대기
            await asyncio.sleep(300)  # 5분 대기
            return await self.request(prompt)  # 재시도
```

---

## 📊 에이전트 통신 프로토콜

```python
class AgentMessage:
    """에이전트 간 메시지 포맷"""
    
    def __init__(self):
        self.sender: str        # 발신 에이전트
        self.receiver: str      # 수신 에이전트
        self.task_id: str       # 작업 ID
        self.content: dict      # 실제 내용
        self.priority: int      # 우선순위
        self.timestamp: datetime
        
class MessageQueue:
    """에이전트 메시지 큐"""
    
    def __init__(self):
        self.queues = {
            agent: asyncio.Queue() 
            for agent in ALL_AGENTS
        }
    
    async def send(self, message: AgentMessage):
        """메시지 전송"""
        queue = self.queues[message.receiver]
        await queue.put(message)
    
    async def receive(self, agent_name: str):
        """메시지 수신"""
        queue = self.queues[agent_name]
        return await queue.get()
```

---

## 🚀 실행 플로우

### 1. 시스템 초기화
```python
# 모든 에이전트 초기화
agents = initialize_all_agents()

# 메모리 로드
load_worldbuilding_memory()
load_history_memory()

# 파일 감시 시작
start_file_watcher()
```

### 2. 새 에피소드 생성
```python
# 매일 정해진 시간에 실행
schedule.every().day.at("02:00").do(create_new_episode)
```

### 3. 검수 파이프라인
```python
# 순차적 검수 진행
episode → 세계관 → 역사 → 문법 → AI감지 → 독자평가 → QA → 발행
```

이제 구현을 시작할까요?