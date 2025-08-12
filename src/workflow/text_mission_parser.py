"""
자연어 텍스트 미션 파서
사용자가 텍스트로 입력한 미션을 파싱하고 실행 가능한 형태로 변환
"""

import re
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass
import json

@dataclass
class ParsedMission:
    """파싱된 미션"""
    original_text: str
    episodes: List[int]
    action: str
    target_score: Optional[float]
    iterations: Optional[int]
    focus_areas: List[str]
    constraints: Dict[str, Any]
    
class TextMissionParser:
    """텍스트 미션 파서"""
    
    def __init__(self):
        # 미션 키워드 매핑
        self.action_keywords = {
            '개선': 'improve',
            '향상': 'enhance',
            '수정': 'fix',
            '보완': 'supplement',
            '강화': 'strengthen',
            '다듬기': 'polish',
            '완성': 'complete',
            '최적화': 'optimize',
            '리뷰': 'review',
            '분석': 'analyze'
        }
        
        self.focus_keywords = {
            '액션': 'action',
            '전투': 'combat',
            '캐릭터': 'character',
            '인물': 'character',
            '세계관': 'worldbuilding',
            '설정': 'setting',
            '문법': 'grammar',
            '오타': 'typo',
            '대화': 'dialogue',
            '묘사': 'description',
            '플롯': 'plot',
            '스토리': 'story',
            '긴장감': 'tension',
            '페이싱': 'pacing',
            '속도': 'pacing',
            '감정': 'emotion',
            '로맨스': 'romance',
            '분위기': 'atmosphere'
        }
    
    def parse(self, mission_text: str) -> ParsedMission:
        """텍스트 미션 파싱"""
        
        # 기본값
        episodes = []
        action = 'improve'
        target_score = None
        iterations = None
        focus_areas = []
        constraints = {}
        
        # 1. 에피소드 번호 추출
        episodes = self._extract_episodes(mission_text)
        
        # 2. 액션 추출
        action = self._extract_action(mission_text)
        
        # 3. 목표 점수 추출
        target_score = self._extract_target_score(mission_text)
        
        # 4. 반복 횟수 추출
        iterations = self._extract_iterations(mission_text)
        
        # 5. 집중 영역 추출
        focus_areas = self._extract_focus_areas(mission_text)
        
        # 6. 제약 조건 추출
        constraints = self._extract_constraints(mission_text)
        
        return ParsedMission(
            original_text=mission_text,
            episodes=episodes or [1, 2, 3],
            action=action,
            target_score=target_score,
            iterations=iterations,
            focus_areas=focus_areas,
            constraints=constraints
        )
    
    def _extract_episodes(self, text: str) -> List[int]:
        """에피소드 번호 추출"""
        episodes = []
        
        # 패턴 1: "1~3화", "1-3화"
        range_pattern = r'(\d+)[~\-](\d+)화'
        match = re.search(range_pattern, text)
        if match:
            start, end = int(match.group(1)), int(match.group(2))
            episodes = list(range(start, end + 1))
        
        # 패턴 2: "1,2,3화", "1, 2, 3화"
        list_pattern = r'((?:\d+,?\s*)+)화'
        if not episodes:
            match = re.search(list_pattern, text)
            if match:
                numbers = re.findall(r'\d+', match.group(1))
                episodes = [int(n) for n in numbers]
        
        # 패턴 3: "1화", "첫화", "첫 화"
        single_pattern = r'(\d+)화|첫\s?화|처음'
        if not episodes:
            if '첫' in text or '처음' in text:
                episodes = [1]
            else:
                match = re.search(single_pattern, text)
                if match and match.group(1):
                    episodes = [int(match.group(1))]
        
        # 패턴 4: "전체", "모든"
        if '전체' in text or '모든' in text:
            episodes = [1, 2, 3]  # 기본 전체
        
        return episodes
    
    def _extract_action(self, text: str) -> str:
        """액션 추출"""
        for korean, english in self.action_keywords.items():
            if korean in text:
                return english
        return 'improve'  # 기본값
    
    def _extract_target_score(self, text: str) -> Optional[float]:
        """목표 점수 추출"""
        
        # 패턴: "8.5점", "9점", "8.5점까지"
        score_pattern = r'(\d+(?:\.\d+)?)\s?점'
        match = re.search(score_pattern, text)
        if match:
            return float(match.group(1))
        
        # 패턴: "80%", "90%"
        percent_pattern = r'(\d+)\s?%'
        match = re.search(percent_pattern, text)
        if match:
            return float(match.group(1)) / 10  # 100% = 10점
        
        return None
    
    def _extract_iterations(self, text: str) -> Optional[int]:
        """반복 횟수 추출"""
        
        # 패턴: "10번", "5회", "3번 반복"
        iteration_pattern = r'(\d+)\s?[번회]\s?(?:반복)?'
        match = re.search(iteration_pattern, text)
        if match:
            return int(match.group(1))
        
        # 키워드 기반
        if '무한' in text or '계속' in text:
            return 999  # 무한 반복
        elif '한번' in text or '한 번' in text:
            return 1
        
        return None
    
    def _extract_focus_areas(self, text: str) -> List[str]:
        """집중 영역 추출"""
        areas = []
        
        for korean, english in self.focus_keywords.items():
            if korean in text:
                if english not in areas:
                    areas.append(english)
        
        # 특별 조합
        if '액션' in text and '씬' in text:
            areas.append('action_scenes')
        if '캐릭터' in text and '개발' in text:
            areas.append('character_development')
        if '세계관' in text and '설정' in text:
            areas.append('worldbuilding_consistency')
        
        return areas
    
    def _extract_constraints(self, text: str) -> Dict[str, Any]:
        """제약 조건 추출"""
        constraints = {}
        
        # 시간 제약
        time_pattern = r'(\d+)\s?시간\s?(?:이내|안에)?'
        match = re.search(time_pattern, text)
        if match:
            constraints['time_limit_hours'] = int(match.group(1))
        
        # 최소/최대 조건
        if '최소' in text:
            constraints['minimum_improvement'] = True
        if '최대' in text:
            constraints['maximum_effort'] = True
        
        # 특별 조건
        if '빠르게' in text or '신속' in text:
            constraints['speed_priority'] = True
        if '꼼꼼' in text or '정밀' in text:
            constraints['quality_priority'] = True
        if '균형' in text:
            constraints['balanced_approach'] = True
        
        return constraints
    
    def to_mission_config(self, parsed: ParsedMission) -> Dict[str, Any]:
        """파싱 결과를 미션 설정으로 변환"""
        
        # 기본 설정
        config = {
            'name': f"텍스트 미션: {parsed.original_text[:30]}",
            'type': 'text_based',
            'description': parsed.original_text,
            'target_episodes': parsed.episodes,
            'action': parsed.action,
            'priority_aspects': parsed.focus_areas or ['general'],
            'settings': {}
        }
        
        # 성공 기준 설정
        success_criteria = {}
        if parsed.target_score:
            success_criteria['min_score'] = parsed.target_score
        
        if parsed.focus_areas:
            for area in parsed.focus_areas:
                success_criteria[f'{area}_score'] = (parsed.target_score or 8.0) - 0.5
        
        config['success_criteria'] = success_criteria
        
        # 반복 설정
        if parsed.iterations:
            config['max_cycles'] = parsed.iterations
        else:
            # 목표 점수에 따른 자동 설정
            if parsed.target_score:
                if parsed.target_score >= 9.0:
                    config['max_cycles'] = 15
                elif parsed.target_score >= 8.0:
                    config['max_cycles'] = 10
                else:
                    config['max_cycles'] = 5
            else:
                config['max_cycles'] = 10
        
        # 제약 조건 적용
        if parsed.constraints:
            config['constraints'] = parsed.constraints
            
            if 'time_limit_hours' in parsed.constraints:
                # 시간당 2사이클 가정
                max_cycles_by_time = parsed.constraints['time_limit_hours'] * 2
                config['max_cycles'] = min(config['max_cycles'], max_cycles_by_time)
            
            if 'speed_priority' in parsed.constraints:
                config['settings']['quick_mode'] = True
            
            if 'quality_priority' in parsed.constraints:
                config['settings']['thorough_mode'] = True
        
        return config


