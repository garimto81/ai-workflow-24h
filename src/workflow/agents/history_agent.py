"""
역사 담당 에이전트 (History Agent)
작품 내 역사 및 연대기 관리를 담당
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List

from .base_agent import BaseAgent
from .project_loader import project_loader

logger = logging.getLogger(__name__)


class HistoryAgent(BaseAgent):
    """역사 담당 에이전트"""
    
    def __init__(self):
        super().__init__("History")
        self.timeline = {}
        self.historical_events = {}
    
    async def initialize(self):
        """역사 에이전트 초기화"""
        logger.info("역사 에이전트 초기화")
        
        # 타임라인 설정
        self.timeline = {
            '대붕괴': '50년 전',
            '현재': '회귀 시점',
            '미래_예정': '3개월 후 큰 변화'
        }
        
        # 역사적 사건들
        self.historical_events = {
            '대붕괴': '문명이 무너진 사건',
            '공명력_발견': '대붕괴 후 새로운 힘 발견',
            '생존자_정착': '현재 거점 설립'
        }
        
        logger.info("역사 에이전트 초기화 완료")
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """작업 실행"""
        task_type = task.get('type')
        
        if task_type == 'validate_timeline':
            return await self.validate_timeline_consistency(task)
        else:
            return {"error": f"Unknown task type: {task_type}"}
    
    async def validate_timeline_consistency(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """시간선 일관성 검증"""
        episode_num = task.get('episode_number')
        
        # 에피소드 내용 로드
        content = project_loader.get_episode_content(episode_num)
        if not content:
            return {"error": f"에피소드 {episode_num}화를 찾을 수 없습니다"}
        
        logger.info(f"⏰ 역사 에이전트: {episode_num}화 시간선 검증")
        
        # 시간 표현 체크
        time_references = self.extract_time_references(content)
        
        # 역사적 사건 언급 확인
        historical_mentions = self.check_historical_mentions(content)
        
        # 시간 일관성 검사
        consistency_check = self.check_time_consistency(content, time_references)
        
        # 점수 계산
        timeline_score = self.calculate_timeline_score(time_references, historical_mentions, consistency_check)
        
        result = {
            'episode_number': episode_num,
            'timeline_score': timeline_score,
            'time_references': time_references,
            'historical_mentions': historical_mentions,
            'consistency_issues': consistency_check['issues'],
            'continuity_issues': ['시간 흐름 애매'] if timeline_score < 7.0 else [],
            'suggestions': ['시간 표현 명확화', '과거 사건 연결성 강화'],
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"✅ {episode_num}화 시간선 검증 완료 - 점수: {timeline_score:.1f}/10")
        
        return result
    
    def extract_time_references(self, content: str) -> List[Dict]:
        """시간 표현 추출"""
        time_keywords = ['전에', '후에', '지금', '현재', '과거', '미래', '년', '개월', '일']
        references = []
        
        for keyword in time_keywords:
            if keyword in content:
                references.append({
                    'keyword': keyword,
                    'count': content.count(keyword)
                })
        
        return references
    
    def check_historical_mentions(self, content: str) -> List[str]:
        """역사적 사건 언급 확인"""
        mentions = []
        
        for event, description in self.historical_events.items():
            if event in content or any(word in content for word in description.split()[:2]):
                mentions.append(event)
        
        return mentions
    
    def check_time_consistency(self, content: str, time_references: List) -> Dict:
        """시간 일관성 검사"""
        issues = []
        
        # 기본 시간 흐름 체크
        if not time_references:
            issues.append('시간 표현 부족')
        
        # 회귀물 특성상 과거/현재 언급 확인
        past_mentions = content.count('전에') + content.count('과거')
        present_mentions = content.count('지금') + content.count('현재')
        
        if past_mentions == 0 and present_mentions == 0:
            issues.append('시간 기준점 모호')
        
        return {
            'issues': issues,
            'past_mentions': past_mentions,
            'present_mentions': present_mentions
        }
    
    def calculate_timeline_score(self, time_references: List, historical_mentions: List, consistency_check: Dict) -> float:
        """시간선 점수 계산"""
        score = 6.0  # 기본 점수
        
        # 시간 표현 보너스
        if time_references:
            score += min(len(time_references) * 0.3, 1.5)
        
        # 역사적 사건 언급 보너스
        if historical_mentions:
            score += min(len(historical_mentions) * 0.5, 1.0)
        
        # 일관성 문제 감점
        score -= len(consistency_check['issues']) * 0.5
        
        return max(min(score, 8.5), 4.0)