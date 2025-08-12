"""
미션 설정 시스템
다양한 개선 목표와 작업을 정의하고 관리
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
import json
from pathlib import Path

class MissionType(Enum):
    """미션 타입"""
    SCORE_IMPROVEMENT = "score_improvement"  # 점수 향상
    SPECIFIC_ASPECT = "specific_aspect"      # 특정 측면 개선
    READER_SATISFACTION = "reader_satisfaction"  # 독자 만족도
    WORLDBUILDING = "worldbuilding"         # 세계관 강화
    CHARACTER_DEVELOPMENT = "character_development"  # 캐릭터 개발
    PLOT_ENHANCEMENT = "plot_enhancement"   # 플롯 강화
    WRITING_STYLE = "writing_style"         # 문체 개선
    GENRE_OPTIMIZATION = "genre_optimization"  # 장르 최적화
    COMPLETE_OVERHAUL = "complete_overhaul"  # 전면 개편
    CUSTOM = "custom"                        # 사용자 정의

@dataclass
class Mission:
    """미션 정의"""
    name: str
    type: MissionType
    description: str
    target_episodes: List[int]
    success_criteria: Dict[str, Any]
    priority_aspects: List[str]
    max_cycles: int = 10
    settings: Dict[str, Any] = None

class MissionLibrary:
    """사전 정의된 미션 라이브러리"""
    
    @staticmethod
    def get_preset_missions() -> Dict[str, Mission]:
        """프리셋 미션들"""
        return {
            "beginner_polish": Mission(
                name="초보자 다듬기",
                type=MissionType.SCORE_IMPROVEMENT,
                description="기본적인 품질 향상 - 문법, 오타, 기본 흐름 개선",
                target_episodes=[1, 2, 3],
                success_criteria={
                    "min_score": 7.0,
                    "grammar_score": 8.0,
                    "readability": 7.5
                },
                priority_aspects=["grammar", "readability", "flow"],
                max_cycles=5
            ),
            
            "action_intensify": Mission(
                name="액션 강화",
                type=MissionType.SPECIFIC_ASPECT,
                description="액션 씬 강화 - 전투, 긴장감, 스피드 향상",
                target_episodes=[1, 2, 3],
                success_criteria={
                    "action_reader_score": 8.0,
                    "tension_level": "high",
                    "pacing_score": 8.5
                },
                priority_aspects=["action", "tension", "pacing"],
                max_cycles=8
            ),
            
            "worldbuilding_deep": Mission(
                name="세계관 심화",
                type=MissionType.WORLDBUILDING,
                description="세계관 설정 강화 - 일관성, 깊이, 독창성",
                target_episodes=[1, 2, 3],
                success_criteria={
                    "worldbuilding_score": 9.0,
                    "consistency_check": True,
                    "originality_score": 8.5
                },
                priority_aspects=["worldbuilding", "consistency", "depth"],
                max_cycles=10
            ),
            
            "character_focus": Mission(
                name="캐릭터 집중 개발",
                type=MissionType.CHARACTER_DEVELOPMENT,
                description="캐릭터 매력도와 개성 강화",
                target_episodes=[1, 2, 3],
                success_criteria={
                    "character_score": 8.5,
                    "dialogue_quality": 8.0,
                    "character_consistency": 9.0
                },
                priority_aspects=["character", "dialogue", "personality"],
                max_cycles=7
            ),
            
            "reader_all_satisfy": Mission(
                name="모든 독자 만족",
                type=MissionType.READER_SATISFACTION,
                description="10개 독자 페르소나 모두 만족시키기",
                target_episodes=[1, 2, 3],
                success_criteria={
                    "all_readers_min_score": 7.0,
                    "average_reader_score": 8.0,
                    "no_reader_below": 6.5
                },
                priority_aspects=["balance", "variety", "appeal"],
                max_cycles=15
            ),
            
            "publication_ready": Mission(
                name="출간 준비",
                type=MissionType.COMPLETE_OVERHAUL,
                description="상업 출간 수준까지 품질 향상",
                target_episodes=[1, 2, 3],
                success_criteria={
                    "overall_score": 9.0,
                    "grammar_score": 9.5,
                    "plot_score": 8.5,
                    "character_score": 8.5,
                    "worldbuilding_score": 8.5,
                    "commercial_viability": True
                },
                priority_aspects=["all"],
                max_cycles=20
            ),
            
            "genre_perfect": Mission(
                name="장르 완벽주의",
                type=MissionType.GENRE_OPTIMIZATION,
                description="포스트 아포칼립스 판타지 장르 최적화",
                target_episodes=[1, 2, 3],
                success_criteria={
                    "genre_score": 9.0,
                    "genre_conventions": True,
                    "unique_elements": 3
                },
                priority_aspects=["genre", "atmosphere", "themes"],
                max_cycles=10
            ),
            
            "speed_run": Mission(
                name="스피드런",
                type=MissionType.SCORE_IMPROVEMENT,
                description="최단 시간 내 목표 점수 달성",
                target_episodes=[1],
                success_criteria={
                    "min_score": 8.0,
                    "time_limit_hours": 3
                },
                priority_aspects=["efficiency", "key_improvements"],
                max_cycles=3
            ),
            
            "episode_perfect": Mission(
                name="1화 완벽주의",
                type=MissionType.COMPLETE_OVERHAUL,
                description="1화만 완벽하게 만들기",
                target_episodes=[1],
                success_criteria={
                    "episode_1_score": 9.5,
                    "all_aspects_above": 8.0
                },
                priority_aspects=["all"],
                max_cycles=30
            ),
            
            "experimental": Mission(
                name="실험적 개선",
                type=MissionType.CUSTOM,
                description="AI의 창의적 해석으로 독특하게 개선",
                target_episodes=[1, 2, 3],
                success_criteria={
                    "creativity_score": 9.0,
                    "originality_score": 9.0,
                    "maintain_coherence": True
                },
                priority_aspects=["creativity", "uniqueness", "innovation"],
                max_cycles=10
            )
        }

class MissionManager:
    """미션 관리자"""
    
    def __init__(self):
        self.config_path = Path("mission_config.json")
        self.current_mission: Optional[Mission] = None
        self.mission_history = []
        
    def load_mission(self, mission_name: str = None) -> Mission:
        """미션 로드"""
        if self.config_path.exists():
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                if 'current_mission' in config:
                    return self._dict_to_mission(config['current_mission'])
        
        if mission_name:
            presets = MissionLibrary.get_preset_missions()
            if mission_name in presets:
                return presets[mission_name]
        
        # 기본 미션
        return MissionLibrary.get_preset_missions()["beginner_polish"]
    
    def save_mission(self, mission: Mission):
        """미션 저장"""
        config = {
            'current_mission': self._mission_to_dict(mission),
            'history': self.mission_history
        }
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
    
    def create_custom_mission(
        self,
        name: str,
        description: str,
        target_episodes: List[int],
        **kwargs
    ) -> Mission:
        """커스텀 미션 생성"""
        return Mission(
            name=name,
            type=MissionType.CUSTOM,
            description=description,
            target_episodes=target_episodes,
            success_criteria=kwargs.get('success_criteria', {'min_score': 8.0}),
            priority_aspects=kwargs.get('priority_aspects', ['all']),
            max_cycles=kwargs.get('max_cycles', 10),
            settings=kwargs.get('settings', {})
        )
    
    def _mission_to_dict(self, mission: Mission) -> Dict:
        """미션을 딕셔너리로 변환"""
        return {
            'name': mission.name,
            'type': mission.type.value,
            'description': mission.description,
            'target_episodes': mission.target_episodes,
            'success_criteria': mission.success_criteria,
            'priority_aspects': mission.priority_aspects,
            'max_cycles': mission.max_cycles,
            'settings': mission.settings or {}
        }
    
    def _dict_to_mission(self, data: Dict) -> Mission:
        """딕셔너리를 미션으로 변환"""
        return Mission(
            name=data['name'],
            type=MissionType(data['type']),
            description=data['description'],
            target_episodes=data['target_episodes'],
            success_criteria=data['success_criteria'],
            priority_aspects=data['priority_aspects'],
            max_cycles=data.get('max_cycles', 10),
            settings=data.get('settings')
        )
    
    def get_mission_prompt(self, mission: Mission) -> str:
        """미션을 에이전트 프롬프트로 변환"""
        prompt = f"""
