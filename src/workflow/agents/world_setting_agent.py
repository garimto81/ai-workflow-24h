"""
세계관 담당 에이전트 (World Setting Agent)
세계관 설정 관리 및 일관성 유지를 담당
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List

from .base_agent import BaseAgent
from .project_loader import project_loader

logger = logging.getLogger(__name__)


class WorldSettingAgent(BaseAgent):
    """세계관 담당 에이전트"""
    
    def __init__(self):
        super().__init__("WorldSetting")
        self.world_knowledge = {}
        self.consistency_rules = {}
    
    async def initialize(self):
        """세계관 에이전트 초기화"""
        logger.info("세계관 에이전트 초기화")
        
        # 세계관 지식 로드
        await self.load_world_knowledge()
        
        # 일관성 규칙 설정
        await self.setup_consistency_rules()
        
        logger.info("세계관 에이전트 초기화 완료")
    
    async def load_world_knowledge(self):
        """세계관 지식 로드"""
        try:
            # 공명력 시스템 문서
            resonance_doc = project_loader.documents.get('world_setting/021_resonance_system.md', '')
            
            # 기본 세계 설정
            basic_setting = project_loader.documents.get('world_setting/001_basic_world_setting.md', '')
            
            self.world_knowledge = {
                'resonance_system': self.extract_resonance_rules(resonance_doc),
                'basic_world': self.extract_world_info(basic_setting),
                'terminology': self.extract_terminology(),
                'power_system': 'resonance_based',
                'world_type': 'post_apocalyptic_fantasy'
            }
        except Exception as e:
            logger.warning(f"세계관 문서 로드 실패: {e}")
            # 기본 설정 사용
            self.world_knowledge = {
                'resonance_system': {'basic_rule': '공명력은 생명체의 정신적 에너지'},
                'terminology': ['공명력', '공명석', '공명자'],
                'power_system': 'resonance_based',
                'world_type': 'post_apocalyptic_fantasy'
            }
    
    def extract_resonance_rules(self, document: str) -> Dict[str, Any]:
        """공명력 시스템 규칙 추출"""
        rules = {}
        
        if document:
            lines = document.split('\n')
            for line in lines:
                if '공명력' in line and ':' in line:
                    key, value = line.split(':', 1)
                    rules[key.strip()] = value.strip()
        
        # 기본 규칙
        if not rules:
            rules = {
                '기본 정의': '공명력은 생명체의 정신적 에너지',
                '사용 조건': '정신적 집중과 의지력 필요',
                '제한 사항': '과도한 사용시 정신적 피로'
            }
        
        return rules
    
    def extract_world_info(self, document: str) -> Dict[str, Any]:
        """기본 세계 정보 추출"""
        world_info = {}
        
        if document:
            # 키워드 기반 정보 추출
            info_keywords = ['시대', '배경', '문명', '기술', '사회']
            for keyword in info_keywords:
                for line in document.split('\n'):
                    if keyword in line:
                        world_info[keyword] = line.strip()
        
        # 기본 정보
        if not world_info:
            world_info = {
                '시대': '포스트 아포칼립스',
                '배경': '문명 붕괴 이후의 세계',
                '기술': '공명력 기반 기술',
                '사회': '생존자 공동체 중심'
            }
        
        return world_info
    
    def extract_terminology(self) -> List[str]:
        """전문 용어 추출"""
        return [
            '공명력', '공명석', '공명자', '공명 반응',
            '정신력', '의지력', '공명 증폭기', '공명 차단기',
            '대붕괴', '생존자', '폐허', '변이체'
        ]
    
    async def setup_consistency_rules(self):
        """일관성 규칙 설정"""
        self.consistency_rules = {
            'terminology': {
                'required_terms': self.world_knowledge.get('terminology', []),
                'forbidden_terms': ['마나', '마법', 'MP', '레벨업'],
                'alternative_terms': {
                    '마나': '공명력',
                    '마법': '공명술',
                    '마법사': '공명자'
                }
            },
            'power_system': {
                'source': 'mental_energy',
                'limitation': 'mental_fatigue',
                'enhancement': 'resonance_stones'
            },
            'world_rules': {
                'technology_level': 'post_modern_mixed',
                'civilization_state': 'collapsed',
                'survival_focus': True
            }
        }
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """작업 실행"""
        task_type = task.get('type')
        
        if task_type == 'verify_world_consistency':
            return await self.verify_world_consistency(task)
        else:
            return {"error": f"Unknown task type: {task_type}"}
    
    async def verify_world_consistency(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """세계관 일관성 검증"""
        episode_num = task.get('episode_number')
        
        # 에피소드 내용 로드
        content = project_loader.get_episode_content(episode_num)
        if not content:
            return {"error": f"에피소드 {episode_num}화를 찾을 수 없습니다"}
        
        logger.info(f"🌍 세계관 에이전트: {episode_num}화 일관성 검증")
        
        # 각종 검증 수행
        terminology_check = self.check_terminology_consistency(content)
        power_system_check = self.check_power_system_consistency(content)
        world_rule_check = self.check_world_rule_consistency(content)
        setting_reference_check = self.check_setting_references(content)
        
        # 전체 점수 계산
        consistency_score = self.calculate_consistency_score(
            terminology_check, power_system_check, world_rule_check, setting_reference_check
        )
        
        # 개선 제안 생성
        improvements = self.generate_consistency_improvements(
            terminology_check, power_system_check, world_rule_check
        )
        
        result = {
            'episode_number': episode_num,
            'consistency_score': consistency_score,
            'terminology_check': terminology_check,
            'power_system_check': power_system_check,
            'world_rule_check': world_rule_check,
            'setting_reference_check': setting_reference_check,
            'issues': self.identify_consistency_issues(terminology_check, power_system_check, world_rule_check),
            'improvements': improvements,
            'world_elements_used': self.count_world_elements(content),
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"✅ {episode_num}화 세계관 검증 완료 - 점수: {consistency_score:.1f}/10")
        
        return result
    
    def check_terminology_consistency(self, content: str) -> Dict[str, Any]:
        """용어 일관성 검사"""
        
        # 적절한 용어 사용 확인
        correct_terms_used = []
        for term in self.world_knowledge.get('terminology', []):
            if term in content:
                correct_terms_used.append(term)
        
        # 금지된 용어 사용 확인
        forbidden_terms_found = []
        for term in self.consistency_rules['terminology']['forbidden_terms']:
            if term in content:
                forbidden_terms_found.append(term)
        
        # 대체 가능한 용어 제안
        alternative_suggestions = []
        for forbidden, alternative in self.consistency_rules['terminology']['alternative_terms'].items():
            if forbidden in content:
                alternative_suggestions.append({
                    'original': forbidden,
                    'alternative': alternative,
                    'count': content.count(forbidden)
                })
        
        # 점수 계산
        score = 6.0  # 기본 점수
        score += min(len(correct_terms_used) * 0.5, 3.0)  # 적절한 용어 사용
        score -= len(forbidden_terms_found) * 1.0  # 금지 용어 감점
        score = max(score, 0.0)
        
        return {
            'correct_terms_used': correct_terms_used,
            'correct_terms_count': len(correct_terms_used),
            'forbidden_terms_found': forbidden_terms_found,
            'alternative_suggestions': alternative_suggestions,
            'terminology_score': score
        }
    
    def check_power_system_consistency(self, content: str) -> Dict[str, Any]:
        """힘 체계 일관성 검사"""
        
        # 공명력 관련 표현 찾기
        power_mentions = []
        power_keywords = ['공명력', '공명', '정신력', '의지력', '집중']
        
        for keyword in power_keywords:
            count = content.count(keyword)
            if count > 0:
                power_mentions.append({
                    'keyword': keyword,
                    'count': count
                })
        
        # 힘의 사용 패턴 분석
        power_usage_patterns = []
        usage_indicators = ['사용했다', '발동했다', '집중했다', '소모됐다', '피로했다']
        
        for indicator in usage_indicators:
            if indicator in content:
                power_usage_patterns.append(indicator)
        
        # 제한사항 언급 확인
        limitation_mentions = []
        limitations = ['피로', '한계', '소모', '지쳤다', '부담']
        
        for limitation in limitations:
            if limitation in content:
                limitation_mentions.append(limitation)
        
        # 점수 계산
        score = 6.0  # 기본 점수
        if power_mentions:
            score += 1.5  # 힘 체계 언급
        if power_usage_patterns:
            score += 1.0  # 사용 패턴 적절
        if limitation_mentions:
            score += 0.5  # 제한사항 인지
        
        return {
            'power_mentions': power_mentions,
            'power_usage_patterns': power_usage_patterns,
            'limitation_mentions': limitation_mentions,
            'power_system_integrated': len(power_mentions) > 0,
            'power_system_score': min(score, 8.5)
        }
    
    def check_world_rule_consistency(self, content: str) -> Dict[str, Any]:
        """세계 규칙 일관성 검사"""
        
        # 포스트 아포칼립스 분위기 확인
        apocalyptic_elements = []
        apocalyptic_keywords = ['폐허', '붕괴', '생존', '파괴된', '버려진', '잔해']
        
        for keyword in apocalyptic_keywords:
            if keyword in content:
                apocalyptic_elements.append(keyword)
        
        # 문명 수준 확인
        tech_level_indicators = []
        modern_tech = ['컴퓨터', '인터넷', '휴대폰', '자동차']  # 현대 기술
        post_tech = ['공명 장치', '생존 도구', '간이 설비']  # 포스트 기술
        
        for tech in modern_tech:
            if tech in content:
                tech_level_indicators.append({'type': 'modern', 'tech': tech})
        
        for tech in post_tech:
            if tech in content:
                tech_level_indicators.append({'type': 'post', 'tech': tech})
        
        # 생존 주제 확인
        survival_themes = []
        survival_keywords = ['생존', '살아남다', '버티다', '견디다', '극복']
        
        for keyword in survival_keywords:
            if keyword in content:
                survival_themes.append(keyword)
        
        # 점수 계산
        score = 6.0  # 기본 점수
        if apocalyptic_elements:
            score += min(len(apocalyptic_elements) * 0.3, 1.5)
        if survival_themes:
            score += min(len(survival_themes) * 0.2, 1.0)
        
        # 부적절한 현대 기술 과다 사용시 감점
        modern_tech_count = len([t for t in tech_level_indicators if t['type'] == 'modern'])
        if modern_tech_count > 2:
            score -= (modern_tech_count - 2) * 0.5
        
        return {
            'apocalyptic_elements': apocalyptic_elements,
            'tech_level_indicators': tech_level_indicators,
            'survival_themes': survival_themes,
            'atmosphere_appropriate': len(apocalyptic_elements) > 0,
            'world_rule_score': max(min(score, 8.0), 3.0)
        }
    
    def check_setting_references(self, content: str) -> Dict[str, Any]:
        """설정 문서 참조 확인"""
        
        # 알려진 설정 요소 확인
        known_elements = []
        
        # 공명력 시스템 참조
        resonance_elements = self.world_knowledge.get('resonance_system', {})
        for element_key, element_desc in resonance_elements.items():
            key_words = element_desc.split()[:3]  # 처음 3단어만
            for word in key_words:
                if len(word) > 1 and word in content:
                    known_elements.append({
                        'category': 'resonance',
                        'element': element_key,
                        'reference': word
                    })
        
        # 세계 정보 참조
        world_elements = self.world_knowledge.get('basic_world', {})
        for element_key, element_desc in world_elements.items():
            key_words = element_desc.split()[:2]
            for word in key_words:
                if len(word) > 1 and word in content:
                    known_elements.append({
                        'category': 'world',
                        'element': element_key,
                        'reference': word
                    })
        
        return {
            'known_elements_referenced': known_elements,
            'reference_count': len(known_elements),
            'categories_covered': list(set([e['category'] for e in known_elements]))
        }
    
    def calculate_consistency_score(self, terminology_check: Dict, power_system_check: Dict, world_rule_check: Dict, setting_reference_check: Dict) -> float:
        """전체 일관성 점수 계산"""
        
        terminology_score = terminology_check.get('terminology_score', 0)
        power_score = power_system_check.get('power_system_score', 0)
        world_score = world_rule_check.get('world_rule_score', 0)
        
        # 가중 평균 (용어 35%, 힘 체계 35%, 세계 규칙 30%)
        total_score = (terminology_score * 0.35) + (power_score * 0.35) + (world_score * 0.30)
        
        return round(total_score, 1)
    
    def identify_consistency_issues(self, terminology_check: Dict, power_system_check: Dict, world_rule_check: Dict) -> List[str]:
        """일관성 문제점 식별"""
        issues = []
        
        # 용어 관련 문제
        if terminology_check.get('forbidden_terms_found'):
            issues.append('부적절한 용어 사용 발견')
        
        if terminology_check.get('correct_terms_count', 0) < 2:
            issues.append('세계관 관련 용어 사용 부족')
        
        # 힘 체계 문제
        if not power_system_check.get('power_system_integrated', False):
            issues.append('공명력 시스템 설명 부족')
        
        # 세계 규칙 문제
        if not world_rule_check.get('atmosphere_appropriate', False):
            issues.append('포스트 아포칼립스 분위기 부족')
        
        return issues
    
    def generate_consistency_improvements(self, terminology_check: Dict, power_system_check: Dict, world_rule_check: Dict) -> List[str]:
        """일관성 개선 제안"""
        improvements = []
        
        # 용어 개선
        alternative_suggestions = terminology_check.get('alternative_suggestions', [])
        for suggestion in alternative_suggestions[:3]:  # 상위 3개만
            improvements.append(f"'{suggestion['original']}'를 '{suggestion['alternative']}'로 변경")
        
        # 힘 체계 개선
        if power_system_check.get('power_system_score', 0) < 7.0:
            improvements.append('공명력 시스템 설명 및 활용 강화')
            improvements.append('힘 사용의 제한사항과 부작용 명시')
        
        # 세계 규칙 개선
        if world_rule_check.get('world_rule_score', 0) < 7.0:
            improvements.append('포스트 아포칼립스적 배경 묘사 강화')
            improvements.append('생존 상황과 어려움 부각')
        
        # 일반적 개선사항
        improvements.extend([
            '설정 문서와 일치하는 세계관 요소 적극 활용',
            '세계관의 독창성과 일관성 동시 유지'
        ])
        
        return improvements
    
    def count_world_elements(self, content: str) -> Dict[str, int]:
        """세계관 요소 사용 빈도"""
        element_counts = {}
        
        # 주요 세계관 요소별 카운트
        world_categories = {
            'power_system': ['공명력', '공명', '정신력'],
            'apocalyptic': ['폐허', '붕괴', '생존', '파괴'],
            'technology': ['공명 장치', '생존 도구', '장비'],
            'atmosphere': ['어둠', '절망', '희망', '의지']
        }
        
        for category, keywords in world_categories.items():
            count = sum(content.count(keyword) for keyword in keywords)
            element_counts[category] = count
        
        return element_counts