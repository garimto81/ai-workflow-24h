"""
독자 에이전트 (Reader Agent)
10개 다양한 독자 페르소나로 작품을 평가하는 에이전트
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List

from .base_agent import BaseAgent
from .project_loader import project_loader

logger = logging.getLogger(__name__)


class ReaderAgent(BaseAgent):
    """독자 에이전트 - 10개 페르소나"""
    
    def __init__(self):
        super().__init__("Reader")
        self.personas = {}
    
    async def initialize(self):
        """독자 에이전트 초기화"""
        logger.info("독자 에이전트 초기화")
        
        # 10개 독자 페르소나 설정
        self.personas = {
            1: {
                "type": "액션_선호", 
                "age": 20, 
                "gender": "남성",
                "preferences": ["전투", "액션", "스릴"],
                "dislikes": ["로맨스", "일상", "대화 위주"],
                "evaluation_focus": ["전투 묘사", "긴장감", "스피드감"]
            },
            2: {
                "type": "로맨스_선호", 
                "age": 25, 
                "gender": "여성",
                "preferences": ["감정", "관계", "성장"],
                "dislikes": ["과도한 액션", "잔혹함"],
                "evaluation_focus": ["감정 묘사", "캐릭터 관계", "심리 변화"]
            },
            3: {
                "type": "세계관_중시", 
                "age": 30, 
                "gender": "남성",
                "preferences": ["설정", "시스템", "논리성"],
                "dislikes": ["설정 오류", "비논리적 전개"],
                "evaluation_focus": ["세계관 일관성", "설정 완성도", "시스템 이해도"]
            },
            4: {
                "type": "캐릭터_중심", 
                "age": 22, 
                "gender": "여성",
                "preferences": ["인물 매력", "성격", "대화"],
                "dislikes": ["평면적 캐릭터", "성격 변화 없음"],
                "evaluation_focus": ["캐릭터 매력도", "개성", "발전 과정"]
            },
            5: {
                "type": "완결성_중시", 
                "age": 35, 
                "gender": "남성",
                "preferences": ["논리적 전개", "명확한 결말", "떡밥 회수"],
                "dislikes": ["미완결", "애매한 결말", "논리 오류"],
                "evaluation_focus": ["스토리 완성도", "논리성", "개연성"]
            },
            6: {
                "type": "몰입도_중시", 
                "age": 19, 
                "gender": "여성",
                "preferences": ["재미", "흥미", "집중"],
                "dislikes": ["지루함", "복잡함", "어려운 표현"],
                "evaluation_focus": ["재미요소", "흥미진진함", "읽기 편함"]
            },
            7: {
                "type": "문체_중시", 
                "age": 28, 
                "gender": "남성",
                "preferences": ["우아한 문체", "표현력", "문학성"],
                "dislikes": ["어색한 문장", "유치한 표현"],
                "evaluation_focus": ["문장력", "표현의 적절성", "문체 통일성"]
            },
            8: {
                "type": "장르순수성", 
                "age": 24, 
                "gender": "여성",
                "preferences": ["장르적 특색", "클리셰 활용", "왕도적 전개"],
                "dislikes": ["장르 혼재", "예측 불가능한 전개"],
                "evaluation_focus": ["장르 특성", "기대 충족도", "클리셰 활용"]
            },
            9: {
                "type": "현실성_중시", 
                "age": 32, 
                "gender": "남성",
                "preferences": ["현실적 묘사", "개연성", "논리"],
                "dislikes": ["비현실적 설정", "갑작스런 전개"],
                "evaluation_focus": ["현실감", "개연성", "논리적 타당성"]
            },
            10: {
                "type": "전개속도중시", 
                "age": 21, 
                "gender": "여성",
                "preferences": ["빠른 전개", "다이나믹", "변화"],
                "dislikes": ["느린 전개", "반복", "정체"],
                "evaluation_focus": ["전개 속도", "변화량", "다이나믹함"]
            }
        }
        
        logger.info("독자 에이전트 초기화 완료 - 10개 페르소나 설정")
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """작업 실행"""
        task_type = task.get('type')
        
        if task_type == 'evaluate_from_reader_perspective':
            return await self.evaluate_from_reader_perspective(task)
        else:
            return {"error": f"Unknown task type: {task_type}"}
    
    async def evaluate_from_reader_perspective(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """독자 관점에서 평가"""
        episode_num = task.get('episode_number')
        persona_id = task.get('persona_id', 1)
        
        # 에피소드 내용 로드
        content = project_loader.get_episode_content(episode_num)
        if not content:
            return {"error": f"에피소드 {episode_num}화를 찾을 수 없습니다"}
        
        # 페르소나 정보 가져오기
        persona = self.personas.get(persona_id, self.personas[1])
        
        logger.info(f"📚 독자 에이전트: {episode_num}화를 {persona['type']} 관점에서 평가")
        
        # 페르소나별 평가 수행
        evaluation_result = await self.perform_persona_evaluation(content, persona, episode_num)
        
        result = {
            'episode_number': episode_num,
            'persona_id': persona_id,
            'persona_type': persona['type'],
            'persona_info': {
                'age': persona['age'],
                'gender': persona['gender'],
                'preferences': persona['preferences'],
                'evaluation_focus': persona['evaluation_focus']
            },
            'reader_score': evaluation_result['score'],
            'engagement_level': evaluation_result['engagement'],
            'satisfaction_level': evaluation_result['satisfaction'],
            'specific_feedback': evaluation_result['feedback'],
            'likes': evaluation_result['likes'],
            'dislikes': evaluation_result['dislikes'],
            'recommendations': evaluation_result['recommendations'],
            'target_audience_fit': evaluation_result['target_fit'],
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"✅ {persona['type']} 독자 평가 완료 - 점수: {evaluation_result['score']:.1f}/10")
        
        return result
    
    async def perform_persona_evaluation(self, content: str, persona: Dict, episode_num: int) -> Dict[str, Any]:
        """페르소나별 평가 수행"""
        
        # 기본 점수 (6.0에서 시작)
        base_score = 6.0
        
        # 페르소나별 특화 평가
        if persona['type'] == '액션_선호':
            evaluation = self.evaluate_action_elements(content, persona)
        elif persona['type'] == '로맨스_선호':
            evaluation = self.evaluate_emotional_elements(content, persona)
        elif persona['type'] == '세계관_중시':
            evaluation = self.evaluate_worldbuilding_elements(content, persona)
        elif persona['type'] == '캐릭터_중심':
            evaluation = self.evaluate_character_elements(content, persona)
        elif persona['type'] == '완결성_중시':
            evaluation = self.evaluate_narrative_completeness(content, persona)
        elif persona['type'] == '몰입도_중시':
            evaluation = self.evaluate_engagement_elements(content, persona)
        elif persona['type'] == '문체_중시':
            evaluation = self.evaluate_writing_style(content, persona)
        elif persona['type'] == '장르순수성':
            evaluation = self.evaluate_genre_elements(content, persona)
        elif persona['type'] == '현실성_중시':
            evaluation = self.evaluate_realism_elements(content, persona)
        elif persona['type'] == '전개속도중시':
            evaluation = self.evaluate_pacing_elements(content, persona)
        else:
            evaluation = self.evaluate_general_elements(content, persona)
        
        # 최종 점수 계산
        final_score = base_score + evaluation['bonus_score'] - evaluation['penalty_score']
        final_score = max(min(final_score, 10.0), 1.0)  # 1.0-10.0 범위
        
        return {
            'score': round(final_score, 1),
            'engagement': evaluation['engagement'],
            'satisfaction': evaluation['satisfaction'],
            'feedback': evaluation['feedback'],
            'likes': evaluation['likes'],
            'dislikes': evaluation['dislikes'],
            'recommendations': evaluation['recommendations'],
            'target_fit': evaluation.get('target_fit', 'medium')
        }
    
    def evaluate_action_elements(self, content: str, persona: Dict) -> Dict[str, Any]:
        """액션 요소 평가"""
        bonus_score = 0.0
        penalty_score = 0.0
        likes = []
        dislikes = []
        
        # 액션 키워드 체크
        action_keywords = ['싸움', '전투', '공격', '방어', '달려들었다', '피했다', '때렸다', '막았다']
        action_count = sum(content.count(keyword) for keyword in action_keywords)
        
        if action_count >= 5:
            bonus_score += 2.0
            likes.append('충분한 액션 요소')
        elif action_count >= 2:
            bonus_score += 1.0
            likes.append('적당한 액션 요소')
        else:
            penalty_score += 1.0
            dislikes.append('액션 부족')
        
        # 긴장감 키워드 체크
        tension_keywords = ['긴장', '위험', '급박', '빠르게', '서둘러']
        tension_count = sum(content.count(keyword) for keyword in tension_keywords)
        
        if tension_count >= 3:
            bonus_score += 1.0
            likes.append('긴장감 있는 전개')
        
        # 로맨스 과다시 감점
        romance_keywords = ['사랑', '마음', '감정', '좋아한다']
        romance_count = sum(content.count(keyword) for keyword in romance_keywords)
        
        if romance_count >= 5:
            penalty_score += 0.5
            dislikes.append('로맨스 요소 과다')
        
        engagement = 'high' if action_count >= 3 else 'medium' if action_count >= 1 else 'low'
        satisfaction = 'high' if bonus_score > penalty_score else 'medium'
        
        return {
            'bonus_score': bonus_score,
            'penalty_score': penalty_score,
            'engagement': engagement,
            'satisfaction': satisfaction,
            'feedback': f'액션 요소 {action_count}개, 긴장감 요소 {tension_count}개 발견',
            'likes': likes,
            'dislikes': dislikes,
            'recommendations': ['더 역동적인 전투 묘사', '스피드감 있는 전개']
        }
    
    def evaluate_emotional_elements(self, content: str, persona: Dict) -> Dict[str, Any]:
        """감정적 요소 평가 (로맨스 선호)"""
        bonus_score = 0.0
        penalty_score = 0.0
        likes = []
        dislikes = []
        
        # 감정 표현 체크
        emotion_keywords = ['느꼈다', '생각했다', '마음', '감정', '기분', '슬펐다', '기뻤다']
        emotion_count = sum(content.count(keyword) for keyword in emotion_keywords)
        
        if emotion_count >= 5:
            bonus_score += 2.0
            likes.append('풍부한 감정 표현')
        elif emotion_count >= 2:
            bonus_score += 1.0
            likes.append('적절한 감정 묘사')
        
        # 관계성 키워드 체크
        relationship_keywords = ['함께', '서로', '관계', '친구', '동료', '믿음']
        relationship_count = sum(content.count(keyword) for keyword in relationship_keywords)
        
        if relationship_count >= 3:
            bonus_score += 1.0
            likes.append('인물간 관계 발전')
        
        # 과도한 액션시 감점
        violence_keywords = ['피', '죽음', '폭력', '잔혹']
        violence_count = sum(content.count(keyword) for keyword in violence_keywords)
        
        if violence_count >= 3:
            penalty_score += 0.5
            dislikes.append('잔혹한 묘사')
        
        engagement = 'high' if emotion_count >= 3 else 'medium'
        satisfaction = 'high' if relationship_count >= 2 else 'medium'
        
        return {
            'bonus_score': bonus_score,
            'penalty_score': penalty_score,
            'engagement': engagement,
            'satisfaction': satisfaction,
            'feedback': f'감정 표현 {emotion_count}개, 관계성 요소 {relationship_count}개',
            'likes': likes,
            'dislikes': dislikes,
            'recommendations': ['캐릭터 간 감정적 교감 강화', '내적 갈등 묘사 추가']
        }
    
    def evaluate_worldbuilding_elements(self, content: str, persona: Dict) -> Dict[str, Any]:
        """세계관 요소 평가"""
        bonus_score = 0.0
        penalty_score = 0.0
        likes = []
        dislikes = []
        
        # 세계관 설정 키워드
        worldbuilding_keywords = ['공명력', '시스템', '설정', '규칙', '세계', '능력', '힘']
        world_count = sum(content.count(keyword) for keyword in worldbuilding_keywords)
        
        if world_count >= 5:
            bonus_score += 2.5
            likes.append('세계관 설정이 잘 드러남')
        elif world_count >= 2:
            bonus_score += 1.0
            likes.append('적절한 설정 설명')
        else:
            penalty_score += 1.0
            dislikes.append('세계관 설명 부족')
        
        # 논리성 키워드
        logic_keywords = ['왜냐하면', '때문에', '따라서', '그러므로', '이유']
        logic_count = sum(content.count(keyword) for keyword in logic_keywords)
        
        if logic_count >= 3:
            bonus_score += 1.0
            likes.append('논리적 설명')
        
        # 설정 오류 (일반적인 판타지 용어 사용시)
        error_keywords = ['마나', '마법', '레벨업', 'MP']
        error_count = sum(content.count(keyword) for keyword in error_keywords)
        
        if error_count > 0:
            penalty_score += 2.0
            dislikes.append('설정 일관성 오류')
        
        engagement = 'high' if world_count >= 4 else 'medium'
        satisfaction = 'high' if error_count == 0 else 'low'
        
        return {
            'bonus_score': bonus_score,
            'penalty_score': penalty_score,
            'engagement': engagement,
            'satisfaction': satisfaction,
            'feedback': f'세계관 요소 {world_count}개, 논리적 연결 {logic_count}개',
            'likes': likes,
            'dislikes': dislikes,
            'recommendations': ['세계관 설정 상세화', '시스템 작동 원리 명확화']
        }
    
    def evaluate_character_elements(self, content: str, persona: Dict) -> Dict[str, Any]:
        """캐릭터 요소 평가"""
        bonus_score = 0.0
        penalty_score = 0.0
        likes = []
        dislikes = []
        
        # 대화 비율 체크
        dialogue_count = content.count('"') + content.count("'")
        if dialogue_count >= 10:
            bonus_score += 2.0
            likes.append('풍부한 대화')
        elif dialogue_count >= 5:
            bonus_score += 1.0
            likes.append('적절한 대화량')
        
        # 캐릭터 심리 묘사
        psychology_keywords = ['생각', '느낌', '마음', '의도', '판단', '결심']
        psychology_count = sum(content.count(keyword) for keyword in psychology_keywords)
        
        if psychology_count >= 5:
            bonus_score += 1.5
            likes.append('심리 묘사가 풍부')
        
        # 캐릭터 행동 다양성
        action_variety = ['말했다', '웃었다', '고개를', '손을', '일어났다', '앉았다']
        variety_count = sum(1 for action in action_variety if action in content)
        
        if variety_count >= 4:
            bonus_score += 1.0
            likes.append('다양한 행동 묘사')
        
        engagement = 'high' if dialogue_count >= 8 else 'medium'
        satisfaction = 'high' if psychology_count >= 3 else 'medium'
        
        return {
            'bonus_score': bonus_score,
            'penalty_score': penalty_score,
            'engagement': engagement,
            'satisfaction': satisfaction,
            'feedback': f'대화 {dialogue_count}회, 심리묘사 {psychology_count}개',
            'likes': likes,
            'dislikes': dislikes,
            'recommendations': ['캐릭터 개성 강화', '내적 갈등 추가']
        }
    
    def evaluate_general_elements(self, content: str, persona: Dict) -> Dict[str, Any]:
        """일반적 요소 평가"""
        bonus_score = 1.0  # 기본 보너스
        penalty_score = 0.0
        
        # 기본 품질 체크
        word_count = len(content.split())
        if word_count >= 1500:
            bonus_score += 0.5
        
        paragraph_count = len(content.split('\n\n'))
        if 5 <= paragraph_count <= 15:
            bonus_score += 0.5
        
        return {
            'bonus_score': bonus_score,
            'penalty_score': penalty_score,
            'engagement': 'medium',
            'satisfaction': 'medium',
            'feedback': f'일반적 품질 평가: {word_count}자, {paragraph_count}문단',
            'likes': ['평균적 품질'],
            'dislikes': [],
            'recommendations': ['장르 특성 강화']
        }
    
    def evaluate_engagement_elements(self, content: str, persona: Dict) -> Dict[str, Any]:
        """몰입도 요소 평가"""
        bonus_score = 0.0
        penalty_score = 0.0
        likes = []
        dislikes = []
        
        # 흥미 요소
        interest_keywords = ['궁금', '놀라운', '신기한', '재미있', '흥미진진']
        interest_count = sum(content.count(keyword) for keyword in interest_keywords)
        
        if interest_count >= 2:
            bonus_score += 1.5
            likes.append('흥미로운 요소')
        
        # 복잡함 체크 (어려운 단어 사용)
        difficult_words = ['상황', '체계', '시스템', '구조', '원리', '이론']
        difficulty = sum(content.count(word) for word in difficult_words)
        
        if difficulty >= 5:
            penalty_score += 0.5
            dislikes.append('다소 복잡한 표현')
        
        engagement = 'high' if interest_count >= 2 else 'medium'
        satisfaction = 'high' if difficulty < 3 else 'medium'
        
        return {
            'bonus_score': bonus_score,
            'penalty_score': penalty_score,
            'engagement': engagement,
            'satisfaction': satisfaction,
            'feedback': f'흥미 요소 {interest_count}개, 복잡도 {difficulty}',
            'likes': likes,
            'dislikes': dislikes,
            'recommendations': ['더 재미있는 요소 추가', '쉽고 명확한 표현']
        }
    
    def evaluate_narrative_completeness(self, content: str, persona: Dict) -> Dict[str, Any]:
        """완결성 평가 (완결성 중시 독자)"""
        bonus_score = 0.0
        penalty_score = 0.0
        likes = []
        dislikes = []
        
        # 논리적 연결성 체크
        logic_keywords = ['때문에', '따라서', '그러므로', '왜냐하면', '결과적으로']
        logic_count = sum(content.count(keyword) for keyword in logic_keywords)
        
        if logic_count >= 3:
            bonus_score += 2.0
            likes.append('논리적 전개')
        elif logic_count >= 1:
            bonus_score += 1.0
            likes.append('일부 논리적 연결')
        
        # 명확한 결말/결론
        conclusion_keywords = ['결국', '마침내', '드디어', '최종적으로', '결론적으로']
        conclusion_count = sum(content.count(keyword) for keyword in conclusion_keywords)
        
        if conclusion_count >= 1:
            bonus_score += 1.0
            likes.append('명확한 결론')
        
        # 애매한 표현 체크
        vague_keywords = ['아마도', '어쩌면', '그런 것 같다', '모호한']
        vague_count = sum(content.count(keyword) for keyword in vague_keywords)
        
        if vague_count >= 3:
            penalty_score += 1.0
            dislikes.append('애매한 표현')
        
        engagement = 'high' if logic_count >= 2 else 'medium'
        satisfaction = 'high' if conclusion_count >= 1 else 'medium'
        
        return {
            'bonus_score': bonus_score,
            'penalty_score': penalty_score,
            'engagement': engagement,
            'satisfaction': satisfaction,
            'feedback': f'논리적 연결 {logic_count}개, 명확한 결론 {conclusion_count}개',
            'likes': likes,
            'dislikes': dislikes,
            'recommendations': ['논리적 인과관계 강화', '명확한 결말 제시']
        }
    
    def evaluate_writing_style(self, content: str, persona: Dict) -> Dict[str, Any]:
        """문체 평가 (문체 중시 독자)"""
        bonus_score = 0.0
        penalty_score = 0.0
        likes = []
        dislikes = []
        
        # 문장 다양성 체크
        sentences = content.split('.')
        avg_sentence_length = sum(len(s.strip()) for s in sentences) / len(sentences) if sentences else 0
        
        if 20 <= avg_sentence_length <= 40:
            bonus_score += 1.5
            likes.append('적절한 문장 길이')
        elif avg_sentence_length < 10:
            penalty_score += 1.0
            dislikes.append('너무 짧은 문장')
        elif avg_sentence_length > 60:
            penalty_score += 0.5
            dislikes.append('너무 긴 문장')
        
        # 표현의 우아함
        elegant_expressions = ['~하였다', '~였다', '~되었다', '~있었다']
        elegant_count = sum(content.count(expr) for expr in elegant_expressions)
        
        if elegant_count >= 5:
            bonus_score += 1.0
            likes.append('우아한 표현')
        
        # 어색한 표현 체크
        awkward_expressions = ['~해졌다', '~당했다', '~되어버렸다']
        awkward_count = sum(content.count(expr) for expr in awkward_expressions)
        
        if awkward_count >= 3:
            penalty_score += 1.0
            dislikes.append('어색한 표현')
        
        engagement = 'high' if elegant_count >= 3 else 'medium'
        satisfaction = 'high' if awkward_count == 0 else 'medium'
        
        return {
            'bonus_score': bonus_score,
            'penalty_score': penalty_score,
            'engagement': engagement,
            'satisfaction': satisfaction,
            'feedback': f'평균 문장길이 {avg_sentence_length:.1f}자, 우아한 표현 {elegant_count}개',
            'likes': likes,
            'dislikes': dislikes,
            'recommendations': ['문체 통일성 강화', '표현의 세련됨 개선']
        }
    
    def evaluate_genre_elements(self, content: str, persona: Dict) -> Dict[str, Any]:
        """장르 요소 평가 (장르순수성 중시 독자)"""
        bonus_score = 0.0
        penalty_score = 0.0
        likes = []
        dislikes = []
        
        # 포스트 아포칼립스 장르 요소
        apocalypse_keywords = ['폐허', '재앙', '생존', '멸망', '파괴된', '황폐한']
        apocalypse_count = sum(content.count(keyword) for keyword in apocalypse_keywords)
        
        if apocalypse_count >= 2:
            bonus_score += 2.0
            likes.append('포스트 아포칼립스 분위기')
        elif apocalypse_count >= 1:
            bonus_score += 1.0
            likes.append('일부 장르 요소')
        
        # 판타지 요소 (공명력 시스템)
        fantasy_keywords = ['공명력', '능력', '힘', '특별한', '초자연적']
        fantasy_count = sum(content.count(keyword) for keyword in fantasy_keywords)
        
        if fantasy_count >= 3:
            bonus_score += 1.5
            likes.append('판타지 요소 적절')
        
        # 다른 장르 혼재 체크
        other_genre_keywords = ['마법', '마나', '드래곤', '엘프', '학교', '일상']
        other_count = sum(content.count(keyword) for keyword in other_genre_keywords)
        
        if other_count >= 2:
            penalty_score += 1.5
            dislikes.append('장르 혼재')
        
        engagement = 'high' if apocalypse_count >= 2 else 'medium'
        satisfaction = 'high' if other_count == 0 else 'low'
        
        return {
            'bonus_score': bonus_score,
            'penalty_score': penalty_score,
            'engagement': engagement,
            'satisfaction': satisfaction,
            'feedback': f'포스트아포칼립스 {apocalypse_count}개, 판타지 {fantasy_count}개',
            'likes': likes,
            'dislikes': dislikes,
            'recommendations': ['장르 특성 강화', '클리셰 적절한 활용']
        }
    
    def evaluate_realism_elements(self, content: str, persona: Dict) -> Dict[str, Any]:
        """현실성 평가 (현실성 중시 독자)"""
        bonus_score = 0.0
        penalty_score = 0.0
        likes = []
        dislikes = []
        
        # 현실적 묘사
        realistic_keywords = ['자연스럽게', '현실적으로', '실제로', '사실', '진짜']
        realistic_count = sum(content.count(keyword) for keyword in realistic_keywords)
        
        if realistic_count >= 2:
            bonus_score += 1.5
            likes.append('현실적 묘사')
        
        # 개연성 있는 전개
        logical_keywords = ['당연히', '자연스럽게', '예상대로', '그럴만하다']
        logical_count = sum(content.count(keyword) for keyword in logical_keywords)
        
        if logical_count >= 2:
            bonus_score += 1.0
            likes.append('개연성 있는 전개')
        
        # 비현실적 요소
        unrealistic_keywords = ['갑자기', '순간적으로', '마법처럼', '기적적으로']
        unrealistic_count = sum(content.count(keyword) for keyword in unrealistic_keywords)
        
        if unrealistic_count >= 3:
            penalty_score += 1.0
            dislikes.append('급작스런 전개')
        
        engagement = 'high' if realistic_count >= 2 else 'medium'
        satisfaction = 'high' if unrealistic_count <= 1 else 'low'
        
        return {
            'bonus_score': bonus_score,
            'penalty_score': penalty_score,
            'engagement': engagement,
            'satisfaction': satisfaction,
            'feedback': f'현실적 묘사 {realistic_count}개, 비현실적 요소 {unrealistic_count}개',
            'likes': likes,
            'dislikes': dislikes,
            'recommendations': ['개연성 강화', '논리적 타당성 개선']
        }
    
    def evaluate_pacing_elements(self, content: str, persona: Dict) -> Dict[str, Any]:
        """페이싱 평가 (전개속도 중시 독자)"""
        bonus_score = 0.0
        penalty_score = 0.0
        likes = []
        dislikes = []
        
        # 빠른 전개 키워드
        fast_keywords = ['빠르게', '서둘러', '급히', '즉시', '곧바로', '빨리']
        fast_count = sum(content.count(keyword) for keyword in fast_keywords)
        
        if fast_count >= 3:
            bonus_score += 2.0
            likes.append('빠른 전개')
        elif fast_count >= 1:
            bonus_score += 1.0
            likes.append('적당한 속도감')
        
        # 다이나믹한 변화
        change_keywords = ['변했다', '바뀌었다', '달라졌다', '새로운', '다른']
        change_count = sum(content.count(keyword) for keyword in change_keywords)
        
        if change_count >= 2:
            bonus_score += 1.0
            likes.append('다이나믹한 변화')
        
        # 느린 전개 (반복, 정체)
        slow_keywords = ['천천히', '느리게', '오랫동안', '계속', '반복']
        slow_count = sum(content.count(keyword) for keyword in slow_keywords)
        
        if slow_count >= 3:
            penalty_score += 1.0
            dislikes.append('느린 전개')
        
        engagement = 'high' if fast_count >= 2 else 'medium'
        satisfaction = 'high' if change_count >= 2 else 'medium'
        
        return {
            'bonus_score': bonus_score,
            'penalty_score': penalty_score,
            'engagement': engagement,
            'satisfaction': satisfaction,
            'feedback': f'속도감 {fast_count}개, 변화요소 {change_count}개',
            'likes': likes,
            'dislikes': dislikes,
            'recommendations': ['더 빠른 전개', '다양한 변화 추가']
        }