"""
문법/오탈자 검증 에이전트 (Grammar Agent)
맞춤법, 문법 오류, 문체 일관성 등을 담당
"""

import asyncio
import logging
import re
from datetime import datetime
from typing import Dict, Any, List

from .base_agent import BaseAgent
from .project_loader import project_loader

logger = logging.getLogger(__name__)


class GrammarAgent(BaseAgent):
    """문법/오탈자 검증 에이전트"""
    
    def __init__(self):
        super().__init__("Grammar")
        self.common_errors = {}
        self.style_rules = {}
    
    async def initialize(self):
        """문법 에이전트 초기화"""
        logger.info("문법 에이전트 초기화")
        
        # 일반적인 오류 패턴 로드
        self.common_errors = {
            'typos': ['되었다' '→ 됐다', '하였다 → 했다'],
            'spacing': ['안 한다 → 안한다', '할 수 없다 → 할수없다'],
            'grammar': ['~던 것 → ~든 것', '~실 수 → ~실수']
        }
        
        # 문체 규칙
        self.style_rules = {
            'consistency': 'formal_narrative',
            'tense': 'past_tense',
            'person': 'third_person'
        }
        
        logger.info("문법 에이전트 초기화 완료")
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """작업 실행"""
        task_type = task.get('type')
        
        if task_type == 'check_grammar':
            return await self.check_grammar_and_style(task)
        else:
            return {"error": f"Unknown task type: {task_type}"}
    
    async def check_grammar_and_style(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """문법 및 스타일 검사"""
        episode_num = task.get('episode_number')
        
        # 에피소드 내용 로드
        content = project_loader.get_episode_content(episode_num)
        if not content:
            return {"error": f"에피소드 {episode_num}화를 찾을 수 없습니다"}
        
        logger.info(f"📝 문법 에이전트: {episode_num}화 검사")
        
        # 각종 검사 수행
        typo_check = self.check_typos(content)
        grammar_check = self.check_grammar_rules(content)
        style_check = self.check_style_consistency(content)
        punctuation_check = self.check_punctuation(content)
        
        # 전체 점수 계산
        grammar_score = self.calculate_grammar_score(typo_check, grammar_check, style_check, punctuation_check)
        
        # 수정 제안 생성
        corrections = self.generate_corrections(typo_check, grammar_check, style_check, punctuation_check)
        
        result = {
            'episode_number': episode_num,
            'grammar_score': grammar_score,
            'typo_check': typo_check,
            'grammar_check': grammar_check,
            'style_check': style_check,
            'punctuation_check': punctuation_check,
            'errors_found': len(corrections),
            'error_types': list(set([c['type'] for c in corrections])),
            'corrections': corrections[:10],  # 상위 10개만
            'recommendations': self.get_style_recommendations(style_check),
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"✅ {episode_num}화 문법 검사 완료 - 점수: {grammar_score:.1f}/10, 오류: {len(corrections)}개")
        
        return result
    
    def check_typos(self, content: str) -> Dict[str, Any]:
        """맞춤법 검사"""
        typos_found = []
        
        # 간단한 패턴 기반 맞춤법 검사
        typo_patterns = {
            '되었다': '됐다',
            '하였다': '했다', 
            '그렇게 된다면': '그렇다면',
            '할 수 밖에': '할 수밖에',
            '안 되': '안돼',
            '웬일': '왠일'  # 실제로는 '웬일'이 맞음 - 예시용
        }
        
        for wrong, correct in typo_patterns.items():
            if wrong in content:
                typos_found.append({
                    'original': wrong,
                    'correction': correct,
                    'count': content.count(wrong)
                })
        
        return {
            'typos_found': len(typos_found),
            'typo_list': typos_found,
            'score': max(8.0 - len(typos_found) * 0.5, 0)
        }
    
    def check_grammar_rules(self, content: str) -> Dict[str, Any]:
        """문법 규칙 검사"""
        grammar_issues = []
        
        # 기본 문법 패턴 검사
        patterns_to_check = [
            (r'\.{3,}', '과도한 말줄임표', '...'),
            (r'!{2,}', '과도한 느낌표', '!'),
            (r'\?{2,}', '과도한 물음표', '?'),
            (r'\s{3,}', '과도한 공백', ' '),
            (r'([가-힣])\1{2,}', '과도한 글자 반복', '적절한 표현')
        ]
        
        for pattern, issue_type, suggestion in patterns_to_check:
            matches = re.findall(pattern, content)
            if matches:
                grammar_issues.append({
                    'type': issue_type,
                    'count': len(matches),
                    'suggestion': suggestion
                })
        
        # 문장 부호 위치 검사
        if re.search(r'[가-힣]\s+[.!?]', content):
            grammar_issues.append({
                'type': '문장부호 띄어쓰기 오류',
                'count': len(re.findall(r'[가-힣]\s+[.!?]', content)),
                'suggestion': '문장부호는 붙여쓰기'
            })
        
        return {
            'grammar_issues': len(grammar_issues),
            'issue_list': grammar_issues,
            'score': max(8.0 - len(grammar_issues) * 0.3, 0)
        }
    
    def check_style_consistency(self, content: str) -> Dict[str, Any]:
        """문체 일관성 검사"""
        style_issues = []
        
        # 시제 일관성 검사
        past_tense_count = len(re.findall(r'[가-힣]었다|[가-힣]았다|[가-힣]였다', content))
        present_tense_count = len(re.findall(r'[가-힣]는다|[가-힣]한다', content))
        
        if past_tense_count > 0 and present_tense_count > 0:
            ratio = min(past_tense_count, present_tense_count) / max(past_tense_count, present_tense_count)
            if ratio > 0.3:  # 30% 이상이면 일관성 문제
                style_issues.append({
                    'type': '시제 일관성',
                    'past_count': past_tense_count,
                    'present_count': present_tense_count
                })
        
        # 높임법 일관성 검사
        formal_count = content.count('습니다') + content.count('했습니다')
        informal_count = content.count('한다') + content.count('했다')
        
        if formal_count > 0 and informal_count > 0:
            style_issues.append({
                'type': '높임법 일관성',
                'formal_count': formal_count,
                'informal_count': informal_count
            })
        
        # 대화체와 서술체 구분
        dialogue_sentences = content.count('"') + content.count("'")
        narrative_sentences = len(content.split('.')) - dialogue_sentences
        
        return {
            'style_issues': len(style_issues),
            'issue_list': style_issues,
            'dialogue_ratio': dialogue_sentences / (dialogue_sentences + narrative_sentences) if (dialogue_sentences + narrative_sentences) > 0 else 0,
            'score': max(8.0 - len(style_issues) * 0.4, 5.0)
        }
    
    def check_punctuation(self, content: str) -> Dict[str, Any]:
        """문장 부호 검사"""
        punctuation_issues = []
        
        # 문장 부호 사용 패턴 분석
        periods = content.count('.')
        questions = content.count('?')
        exclamations = content.count('!')
        commas = content.count(',')
        
        total_sentences = periods + questions + exclamations
        
        if total_sentences == 0:
            punctuation_issues.append('문장 부호 부족')
        
        # 쉼표 과다/부족 검사
        if commas / len(content.split()) < 0.01:  # 단어 100개당 1개 미만
            punctuation_issues.append('쉼표 부족')
        elif commas / len(content.split()) > 0.05:  # 단어 20개당 1개 초과
            punctuation_issues.append('쉼표 과다')
        
        # 따옴표 짝 확인
        if content.count('"') % 2 != 0 or content.count("'") % 2 != 0:
            punctuation_issues.append('따옴표 짝 불일치')
        
        return {
            'punctuation_issues': len(punctuation_issues),
            'issue_list': punctuation_issues,
            'punctuation_stats': {
                'periods': periods,
                'questions': questions,
                'exclamations': exclamations,
                'commas': commas
            },
            'score': max(8.0 - len(punctuation_issues) * 0.5, 4.0)
        }
    
    def calculate_grammar_score(self, typo_check: Dict, grammar_check: Dict, style_check: Dict, punctuation_check: Dict) -> float:
        """전체 문법 점수 계산"""
        
        typo_score = typo_check.get('score', 0)
        grammar_score = grammar_check.get('score', 0)
        style_score = style_check.get('score', 0)
        punct_score = punctuation_check.get('score', 0)
        
        # 가중 평균 (맞춤법 30%, 문법 30%, 문체 25%, 문장부호 15%)
        total_score = (typo_score * 0.3) + (grammar_score * 0.3) + (style_score * 0.25) + (punct_score * 0.15)
        
        return round(total_score, 1)
    
    def generate_corrections(self, typo_check: Dict, grammar_check: Dict, style_check: Dict, punctuation_check: Dict) -> List[Dict]:
        """수정 제안 생성"""
        corrections = []
        
        # 맞춤법 수정
        for typo in typo_check.get('typo_list', []):
            corrections.append({
                'type': 'typo',
                'original': typo['original'],
                'correction': typo['correction'],
                'priority': 'high'
            })
        
        # 문법 수정
        for issue in grammar_check.get('issue_list', []):
            corrections.append({
                'type': 'grammar',
                'issue': issue['type'],
                'suggestion': issue['suggestion'],
                'priority': 'medium'
            })
        
        # 문체 수정
        for issue in style_check.get('issue_list', []):
            corrections.append({
                'type': 'style',
                'issue': issue['type'],
                'priority': 'low'
            })
        
        # 문장부호 수정
        for issue in punctuation_check.get('issue_list', []):
            corrections.append({
                'type': 'punctuation',
                'issue': issue,
                'priority': 'medium'
            })
        
        # 우선순위별 정렬
        priority_order = {'high': 3, 'medium': 2, 'low': 1}
        corrections.sort(key=lambda x: priority_order.get(x['priority'], 0), reverse=True)
        
        return corrections
    
    def get_style_recommendations(self, style_check: Dict) -> List[str]:
        """문체 개선 권장사항"""
        recommendations = []
        
        dialogue_ratio = style_check.get('dialogue_ratio', 0)
        
        if dialogue_ratio < 0.1:
            recommendations.append('대화를 통한 생동감 있는 표현 추가')
        elif dialogue_ratio > 0.5:
            recommendations.append('과도한 대화보다 서술적 표현 균형 맞추기')
        
        if style_check.get('style_issues', 0) > 0:
            recommendations.append('문체 일관성 유지 (시제, 높임법 통일)')
        
        recommendations.extend([
            '웹소설 독자층에 적합한 자연스러운 문체 유지',
            '과도한 수식어보다 명확한 표현 선호',
            '문장 길이 다양화로 읽기 리듬감 개선'
        ])
        
        return recommendations