"""
에피소드 검토 전용 에이전트
Classic Isekai 프로젝트의 기존 에피소드들을 검토하고 개선
"""

import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
import logging
import json

from .base_agent import BaseAgent
from .project_loader import project_loader

logger = logging.getLogger(__name__)


class EpisodeReviewerAgent(BaseAgent):
    """에피소드 검토 전용 에이전트"""
    
    def __init__(self):
        super().__init__("EpisodeReviewer")
        
        # 프로젝트 문서 캐시
        self.project_docs = {}
        self.current_episode = None
        self.review_standards = {}
        
    async def initialize(self):
        """에이전트 초기화"""
        logger.info("에피소드 리뷰어 초기화")
        
        # 프로젝트 로더 초기화
        await project_loader.initialize_project()
        
        # 검토에 필요한 문서들 로드
        await self.load_review_documents()
        
        # 검토 기준 설정
        self.setup_review_standards()
        
        logger.info("에피소드 리뷰어 초기화 완료")
    
    async def load_review_documents(self):
        """검토에 필요한 문서들 로드"""
        
        # 작품 정보 및 가이드라인
        essential_docs = [
            "webnovel_episodes/000_소설정보.md",  # 작품 기본 정보
            "docs/episode_guide.md",              # 에피소드 가이드
            "WORLDBUILDING_RULES.md",             # 세계관 규칙
            "world_setting/000_INDEX.md",         # 문서 구조
            "world_setting/110_story_bible.md"    # 스토리 바이블
        ]
        
        for doc_path in essential_docs:
            full_path = project_loader.base_path / doc_path
            if full_path.exists():
                content = project_loader.read_file(full_path)
                self.project_docs[doc_path] = content
        
        # 세계관 핵심 문서들
        worldbuilding_docs = project_loader.get_agent_documents('worldbuilding_agent')
        self.project_docs.update(worldbuilding_docs)
        
        # 캐릭터 문서들
        character_docs = project_loader.get_agent_documents('character_agent')
        self.project_docs.update(character_docs)
        
        logger.info(f"검토용 문서 {len(self.project_docs)}개 로드 완료")
    
    def setup_review_standards(self):
        """검토 기준 설정"""
        self.review_standards = {
            'worldbuilding_consistency': {
                'weight': 0.2,
                'description': '세계관 일관성',
                'criteria': [
                    '공명력 시스템 일치',
                    '지명/용어 일관성',
                    '사회 구조 일치'
                ]
            },
            'character_consistency': {
                'weight': 0.2,
                'description': '캐릭터 일관성',
                'criteria': [
                    '성격 일치',
                    '능력 수준 일치',
                    '관계 설정 일치'
                ]
            },
            'plot_continuity': {
                'weight': 0.15,
                'description': '플롯 연속성',
                'criteria': [
                    '이전 화와의 연결',
                    '시간선 일치',
                    '사건 인과관계'
                ]
            },
            'writing_quality': {
                'weight': 0.15,
                'description': '작문 품질',
                'criteria': [
                    '문장 자연스러움',
                    '묘사의 생생함',
                    '대화 현실성'
                ]
            },
            'pacing': {
                'weight': 0.1,
                'description': '페이싱',
                'criteria': [
                    '전개 속도 적절성',
                    '긴장감 유지',
                    '클라이맥스 배치'
                ]
            },
            'genre_appropriateness': {
                'weight': 0.1,
                'description': '장르 적합성',
                'criteria': [
                    '포스트 아포칼립스 분위기',
                    '판타지 요소 활용',
                    '독자 기대 충족'
                ]
            },
            'technical_aspects': {
                'weight': 0.1,
                'description': '기술적 측면',
                'criteria': [
                    '맞춤법/띄어쓰기',
                    '문단 구성',
                    '분량 적절성'
                ]
            }
        }
    
    async def execute(self, task: Dict[str, Any]) -> Any:
        """작업 실행"""
        task_type = task.get('type')
        
        if task_type == 'review_episode':
            return await self.review_episode(task)
        elif task_type == 'review_all_episodes':
            return await self.review_all_episodes(task)
        elif task_type == 'analyze_episode_progression':
            return await self.analyze_episode_progression(task)
        else:
            return {"error": f"Unknown task type: {task_type}"}
    
    async def review_episode(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """개별 에피소드 검토"""
        episode_number = task.get('episode_number')
        
        if not episode_number:
            return {"error": "에피소드 번호가 필요합니다"}
        
        logger.info(f"에피소드 {episode_number}화 검토 시작")
        
        # 에피소드 내용 로드
        episode_content = project_loader.get_episode_content(episode_number)
        if not episode_content:
            return {"error": f"에피소드 {episode_number}화를 찾을 수 없습니다"}
        
        # 각 기준별 검토
        review_results = {}
        overall_score = 0.0
        
        for criterion, standard in self.review_standards.items():
            score = await self.evaluate_criterion(
                episode_content, 
                episode_number,
                criterion, 
                standard
            )
            
            review_results[criterion] = {
                'score': score,
                'weight': standard['weight'],
                'weighted_score': score * standard['weight'],
                'description': standard['description']
            }
            
            overall_score += score * standard['weight']
        
        # 전반적 개선 제안
        improvement_suggestions = await self.generate_improvement_suggestions(
            episode_content, 
            review_results
        )
        
        result = {
            'episode_number': episode_number,
            'overall_score': round(overall_score, 2),
            'review_date': datetime.now().isoformat(),
            'detailed_scores': review_results,
            'improvement_suggestions': improvement_suggestions,
            'word_count': len(episode_content),
            'status': 'needs_improvement' if overall_score < 7.5 else 'good'
        }
        
        logger.info(f"에피소드 {episode_number}화 검토 완료 (점수: {overall_score:.1f}/10)")
        
        return result
    
    async def evaluate_criterion(self, episode_content: str, episode_number: int,
                                criterion: str, standard: Dict) -> float:
        """특정 기준에 대한 평가"""
        
        if criterion == 'worldbuilding_consistency':
            return await self.check_worldbuilding_consistency(episode_content)
        
        elif criterion == 'character_consistency':
            return await self.check_character_consistency(episode_content, episode_number)
        
        elif criterion == 'plot_continuity':
            return await self.check_plot_continuity(episode_content, episode_number)
        
        elif criterion == 'writing_quality':
            return await self.check_writing_quality(episode_content)
        
        elif criterion == 'pacing':
            return await self.check_pacing(episode_content)
        
        elif criterion == 'genre_appropriateness':
            return await self.check_genre_appropriateness(episode_content)
        
        elif criterion == 'technical_aspects':
            return await self.check_technical_aspects(episode_content)
        
        else:
            return 7.0  # 기본 점수
    
    async def check_worldbuilding_consistency(self, episode_content: str) -> float:
        """세계관 일관성 검사"""
        
        # 핵심 세계관 요소들 추출
        worldbuilding_context = ""
        if "world_setting/021_resonance_system.md" in self.project_docs:
            worldbuilding_context += self.project_docs["world_setting/021_resonance_system.md"][:1000]
        
        prompt = f"""
        다음은 포스트 아포칼립스 판타지 소설 "Resonance Extinctus"의 에피소드입니다.
        
        【세계관 기준】
        {worldbuilding_context}
        
        【에피소드 내용】
        {episode_content[:2000]}
        
        세계관 일관성을 다음 기준으로 평가하세요:
        1. 공명력(Resonance) 시스템 설명의 일관성
        2. 용어 사용의 정확성
        3. 세계 설정과의 부합성
        
        1-10점으로 점수를 매기고 간단한 이유를 설명하세요.
        """
        
        response = await self.call_claude(prompt, max_tokens=500)
        
        # 점수 추출 (간단한 파싱)
        try:
            import re
            score_match = re.search(r'(\d+(?:\.\d+)?)\s*[점/]', response)
            if score_match:
                return float(score_match.group(1))
        except:
            pass
        
        return 7.0  # 기본값
    
    async def check_character_consistency(self, episode_content: str, episode_number: int) -> float:
        """캐릭터 일관성 검사"""
        
        # 주인공 정보 가져오기
        protagonist_info = ""
        if "world_setting/100_protagonist.md" in self.project_docs:
            protagonist_info = self.project_docs["world_setting/100_protagonist.md"][:1000]
        
        prompt = f"""
        【주인공 설정】
        {protagonist_info}
        
        【현재 에피소드 ({episode_number}화)】
        {episode_content[:2000]}
        
        캐릭터 일관성을 평가하세요:
        1. 주인공의 성격과 행동 일치성
        2. 능력 수준의 적절성
        3. 대화 스타일의 일관성
        
        1-10점으로 평가하고 이유를 설명하세요.
        """
        
        response = await self.call_claude(prompt, max_tokens=500)
        
        # 점수 추출
        try:
            import re
            score_match = re.search(r'(\d+(?:\.\d+)?)\s*[점/]', response)
            if score_match:
                return float(score_match.group(1))
        except:
            pass
        
        return 7.5  # 기본값
    
    async def check_plot_continuity(self, episode_content: str, episode_number: int) -> float:
        """플롯 연속성 검사"""
        
        # 이전 에피소드와 비교
        if episode_number > 1:
            prev_episode = project_loader.get_episode_content(episode_number - 1)
            if prev_episode:
                prompt = f"""
                이전 에피소드와 현재 에피소드의 연결성을 평가하세요.
                
                【이전 화 끝부분】
                {prev_episode[-500:]}
                
                【현재 화 시작부분】
                {episode_content[:500]}
                
                연속성 평가 기준:
                1. 시간적 연결성
                2. 상황/분위기 연결
                3. 캐릭터 상태 연결
                
                1-10점으로 평가하세요.
                """
                
                response = await self.call_claude(prompt, max_tokens=300)
                
                try:
                    import re
                    score_match = re.search(r'(\d+(?:\.\d+)?)\s*[점/]', response)
                    if score_match:
                        return float(score_match.group(1))
                except:
                    pass
        
        return 8.0  # 기본값
    
    async def check_writing_quality(self, episode_content: str) -> float:
        """작문 품질 검사"""
        
        prompt = f"""
        다음 웹소설 에피소드의 작문 품질을 평가하세요.
        
        {episode_content[:2000]}
        
        평가 기준:
        1. 문장의 자연스러움
        2. 묘사의 생생함과 구체성
        3. 대화의 현실성
        4. 전체적인 읽기 흐름
        
        1-10점으로 평가하고 개선점을 제시하세요.
        """
        
        response = await self.call_claude(prompt, max_tokens=500)
        
        try:
            import re
            score_match = re.search(r'(\d+(?:\.\d+)?)\s*[점/]', response)
            if score_match:
                return float(score_match.group(1))
        except:
            pass
        
        return 7.0  # 기본값
    
    async def check_pacing(self, episode_content: str) -> float:
        """페이싱 검사"""
        
        # 간단한 구조 분석
        paragraphs = episode_content.split('\n\n')
        avg_paragraph_length = sum(len(p) for p in paragraphs) / len(paragraphs) if paragraphs else 0
        
        prompt = f"""
        에피소드의 페이싱을 분석하세요.
        
        총 문단 수: {len(paragraphs)}
        평균 문단 길이: {avg_paragraph_length:.0f}자
        전체 길이: {len(episode_content)}자
        
        【샘플 텍스트】
        {episode_content[:1000]}
        
        페이싱 평가:
        1. 전개 속도의 적절성
        2. 긴장감 조절
        3. 독자 몰입도
        
        1-10점으로 평가하세요.
        """
        
        response = await self.call_claude(prompt, max_tokens=400)
        
        try:
            import re
            score_match = re.search(r'(\d+(?:\.\d+)?)\s*[점/]', response)
            if score_match:
                return float(score_match.group(1))
        except:
            pass
        
        return 7.5  # 기본값
    
    async def check_genre_appropriateness(self, episode_content: str) -> float:
        """장르 적합성 검사"""
        
        prompt = f"""
        이 에피소드가 "포스트 아포칼립스 판타지" 장르에 얼마나 적합한지 평가하세요.
        
        {episode_content[:1500]}
        
        장르 요소 확인:
        1. 포스트 아포칼립스적 분위기와 설정
        2. 판타지 요소 (공명력, 특수 능력)
        3. 장르 독자들의 기대 충족
        
        1-10점으로 평가하세요.
        """
        
        response = await self.call_claude(prompt, max_tokens=400)
        
        try:
            import re
            score_match = re.search(r'(\d+(?:\.\d+)?)\s*[점/]', response)
            if score_match:
                return float(score_match.group(1))
        except:
            pass
        
        return 8.0  # 기본값
    
    async def check_technical_aspects(self, episode_content: str) -> float:
        """기술적 측면 검사"""
        
        # 기본 통계
        word_count = len(episode_content)
        paragraphs = episode_content.split('\n\n')
        sentences = episode_content.split('.')
        
        score = 10.0
        
        # 분량 체크 (6000-8000자 권장)
        if word_count < 6000:
            score -= 1.5
        elif word_count > 8000:
            score -= 1.0
        
        # 문단 구성 체크
        if len(paragraphs) < 10:
            score -= 1.0  # 너무 긴 문단들
        elif len(paragraphs) > 50:
            score -= 0.5  # 너무 짧은 문단들
        
        # 간단한 문법 체크 (기본적인 것만)
        grammar_issues = 0
        if '...' in episode_content:
            grammar_issues += episode_content.count('...')
        if '???' in episode_content:
            grammar_issues += episode_content.count('???')
        if '!!!' in episode_content:
            grammar_issues += episode_content.count('!!!')
        
        if grammar_issues > 5:
            score -= 1.0
        
        return max(score, 0.0)
    
    async def generate_improvement_suggestions(self, episode_content: str, 
                                             review_results: Dict) -> List[str]:
        """개선 제안 생성"""
        
        suggestions = []
        
        # 점수가 낮은 항목들에 대한 제안
        for criterion, result in review_results.items():
            if result['score'] < 7.0:
                if criterion == 'worldbuilding_consistency':
                    suggestions.append("세계관 설정과의 일관성 확인 및 용어 통일 필요")
                elif criterion == 'character_consistency':
                    suggestions.append("캐릭터의 성격과 행동 패턴 재검토 필요")
                elif criterion == 'plot_continuity':
                    suggestions.append("이전 화와의 연결성 강화 필요")
                elif criterion == 'writing_quality':
                    suggestions.append("문장 다듬기 및 묘사 보강 필요")
                elif criterion == 'pacing':
                    suggestions.append("전개 속도 조절 및 긴장감 개선 필요")
                elif criterion == 'genre_appropriateness':
                    suggestions.append("장르 특성을 더 잘 살린 내용 보완 필요")
                elif criterion == 'technical_aspects':
                    suggestions.append("문법 점검 및 문단 구성 개선 필요")
        
        return suggestions
    
    async def review_all_episodes(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """모든 에피소드 일괄 검토"""
        logger.info("모든 에피소드 일괄 검토 시작")
        
        all_episodes = project_loader.get_all_episodes()
        review_results = {}
        
        for episode_num in sorted(all_episodes.keys()):
            result = await self.review_episode({'episode_number': episode_num})
            review_results[episode_num] = result
            
            # 처리 간 잠시 대기
            await asyncio.sleep(1)
        
        # 전체 요약
        scores = [r['overall_score'] for r in review_results.values()]
        summary = {
            'total_episodes': len(review_results),
            'average_score': sum(scores) / len(scores) if scores else 0,
            'highest_score': max(scores) if scores else 0,
            'lowest_score': min(scores) if scores else 0,
            'episodes_needing_improvement': len([s for s in scores if s < 7.5]),
            'detailed_results': review_results
        }
        
        logger.info(f"전체 검토 완료. 평균 점수: {summary['average_score']:.1f}/10")
        
        return summary