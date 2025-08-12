"""
설정 개선 에이전트 (Setting Improvement Agent)
더 나은 세계관 및 역사 요소 감지시 기존 설정을 개선하는 에이전트
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List

from .base_agent import BaseAgent
from .project_loader import project_loader

logger = logging.getLogger(__name__)


class SettingImprovementAgent(BaseAgent):
    """설정 개선 에이전트"""
    
    def __init__(self):
        super().__init__("SettingImprovement")
        self.improvement_patterns = {}
        self.enhancement_suggestions = {}
    
    async def initialize(self):
        """설정 개선 에이전트 초기화"""
        logger.info("설정 개선 에이전트 초기화")
        
        # 개선 패턴 정의
        self.improvement_patterns = {
            'new_world_elements': ['새로운 지역', '새로운 능력', '새로운 규칙'],
            'character_depth': ['배경 스토리', '동기', '관계성'],
            'system_enhancement': ['능력 확장', '제약 조건', '부작용']
        }
        
        logger.info("설정 개선 에이전트 초기화 완료")
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """작업 실행"""
        task_type = task.get('type')
        
        if task_type == 'scan_for_improvements':
            return await self.scan_for_improvements(task)
        else:
            return {"error": f"Unknown task type: {task_type}"}
    
    async def scan_for_improvements(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """개선점 스캔"""
        episode_num = task.get('episode_number')
        
        # 에피소드 내용 로드
        content = project_loader.get_episode_content(episode_num)
        if not content:
            return {"error": f"에피소드 {episode_num}화를 찾을 수 없습니다"}
        
        logger.info(f"🔍 설정 개선 에이전트: {episode_num}화 개선점 탐지")
        
        # 새로운 세계관 요소 감지
        new_elements = self.detect_new_world_elements(content)
        
        # 설정 확장 가능성 체크
        expansion_opportunities = self.check_expansion_opportunities(content)
        
        # 개선 제안 생성
        improvement_suggestions = self.generate_improvement_suggestions(new_elements, expansion_opportunities)
        
        result = {
            'episode_number': episode_num,
            'improvement_potential': self.assess_improvement_potential(new_elements, expansion_opportunities),
            'new_elements_detected': len(new_elements) > 0,
            'new_elements': new_elements,
            'expansion_opportunities': expansion_opportunities,
            'suggestions': improvement_suggestions,
            'priority_improvements': self.prioritize_improvements(improvement_suggestions),
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"✅ {episode_num}화 개선점 탐지 완료 - 새 요소: {len(new_elements)}개")
        
        return result
    
    def detect_new_world_elements(self, content: str) -> List[Dict]:
        """새로운 세계관 요소 감지"""
        new_elements = []
        
        # 새로운 장소 감지
        location_indicators = ['새로운 곳', '처음 보는', '알려지지 않은', '숨겨진 장소']
        for indicator in location_indicators:
            if indicator in content:
                new_elements.append({
                    'type': 'location',
                    'indicator': indicator,
                    'description': '새로운 장소 발견'
                })
        
        # 새로운 능력/시스템 감지
        ability_indicators = ['새로운 능력', '다른 방식', '특별한 힘', '알려지지 않은 방법']
        for indicator in ability_indicators:
            if indicator in content:
                new_elements.append({
                    'type': 'ability',
                    'indicator': indicator,
                    'description': '새로운 능력 시스템'
                })
        
        # 새로운 캐릭터/집단 감지
        character_indicators = ['새로운 사람', '다른 집단', '처음 만난', '알려지지 않은 존재']
        for indicator in character_indicators:
            if indicator in content:
                new_elements.append({
                    'type': 'character',
                    'indicator': indicator,
                    'description': '새로운 인물/집단'
                })
        
        return new_elements
    
    def check_expansion_opportunities(self, content: str) -> List[Dict]:
        """설정 확장 기회 체크"""
        opportunities = []
        
        # 언급되지만 자세히 설명되지 않은 요소들
        vague_references = ['그것', '그런 식으로', '어떤 방법', '무언가']
        for reference in vague_references:
            if reference in content:
                opportunities.append({
                    'type': 'detail_expansion',
                    'element': reference,
                    'suggestion': '구체적 설명 추가 가능'
                })
        
        # 복선 가능성이 있는 요소
        foreshadowing_potential = ['이상한', '의문의', '수상한', '특이한']
        for potential in foreshadowing_potential:
            if potential in content:
                opportunities.append({
                    'type': 'foreshadowing',
                    'element': potential,
                    'suggestion': '향후 전개에 활용 가능'
                })
        
        # 갈등 확장 가능성
        conflict_seeds = ['문제가', '어려움이', '장애물이', '방해가']
        for seed in conflict_seeds:
            if seed in content:
                opportunities.append({
                    'type': 'conflict_expansion',
                    'element': seed,
                    'suggestion': '갈등 구조 심화 가능'
                })
        
        return opportunities
    
    def assess_improvement_potential(self, new_elements: List, expansion_opportunities: List) -> str:
        """개선 잠재력 평가"""
        total_potential = len(new_elements) + len(expansion_opportunities)
        
        if total_potential >= 5:
            return 'high'
        elif total_potential >= 2:
            return 'medium'
        else:
            return 'low'
    
    def generate_improvement_suggestions(self, new_elements: List, expansion_opportunities: List) -> List[str]:
        """개선 제안 생성"""
        suggestions = []
        
        # 새로운 요소 기반 제안
        for element in new_elements:
            if element['type'] == 'location':
                suggestions.append('새로운 장소에 대한 세계관 설정 문서 추가')
            elif element['type'] == 'ability':
                suggestions.append('새로운 능력 시스템을 기존 공명력과 연계하여 설명')
            elif element['type'] == 'character':
                suggestions.append('새로운 인물의 배경과 동기를 설정 문서에 추가')
        
        # 확장 기회 기반 제안
        for opportunity in expansion_opportunities:
            if opportunity['type'] == 'detail_expansion':
                suggestions.append('모호한 표현을 구체적인 설정으로 발전시키기')
            elif opportunity['type'] == 'foreshadowing':
                suggestions.append('복선 요소를 향후 스토리 전개에 활용')
            elif opportunity['type'] == 'conflict_expansion':
                suggestions.append('갈등 요소를 세계관 설정과 연계하여 심화')
        
        # 기본 제안사항
        if not suggestions:
            suggestions = [
                '기존 설정 요소의 활용도 증대',
                '세계관의 깊이와 일관성 강화'
            ]
        
        return suggestions
    
    def prioritize_improvements(self, suggestions: List[str]) -> List[Dict]:
        """개선사항 우선순위 결정"""
        prioritized = []
        
        # 우선순위 키워드 매핑
        priority_mapping = {
            'high': ['새로운', '시스템', '능력'],
            'medium': ['설정', '배경', '연계'],
            'low': ['활용', '강화', '심화']
        }
        
        for suggestion in suggestions:
            priority = 'low'  # 기본 우선순위
            
            for level, keywords in priority_mapping.items():
                if any(keyword in suggestion for keyword in keywords):
                    priority = level
                    break
            
            prioritized.append({
                'suggestion': suggestion,
                'priority': priority,
                'impact': 'high' if priority == 'high' else 'medium'
            })
        
        # 우선순위 순으로 정렬
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        prioritized.sort(key=lambda x: priority_order[x['priority']], reverse=True)
        
        return prioritized