class MissionExecutor:
    """텍스트 미션 실행기"""
    
    def __init__(self):
        self.parser = TextMissionParser()
    
    def execute_text_mission(self, mission_text: str) -> Dict[str, Any]:
        """텍스트 미션 실행"""
        
        # 미션 파싱
        parsed = self.parser.parse(mission_text)
        
        # 미션 설정 생성
        config = self.parser.to_mission_config(parsed)
        
        print(f"📝 텍스트 미션 해석:")
        print(f"   원문: {mission_text}")
        print(f"   대상: {parsed.episodes}화")
        print(f"   액션: {parsed.action}")
        if parsed.target_score:
            print(f"   목표: {parsed.target_score}점")
        if parsed.iterations:
            print(f"   반복: {parsed.iterations}회")
        if parsed.focus_areas:
            print(f"   집중: {', '.join(parsed.focus_areas)}")
        
        return config
    
    def suggest_mission(self, context: str) -> List[str]:
        """상황에 맞는 미션 제안"""
        suggestions = []
        
        if '처음' in context or '시작' in context:
            suggestions.extend([
                "1~3화 기본 개선",
                "1화 문법 오타 수정",
                "전체 에피소드 7점까지 향상"
            ])
        
        elif '액션' in context or '전투' in context:
            suggestions.extend([
                "1~3화 액션씬 강화",
                "2화 전투 장면 보완",
                "전체 긴장감 향상"
            ])
        
        elif '캐릭터' in context or '인물' in context:
            suggestions.extend([
                "1화 캐릭터 개발",
                "전체 대화 개선",
                "주인공 매력도 강화"
            ])
        
        elif '빠르게' in context or '급하' in context:
            suggestions.extend([
                "1화 3시간 내 개선",
                "1~2화 빠른 수정",
                "1화 최소 개선"
            ])
        
        else:
            suggestions.extend([
                "1~3화 반복 개선",
                "전체 8.5점까지 향상",
                "1화 완벽하게 다듬기"
            ])
        
        return suggestions


# 예제 사용법
if __name__ == "__main__":
    executor = MissionExecutor()
    
    # 다양한 텍스트 미션 예제
    examples = [
        "1~3화 반복 개선",
        "1화 액션씬 강화하고 9점까지 올려줘",
        "전체 에피소드 문법 오타 수정",
        "2화 캐릭터 대화 10번 반복 개선",
        "첫화를 3시간 안에 8.5점까지",
        "모든 화 세계관 설정 보완",
        "1,2,3화 빠르게 기본 개선",
        "1화부터 3화까지 긴장감 있게 수정"
    ]
    
    for mission_text in examples:
        print("\n" + "="*50)
        config = executor.execute_text_mission(mission_text)
        print(f"   설정: {json.dumps(config, indent=2, ensure_ascii=False)[:200]}...")