# 현재 미션: {mission.name}

## 목표
{mission.description}

## 대상 에피소드
{', '.join([f"{ep}화" for ep in mission.target_episodes])}

## 성공 기준
"""
        for key, value in mission.success_criteria.items():
            prompt += f"- {key}: {value}\n"
        
        prompt += f"""
## 우선 개선 영역
{', '.join(mission.priority_aspects)}

## 최대 사이클
{mission.max_cycles}

이 미션을 달성하기 위해 각 에피소드를 체계적으로 개선해주세요.
우선 개선 영역에 특별히 집중하여 작업을 진행하세요.
"""
        return prompt
    
    def check_mission_complete(self, results: Dict[str, Any]) -> bool:
        """미션 완료 체크"""
        if not self.current_mission:
            return False
        
        criteria = self.current_mission.success_criteria
        
        # 점수 기준 체크
        if 'min_score' in criteria:
            if results.get('average_score', 0) < criteria['min_score']:
                return False
        
        # 모든 독자 만족도 체크
        if 'all_readers_min_score' in criteria:
            reader_scores = results.get('reader_scores', {})
            if any(score < criteria['all_readers_min_score'] for score in reader_scores.values()):
                return False
        
        # 특정 측면 점수 체크
        for key, target_value in criteria.items():
            if key in results:
                if isinstance(target_value, (int, float)):
                    if results[key] < target_value:
                        return False
                elif isinstance(target_value, bool):
                    if results[key] != target_value:
                        return False
        
        return True
    
    def get_progress_report(self, current_results: Dict[str, Any]) -> str:
        """미션 진행 상황 리포트"""
        if not self.current_mission:
            return "미션이 설정되지 않았습니다."
        
        report = []
        report.append(f"📋 미션: {self.current_mission.name}")
        report.append(f"설명: {self.current_mission.description}")
        report.append("")
        report.append("📊 진행 상황:")
        
        criteria = self.current_mission.success_criteria
        for key, target in criteria.items():
            current = current_results.get(key, "N/A")
            if isinstance(target, (int, float)) and isinstance(current, (int, float)):
                progress = (current / target) * 100
                status = "✅" if current >= target else "🔄"
                report.append(f"  {status} {key}: {current:.1f}/{target} ({progress:.0f}%)")
            else:
                status = "✅" if current == target else "🔄"
                report.append(f"  {status} {key}: {current}/{target}")
        
        return "\n".join(report)


# 미션 선택 헬퍼 함수
def select_mission_interactive():
    """대화형 미션 선택"""
    presets = MissionLibrary.get_preset_missions()
    
    print("\n🎯 사용 가능한 미션:")
    print("=" * 50)
    for i, (key, mission) in enumerate(presets.items(), 1):
        print(f"{i}. {mission.name}")
        print(f"   {mission.description}")
        print(f"   난이도: {'⭐' * (mission.max_cycles // 5)}")
        print()
    
    choice = input("미션 번호를 선택하세요 (또는 'custom' 입력): ")
    
    if choice.lower() == 'custom':
        return create_custom_mission_interactive()
    
    try:
        idx = int(choice) - 1
        mission_key = list(presets.keys())[idx]
        return presets[mission_key]
    except:
        print("기본 미션을 선택합니다.")
        return presets["beginner_polish"]


def create_custom_mission_interactive():
    """대화형 커스텀 미션 생성"""
    manager = MissionManager()
    
    name = input("미션 이름: ")
    description = input("미션 설명: ")
    episodes = input("대상 에피소드 (예: 1,2,3): ")
    target_score = float(input("목표 점수: "))
    max_cycles = int(input("최대 사이클: "))
    
    episodes_list = [int(x.strip()) for x in episodes.split(',')]
    
    return manager.create_custom_mission(
        name=name,
        description=description,
        target_episodes=episodes_list,
        success_criteria={'min_score': target_score},
        max_cycles=max_cycles
    )