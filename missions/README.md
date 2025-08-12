# 🎯 미션 시스템 가이드

## 📋 미션이란?

미션은 **특정 목표를 달성하기 위한 작업 세트**입니다. 단순히 "점수 올리기"가 아닌, 구체적인 개선 목표를 설정할 수 있습니다.

## 🎮 사전 정의된 미션들

### 1. 🌱 **초보자 다듬기** (beginner_polish)
- **목표**: 기본적인 품질 향상
- **초점**: 문법, 오타, 기본 흐름
- **난이도**: ⭐
- **최대 사이클**: 5
- **추천 대상**: 첫 개선 시작하는 분

### 2. ⚔️ **액션 강화** (action_intensify)
- **목표**: 액션 씬 강화
- **초점**: 전투, 긴장감, 스피드
- **난이도**: ⭐⭐
- **최대 사이클**: 8
- **추천 대상**: 액션 장면이 부족한 작품

### 3. 🌍 **세계관 심화** (worldbuilding_deep)
- **목표**: 세계관 설정 강화
- **초점**: 일관성, 깊이, 독창성
- **난이도**: ⭐⭐
- **최대 사이클**: 10
- **추천 대상**: 판타지/SF 작품

### 4. 👥 **캐릭터 집중 개발** (character_focus)
- **목표**: 캐릭터 매력도 강화
- **초점**: 대화, 개성, 일관성
- **난이도**: ⭐⭐
- **최대 사이클**: 7
- **추천 대상**: 캐릭터 중심 스토리

### 5. 📊 **모든 독자 만족** (reader_all_satisfy)
- **목표**: 10개 페르소나 모두 만족
- **초점**: 균형, 다양성, 매력
- **난이도**: ⭐⭐⭐
- **최대 사이클**: 15
- **추천 대상**: 대중성 확보 필요

### 6. 📚 **출간 준비** (publication_ready)
- **목표**: 상업 출간 수준
- **초점**: 모든 측면 고품질
- **난이도**: ⭐⭐⭐⭐
- **최대 사이클**: 20
- **추천 대상**: 실제 출간 예정 작품

### 7. 🎯 **장르 완벽주의** (genre_perfect)
- **목표**: 장르 특성 극대화
- **초점**: 장르 관습, 독특함
- **난이도**: ⭐⭐⭐
- **최대 사이클**: 10
- **추천 대상**: 장르물 작품

### 8. ⚡ **스피드런** (speed_run)
- **목표**: 빠른 개선
- **초점**: 효율성, 핵심 개선
- **난이도**: ⭐
- **최대 사이클**: 3
- **추천 대상**: 시간 제한 있는 경우

### 9. 💎 **1화 완벽주의** (episode_perfect)
- **목표**: 1화만 완벽하게
- **초점**: 모든 측면
- **난이도**: ⭐⭐⭐⭐⭐
- **최대 사이클**: 30
- **추천 대상**: 첫인상이 중요한 경우

### 10. 🔬 **실험적 개선** (experimental)
- **목표**: 창의적 재해석
- **초점**: 독창성, 혁신
- **난이도**: ⭐⭐⭐
- **최대 사이클**: 10
- **추천 대상**: 새로운 시도

## 🚀 미션 실행 방법

### GitHub Actions에서 실행

1. **Actions 탭** → **Mission-Based Automation**
2. **Run workflow** 클릭
3. **미션 선택** (드롭다운)
4. **Run workflow** 버튼 클릭

### 로컬에서 실행

```python
from mission_config import MissionManager, MissionLibrary

# 미션 선택
manager = MissionManager()
mission = manager.load_mission("action_intensify")

# 미션 실행
python run_mission.py --mission action_intensify
```

## 🎨 커스텀 미션 만들기

### 방법 1: JSON으로 정의

```json
{
  "name": "나만의 미션",
  "type": "custom",
  "description": "특별한 목표를 위한 미션",
  "target_episodes": [1, 2],
  "success_criteria": {
    "min_score": 8.5,
    "special_requirement": true
  },
  "priority_aspects": ["my_focus"],
  "max_cycles": 12
}
```

### 방법 2: Python 코드로

```python
from mission_config import MissionManager

manager = MissionManager()
custom_mission = manager.create_custom_mission(
    name="나만의 미션",
    description="특별한 목표",
    target_episodes=[1, 2, 3],
    success_criteria={
        'min_score': 8.5,
        'reader_satisfaction': 8.0
    },
    priority_aspects=['dialogue', 'action'],
    max_cycles=10
)
```

## 📊 성공 기준 옵션

### 점수 기반
- `min_score`: 최소 평균 점수
- `all_episodes_above`: 모든 에피소드 최소 점수
- `grammar_score`: 문법 점수
- `worldbuilding_score`: 세계관 점수

### 독자 만족도
- `all_readers_min_score`: 모든 독자 최소 점수
- `average_reader_score`: 평균 독자 점수
- `specific_reader_score`: 특정 독자 점수

### 특별 조건
- `improvements_per_cycle`: 사이클당 개선 수
- `consistency_check`: 일관성 체크
- `originality_score`: 독창성 점수

## 💡 미션 선택 가이드

### 처음 시작하는 경우
1. **초보자 다듬기** → 기본 품질 확보
2. **액션 강화** or **캐릭터 집중** → 특정 측면 강화
3. **모든 독자 만족** → 균형 잡기
4. **출간 준비** → 최종 다듬기

### 특정 문제가 있는 경우
- 지루함 → **액션 강화**
- 캐릭터 빈약 → **캐릭터 집중 개발**
- 세계관 부실 → **세계관 심화**
- 장르 특성 부족 → **장르 완벽주의**

### 시간별 추천
- 1시간 이내 → **스피드런**
- 3시간 → **초보자 다듬기**
- 6시간 → **액션 강화**, **캐릭터 집중**
- 12시간+ → **출간 준비**, **모든 독자 만족**

## 📈 미션 진행 모니터링

### 실시간 확인
```bash
# 미션 상태 확인
cat mission_config.json

# 진행 로그
tail -f logs/mission_progress.log
```

### GitHub Actions에서
- Actions 탭에서 실행 중인 워크플로우 클릭
- Summary에서 전체 진행 상황 확인

## 🏆 미션 달성 보상

각 미션 완료 시:
1. 상세한 개선 리포트 생성
2. Before/After 비교 문서
3. 달성 배지 (GitHub)
4. 다음 추천 미션 제안

## ❓ FAQ

**Q: 미션을 중간에 변경할 수 있나요?**
A: 네, 새로운 미션으로 워크플로우를 다시 시작하면 됩니다.

**Q: 여러 미션을 동시에 실행할 수 있나요?**
A: 각 미션은 독립적으로 실행됩니다. 병렬 실행 가능합니다.

**Q: 미션이 실패하면?**
A: 최대 사이클까지 도달해도 목표 미달성 시 리포트와 개선 제안을 제공합니다.

**Q: 커스텀 미션 공유 가능한가요?**
A: missions/ 폴더에 JSON 파일로 저장하여 공유할 수 있습니다.