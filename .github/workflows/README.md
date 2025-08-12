# 📋 GitHub Actions 워크플로우 가이드

## ⚡ 시스템 상태 (2025-08-12 현재)
- 🟢 **시스템**: 완전 운영 중
- 🟢 **11개 AI 에이전트**: 모든 에이전트 정상 작동
- 🟢 **Classic Isekai 연동**: Private 저장소 연결 완료
- 🟢 **Config 경로 문제**: 해결 완료 (자동 경로 탐지)
- 🟢 **테스트 통과율**: 100%

## 🎯 메인 워크플로우 (사용 권장)

### ✅ `classic-isekai-automation.yml` - 메인 시스템 🚀
**11개 AI 에이전트가 협력하는 완전 자동화 웹소설 개선 시스템**

**주요 특징:**
- 🤖 11개 전문 AI 에이전트 협력
- 🔗 Classic Isekai Private 저장소 연동
- 📊 품질 점수 기반 자동 개선
- 🎯 목표 달성까지 자동 반복
- 🔒 보안 강화된 Private 저장소 접근

#### 지원 모드:
1. **text** - 텍스트 미션 (예: "1~3화 반복 개선")
2. **continuous** - 연속 실행 (목표까지 자동 반복)
3. **single** - 단일 사이클 실행
4. **preset** - 사전 정의 미션

#### 트리거 방법:
- 수동 실행 (workflow_dispatch)
- 스케줄 (6시간마다)
- Issue 생성/수정
- Issue 댓글 (/mission 명령)
- 자동 연속 실행

---

## 📚 레거시 워크플로우 (참고용)

다음 워크플로우들은 **main-automation.yml**에 통합되었습니다:

### 1. `webnovel-automation.yml`
- **용도**: 초기 버전, 기본 자동화
- **상태**: ⚠️ Deprecated
- **대체**: main-automation.yml의 single 모드

### 2. `webnovel-automation-continuous.yml`
- **용도**: 연속 사이클 실행
- **상태**: ⚠️ Deprecated
- **대체**: main-automation.yml의 continuous 모드

### 3. `monitor-automation.yml`
- **용도**: 시스템 모니터링
- **상태**: ⚠️ Deprecated
- **대체**: main-automation.yml의 schedule 트리거

### 4. `mission-based-automation.yml`
- **용도**: 프리셋 미션 실행
- **상태**: ⚠️ Deprecated
- **대체**: main-automation.yml의 preset 모드

### 5. `text-mission-automation.yml`
- **용도**: 텍스트 미션 파싱
- **상태**: ⚠️ Deprecated
- **대체**: main-automation.yml의 text 모드

---

## 🚀 빠른 시작

### 📋 필수 준비사항
1. **ANTHROPIC_API_KEY** - Claude API 키 설정
2. **CLASSIC_ISEKAI_TOKEN** - Private 저장소 접근 토큰

### 🎯 가장 쉬운 실행 방법:
```
1. Actions 탭 이동
2. "🚀 Classic Isekai 웹소설 개선" 선택
3. "Run workflow" 클릭
4. 설정 입력:
   - 미션: "1~3화 반복 개선" 
   - 목표 점수: "8.5"
   - Create PR: "false" (직접 커밋)
5. "Run workflow" 버튼 클릭
6. Actions 로그에서 실시간 진행상황 확인
```

### 텍스트 미션 예시:
- `1~3화 반복 개선`
- `1화 액션씬 강화하고 9점까지`
- `전체 문법 오타 수정`
- `2화 캐릭터 대화 10번 반복`

### 연속 실행:
- 모드: continuous
- 목표 점수 달성까지 자동 반복

---

## 🗑️ 정리 방법

레거시 워크플로우 삭제하려면:

```bash
# 로컬에서
cd .github/workflows
rm webnovel-automation.yml
rm webnovel-automation-continuous.yml
rm monitor-automation.yml
rm mission-based-automation.yml
rm text-mission-automation.yml

# 커밋
git add -A
git commit -m "cleanup: Remove deprecated workflows"
git push
```

또는 GitHub에서 직접:
1. `.github/workflows` 폴더 이동
2. 각 파일 옆 ... 클릭
3. Delete file 선택

---

## 📊 워크플로우 비교표

| 기능 | main-automation.yml | 레거시 워크플로우들 |
|-----|-------------------|-----------------|
| 텍스트 미션 | ✅ text 모드 | text-mission-automation.yml |
| 연속 실행 | ✅ continuous 모드 | webnovel-automation-continuous.yml |
| 프리셋 미션 | ✅ preset 모드 | mission-based-automation.yml |
| 모니터링 | ✅ schedule | monitor-automation.yml |
| 단일 실행 | ✅ single 모드 | webnovel-automation.yml |
| Issue 연동 | ✅ 지원 | 일부만 지원 |
| 통합 관리 | ✅ 하나로 통합 | ❌ 분산 |

---

## 💡 권장사항

1. **main-automation.yml만 사용**하세요
2. 레거시 워크플로우는 **참고용**으로만 보관
3. 필요시 레거시 워크플로우 **삭제** 권장
4. 모든 새 기능은 main-automation.yml에 추가

---

## ❓ FAQ

**Q: 왜 하나로 통합했나요?**
A: 관리 편의성과 일관성을 위해 통합했습니다.

**Q: 기존 워크플로우를 삭제해도 되나요?**
A: 네, main-automation.yml이 모든 기능을 포함합니다.

**Q: 특정 기능만 필요한데?**
A: main-automation.yml에서 원하는 모드만 선택하면 됩니다.