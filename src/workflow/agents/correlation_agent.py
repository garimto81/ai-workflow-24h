"""
에피소드별 연관성 담당 에이전트 (Correlation Agent)
에피소드간 연결성 및 일관성 관리를 담당
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List

from .base_agent import BaseAgent
from .project_loader import project_loader

logger = logging.getLogger(__name__)


class CorrelationAgent(BaseAgent):
    """연관성 담당 에이전트"""
    
    def __init__(self):
        super().__init__("Correlation")
        self.episode_connections = {}
        self.character_progression = {}
    
    async def initialize(self):
        """연관성 에이전트 초기화"""
        logger.info("연관성 에이전트 초기화")
        
        # 에피소드간 연결 패턴
        self.episode_connections = {
            '1->2': '상황 설정 → 갈등 발전',
            '2->3': '갈등 발전 → 해결/성장',
            'general': '이전 결과 → 새로운 상황'
        }
        
        logger.info("연관성 에이전트 초기화 완료")
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """작업 실행"""
        task_type = task.get('type')
        
        if task_type == 'analyze_episode_correlation':
            return await self.analyze_episode_correlation(task)
        else:
            return {"error": f"Unknown task type: {task_type}"}
    
    async def analyze_episode_correlation(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """에피소드 연관성 분석"""
        episode_num = task.get('episode_number')
        
        # 현재 에피소드 내용 로드
        current_content = project_loader.get_episode_content(episode_num)
        if not current_content:
            return {"error": f"에피소드 {episode_num}화를 찾을 수 없습니다"}
        
        logger.info(f"🔗 연관성 에이전트: {episode_num}화 연관성 분석")
        
        # 이전 에피소드와의 연결성 체크
        previous_connection = await self.check_previous_connection(episode_num, current_content)
        
        # 캐릭터 발전 연속성 체크
        character_continuity = self.check_character_continuity(episode_num, current_content)
        
        # 플롯 연결성 체크
        plot_continuity = self.check_plot_continuity(episode_num, current_content)
        
        # 전체 연관성 점수 계산
        correlation_score = self.calculate_correlation_score(previous_connection, character_continuity, plot_continuity)
        
        result = {
            'episode_number': episode_num,
            'correlation_score': correlation_score,
            'previous_connection': previous_connection,
            'character_continuity': character_continuity,
            'plot_continuity': plot_continuity,
            'connection_issues': self.identify_connection_issues(previous_connection, plot_continuity),
            'improvements': ['연결 문구 추가', '이전 화 결과 반영', '캐릭터 상태 연계'],
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"✅ {episode_num}화 연관성 분석 완료 - 점수: {correlation_score:.1f}/10")
        
        return result
    
    async def check_previous_connection(self, episode_num: int, current_content: str) -> Dict[str, Any]:
        """이전 에피소드와의 연결성 확인"""
        
        connection_indicators = []
        
        # 연결 표현 체크
        connection_words = ['지난번', '이전', '앞서', '그때', '그 후', '결국', '그래서']
        for word in connection_words:
            if word in current_content:
                connection_indicators.append(word)
        
        # 이전 에피소드 내용 참조 (간단한 키워드 매칭)
        if episode_num > 1:
            previous_content = project_loader.get_episode_content(episode_num - 1)
            if previous_content:
                # 공통 키워드 찾기
                current_words = set(current_content.split())
                previous_words = set(previous_content.split())
                common_important_words = []
                
                # 중요한 단어들만 체크 (명사/동사)
                important_words = [w for w in current_words & previous_words 
                                 if len(w) > 2 and w not in ['있다', '하다', '되다']]
                common_important_words = list(important_words)[:5]  # 상위 5개만
        else:
            common_important_words = []
        
        connection_strength = 'strong' if len(connection_indicators) >= 2 else 'weak'
        
        return {
            'connection_indicators': connection_indicators,
            'connection_strength': connection_strength,
            'common_elements': common_important_words,
            'has_clear_connection': len(connection_indicators) > 0
        }
    
    def check_character_continuity(self, episode_num: int, current_content: str) -> Dict[str, Any]:
        """캐릭터 연속성 체크"""
        
        # 캐릭터 상태 변화 키워드
        growth_keywords = ['성장했다', '배웠다', '깨달았다', '변했다', '발전했다']
        state_keywords = ['상태', '컨디션', '기분', '마음가짐', '의지']
        
        growth_mentions = [word for word in growth_keywords if word in current_content]
        state_mentions = [word for word in state_keywords if word in current_content]
        
        # 캐릭터 일관성 체크
        personality_consistency = self.check_personality_consistency(current_content)
        
        continuity_score = 6.0
        if growth_mentions:
            continuity_score += 1.0
        if state_mentions:
            continuity_score += 0.5
        if personality_consistency:
            continuity_score += 0.5
        
        return {
            'growth_mentions': growth_mentions,
            'state_mentions': state_mentions,
            'personality_consistent': personality_consistency,
            'continuity_score': min(continuity_score, 8.0)
        }
    
    def check_personality_consistency(self, content: str) -> bool:
        """성격 일관성 간단 체크"""
        # 기본적으로 일관성 있다고 가정 (실제로는 더 정교한 분석 필요)
        return True
    
    def check_plot_continuity(self, episode_num: int, current_content: str) -> Dict[str, Any]:
        """플롯 연속성 체크"""
        
        # 플롯 요소 연결성
        plot_connections = []
        
        # 인과관계 표현
        cause_effect_words = ['때문에', '그래서', '따라서', '결국', '그러므로']
        for word in cause_effect_words:
            if word in current_content:
                plot_connections.append(word)
        
        # 상황 전개
        development_words = ['그런데', '하지만', '그러나', '그리고', '이때']
        development_count = sum(current_content.count(word) for word in development_words)
        
        # 복선/떡밥 관련
        foreshadowing_words = ['예감', '느낌', '생각해보니', '문득', '갑자기']
        foreshadowing_count = sum(current_content.count(word) for word in foreshadowing_words)
        
        plot_score = 6.0
        if plot_connections:
            plot_score += min(len(plot_connections) * 0.5, 1.5)
        if development_count >= 2:
            plot_score += 0.5
        if foreshadowing_count >= 1:
            plot_score += 0.5
        
        return {
            'plot_connections': plot_connections,
            'development_indicators': development_count,
            'foreshadowing_elements': foreshadowing_count,
            'plot_flow_score': min(plot_score, 8.0)
        }
    
    def calculate_correlation_score(self, previous_connection: Dict, character_continuity: Dict, plot_continuity: Dict) -> float:
        """전체 연관성 점수 계산"""
        
        # 각 영역 점수
        connection_score = 7.0 if previous_connection['has_clear_connection'] else 5.0
        character_score = character_continuity.get('continuity_score', 6.0)
        plot_score = plot_continuity.get('plot_flow_score', 6.0)
        
        # 가중 평균 (이전 연결 40%, 캐릭터 30%, 플롯 30%)
        total_score = (connection_score * 0.4) + (character_score * 0.3) + (plot_score * 0.3)
        
        return round(total_score, 1)
    
    def identify_connection_issues(self, previous_connection: Dict, plot_continuity: Dict) -> List[str]:
        """연결성 문제점 식별"""
        issues = []
        
        if not previous_connection['has_clear_connection']:
            issues.append('이전 화와 연결성 부족')
        
        if len(previous_connection['common_elements']) < 2:
            issues.append('공통 요소 부족')
        
        if plot_continuity['plot_flow_score'] < 6.5:
            issues.append('플롯 흐름 개선 필요')
        
        return issues