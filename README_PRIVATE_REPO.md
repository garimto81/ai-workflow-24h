# 🔐 Classic Isekai Private 저장소 연결 완료

## 📋 현재 상태

✅ **시스템 구성 완료**
- AI Workflow 시스템과 Classic Isekai private 저장소 연결 준비 완료
- 11개 에이전트 시스템 구현 완료
- 텍스트 미션 파서 구현 완료
- GitHub Actions 워크플로우 설정 완료

## 🚀 빠른 시작 가이드

### 1️⃣ Personal Access Token 설정

#### 자동 설정 (추천)
```bash
python setup_private_repo.py
```

#### 수동 설정
1. GitHub.com → Settings → Developer settings → Personal access tokens
2. "Generate new token (classic)" 클릭
3. Scopes: ✅ repo (전체)
4. Token 복사 (ghp_xxxx...)

### 2️⃣ 토큰 저장

#### GitHub Actions용 (온라인 실행)
1. ai-workflow-24h 저장소 → Settings → Secrets → Actions
2. "New repository secret"
3. Name: `CLASSIC_ISEKAI_TOKEN`
4. Value: [복사한 토큰]

#### 로컬 테스트용
```bash
# Windows
set CLASSIC_ISEKAI_TOKEN=ghp_xxxxx

# Mac/Linux
export CLASSIC_ISEKAI_TOKEN=ghp_xxxxx
```

### 3️⃣ 연결 테스트

```bash
python test_private_repo_connection.py
```

성공 시 출력:
```
✅ 저장소 접근 성공
✅ 3개 에피소드 발견
✅ 모든 테스트 통과!
```

## 📁 파일 구조

```
ai-workflow-24h/
├── setup_private_repo.py          # 설정 도우미
├── test_private_repo_connection.py # 연결 테스트
├── src/workflow/
│   ├── repository_connector.py     # Classic Isekai 연결자
│   ├── text_mission_parser.py      # 미션 파서
│   └── new_agent_system.py         # 11개 에이전트 시스템
├── .github/workflows/
│   ├── classic-isekai-automation.yml # Private repo 전용
│   └── main-automation.yml           # 통합 워크플로우
└── docs/
    ├── PRIVATE_REPO_SETUP.md        # 상세 설정 가이드
    └── CLASSIC_ISEKAI_INTEGRATION.md # 연동 가이드
```

## 🎯 사용 방법

### GitHub Actions에서 실행

1. Actions 탭 → "🚀 Classic Isekai 웹소설 개선"
2. Run workflow 클릭
3. 설정:
   - 미션: `1~3화 반복 개선`
   - 목표 점수: `8.5`
   - PR 생성: `false` (직접 커밋) 또는 `true` (PR 생성)

### 지원되는 미션 예시

- `1~3화 반복 개선` - 1,2,3화를 반복 개선
- `1화 액션씬 강화` - 1화의 액션 장면 개선
- `2화 캐릭터 대화 개선` - 2화의 대화 향상
- `전체 문법 오타 수정` - 모든 에피소드 교정

## 🔧 트러블슈팅

### "Bad credentials" 오류
```bash
# 토큰 확인
echo %CLASSIC_ISEKAI_TOKEN%  # Windows
echo $CLASSIC_ISEKAI_TOKEN   # Mac/Linux

# 토큰 재생성 필요 시
python setup_private_repo.py
```

### "Repository not found" 오류
- 토큰에 repo 권한이 있는지 확인
- 저장소가 private인지 확인
- 저장소 이름이 정확한지 확인

### 에피소드를 찾을 수 없음
- Classic Isekai 저장소의 `webnovel_episodes/` 폴더 확인
- 파일명 형식: `XXX_에피소드_X화.md`

## 📊 시스템 구성

### 11개 에이전트
1. **메인 코디네이터** - 전체 조율
2. **작가 에이전트** - 문장 개선
3. **문법/오탈자 에이전트** - 교정
4. **세계관 에이전트** - 세계관 일관성
5. **역사 에이전트** - 스토리 연속성
6. **독자 에이전트** (10명) - 다각도 평가
7. **연관성 에이전트** - 에피소드 간 연결
8. **개선 에이전트** - 세계관/역사 업데이트
9-11. **시스템 에이전트** - 통계, 로깅, QA

### 개선 프로세스 (35분/에피소드)
1. 초기 분석 (2분)
2. 병렬 리뷰 (15분)
3. 통합 (5분)
4. 개선 작업 (10분)
5. 저장 (3분)

## 📈 예상 결과

- 에피소드당 평균 1.2점 향상
- 10개 관점에서의 균형잡힌 개선
- 세계관 일관성 유지
- 자동 커밋 또는 PR 생성

## 🔒 보안 주의사항

- ❌ 토큰을 코드에 직접 입력 금지
- ❌ 토큰을 커밋에 포함 금지
- ✅ Secrets 또는 환경 변수 사용
- ✅ .env 파일은 .gitignore에 추가

## 📞 지원

문제 발생 시:
- [AI Workflow Issues](https://github.com/garimto81/ai-workflow-24h/issues)
- [Classic Isekai Issues](https://github.com/garimto81/classic-isekai/issues)

## ✅ 체크리스트

- [ ] PAT 토큰 생성
- [ ] CLASSIC_ISEKAI_TOKEN Secret 설정
- [ ] 연결 테스트 통과
- [ ] 첫 미션 실행
- [ ] 개선 결과 확인

---

**준비 완료!** 이제 GitHub Actions에서 실행하거나 로컬에서 테스트할 수 있습니다.