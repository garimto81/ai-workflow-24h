"""
작가 에이전트 (Writer Agent)
글쓰기 및 창작 담당 에이전트 - 새로운 메인 조율 시스템용
스토리 전개, 플롯 구성, 캐릭터 개발 등을 담당
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path
import logging

from .base_agent import BaseAgent
from .project_loader import project_loader

logger = logging.getLogger(__name__)


class WriterAgent(BaseAgent):
    """작가 에이전트 - 메인 조율 시스템용"""
    
    def __init__(self):
        super().__init__("Writer")
        
        # 스토리 패턴 및 가이드
        self.story_patterns = {}
        self.character_development = {}
        self.plot_structures = {}
    
    async def initialize(self):
        """작가 에이전트 초기화"""
        logger.info("작가 에이전트 초기화")
        
        # 스토리 패턴 로드
        await self.load_story_patterns()
        
        # 캐릭터 개발 가이드 로드  
        await self.load_character_guides()
        
        logger.info("작가 에이전트 초기화 완료")
    
    async def load_story_patterns(self):
        """스토리 패턴 및 구조 로드"""
        # Classic Isekai 장르 특성
        self.story_patterns = {
            'genre': 'post_apocalyptic_fantasy',
            'main_elements': ['survival', 'resonance_system', 'character_growth'],
            'target_word_count': {'min': 1500, 'max': 3000, 'optimal': 2000}
        }
    
    async def load_character_guides(self):
        """캐릭터 개발 가이드 로드"""
        # 주인공 설정 문서 참조
        try:
            protagonist_doc = project_loader.documents.get('world_setting/100_protagonist.md', '')
        except:
            protagonist_doc = ''
        
        if protagonist_doc:
            self.character_development = {
                'protagonist_traits': self.extract_character_traits(protagonist_doc),
                'development_arc': 'reluctant_hero_to_confident_leader'
            }
        else:
            # 기본 캐릭터 설정
            self.character_development = {
                'protagonist_traits': ['적응력', '리더십', '공감능력'],
                'development_arc': 'standard_growth'
            }
    
    def extract_character_traits(self, document: str) -> List[str]:
        """문서에서 캐릭터 특성 추출"""
        traits = []
        keywords = ['성격', '특성', '능력', '성향']
        
        for line in document.split('\n'):
            for keyword in keywords:
                if keyword in line:
                    traits.append(line.strip())
        
        return traits[:5]  # 상위 5개만
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """작업 실행"""
        task_type = task.get('type')
        
        if task_type == 'analyze_story':
            return await self.analyze_story_structure(task)
        elif task_type == 'create_episode':
            return await self.create_episode(task)
        elif task_type == 'revise_episode':
            return await self.revise_episode(task)
        elif task_type == 'improve_plot':
            return await self.improve_plot_development(task)
        else:
            return {"error": f"Unknown task type: {task_type}"}
    
    async def analyze_story_structure(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """스토리 구조 분석 (메인 조율 시스템용)"""
        episode_num = task.get('episode_number')
        priority_areas = task.get('priority_areas', [])
        
        # 에피소드 내용 로드
        content = project_loader.get_episode_content(episode_num)
        if not content:
            return {"error": f"에피소드 {episode_num}화를 찾을 수 없습니다"}
        
        logger.info(f"📖 작가 에이전트: {episode_num}화 스토리 구조 분석")
        
        # 기본 구조 분석
        word_count = len(content.split())
        paragraph_count = len(content.split('\n\n'))
        
        # 구조 점수 계산
        structure_score = 5.0  # 기본 점수
        
        target_words = self.story_patterns['target_word_count']
        if target_words['min'] <= word_count <= target_words['max']:
            structure_score += 2.0
        
        if 5 <= paragraph_count <= 15:
            structure_score += 1.0
        
        # 플롯 요소 체크
        conflict_present = any(word in content for word in ['문제', '위험', '갈등', '어려움', '위기'])
        motivation_clear = any(word in content for word in ['왜', '때문에', '목적', '이유'])
        logical_flow = any(word in content for word in ['그래서', '따라서', '결국', '그러나'])
        
        plot_score = 5.0
        if conflict_present:
            plot_score += 1.0
        if motivation_clear:
            plot_score += 1.0
        if logical_flow:
            plot_score += 1.0
        
        # 캐릭터 요소 체크  
        has_dialogue = '"' in content or "'" in content
        has_thoughts = any(word in content for word in ['생각했다', '느꼈다', '깨달았다'])
        has_actions = any(word in content for word in ['했다', '갔다', '움직였다'])
        
        character_score = 5.0
        if has_dialogue:
            character_score += 1.0
        if has_thoughts:
            character_score += 1.0
        if has_actions:
            character_score += 1.0
        
        # 전체 점수 계산
        story_score = (structure_score * 0.2) + (plot_score * 0.4) + (character_score * 0.4)
        
        # 문제점 식별
        plot_issues = []
        if not conflict_present:
            plot_issues.append('갈등 요소 부족')
        if not motivation_clear:
            plot_issues.append('캐릭터 동기 불분명')
        if word_count < 1000:
            plot_issues.append('내용 분량 부족')
        if not has_dialogue:
            plot_issues.append('대화 부족')
        
        # 개선 제안
        suggestions = []
        if structure_score < 6.0:
            suggestions.append('문단 구성 재조정으로 읽기 흐름 개선')
        if plot_score < 6.0:
            suggestions.append('갈등 구조 강화 및 긴장감 증대')
        if character_score < 6.0:
            suggestions.append('캐릭터 심리 묘사 강화')
        
        suggestions.extend([
            '포스트 아포칼립스 분위기 강화',
            '공명력 시스템 활용도 증대'
        ])
        
        result = {
            'episode_number': episode_num,
            'story_score': round(story_score, 1),
            'structure_analysis': {
                'word_count': word_count,
                'paragraph_count': paragraph_count,
                'structure_score': structure_score
            },
            'plot_evaluation': {
                'plot_score': plot_score,
                'conflict_present': conflict_present,
                'motivation_clear': motivation_clear,
                'logical_flow': logical_flow
            },
            'character_analysis': {
                'character_score': character_score,
                'has_dialogue': has_dialogue,
                'has_thoughts': has_thoughts,
                'has_actions': has_actions
            },
            'plot_issues': plot_issues,
            'suggestions': suggestions,
            'priority_recommendations': [f'{area} 개선 필요' for area in priority_areas],
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"✅ {episode_num}화 스토리 분석 완료 - 점수: {story_score:.1f}/10")
        
        return result
    
    async def improve_plot_development(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """플롯 개발 개선"""
        episode_num = task.get('episode_number')
        improvement_areas = task.get('improvement_areas', [])
        
        improvements = []
        
        for area in improvement_areas:
            if area == 'conflict_enhancement':
                improvements.append('갈등 상황을 더욱 구체적으로 묘사하고 이해관계를 명확히')
            elif area == 'pacing_adjustment':
                improvements.append('전개 속도 조절을 통한 긴장감 조절')
            elif area == 'character_motivation':
                improvements.append('캐릭터 행동의 내적 동기 강화')
        
        return {
            'episode_number': episode_num,
            'improvements': improvements,
            'status': 'completed'
        }
    
    async def create_episode(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """새 에피소드 생성"""
        logger.info("새 에피소드 생성 시작")
        
        # 이전 내용 가져오기
        previous_content = task.get('previous_content', '')
        episode_number = len(self.story_memory['episodes']) + 1
        
        # 프롬프트 생성
        prompt = self.build_episode_prompt(episode_number, previous_content)
        
        # Claude로 에피소드 생성
        episode_content = await self.call_claude(prompt, max_tokens=4000)
        
        # 에피소드 후처리
        processed_episode = await self.post_process_episode(episode_content)
        
        # 메모리 업데이트
        self.update_story_memory(processed_episode, episode_number)
        
        result = {
            "episode_number": episode_number,
            "content": processed_episode,
            "word_count": len(processed_episode),
            "created_at": datetime.now().isoformat()
        }
        
        logger.info(f"에피소드 {episode_number} 생성 완료 ({len(processed_episode)}자)")
        
        return result
    
    def build_episode_prompt(self, episode_number: int, previous_content: str) -> str:
        """에피소드 생성 프롬프트 구성"""
        
        # 기본 설정
        prompt = f"""당신은 한국 웹소설 전문 작가입니다.
다음 설정으로 {episode_number}화를 작성해주세요.

【작품 정보】
제목: {self.novel_config['title']}
장르: {self.novel_config['genre']}
태그: {', '.join(self.novel_config['tags'])}

【세계관】
세계: {self.novel_config['settings']['world_name']}
시대: {self.novel_config['settings']['time_period']}
주인공: {self.novel_config['settings']['main_character']}

【이전 줄거리】
{previous_content[-2000:] if previous_content else '첫 화입니다. 주인공이 회귀하는 장면부터 시작하세요.'}

【작성 지침】
1. 분량: {self.episode_length}자 내외
2. 문체: {self.style} 스타일
3. 포함 요소:
   - 긴장감 있는 전개
   - 주인공의 성장
   - 적절한 액션과 대화
   - 다음 화를 기대하게 하는 마무리

4. 주의사항:
   - AI 특유의 짧은 문장 나열 금지
   - 자연스러운 감정 묘사
   - 과도한 설명 자제
   - 독자 몰입을 해치지 않는 전개

【{episode_number}화 핵심】
"""
        
        # 에피소드별 특별 지시
        if episode_number == 1:
            prompt += "- 임팩트 있는 도입부\n- 주인공의 회귀 상황 설명\n- 세계관 자연스럽게 소개"
        elif episode_number % 10 == 0:
            prompt += "- 중요한 전환점\n- 새로운 갈등 도입\n- 클리프행어 엔딩"
        else:
            prompt += "- 이전 화의 자연스러운 연결\n- 스토리 진행\n- 캐릭터 발전"
        
        prompt += f"\n\n이제 {episode_number}화를 작성해주세요:"
        
        return prompt
    
    async def post_process_episode(self, content: str) -> str:
        """에피소드 후처리"""
        
        # 기본 정리
        content = content.strip()
        
        # 챕터 제목 추가 (없으면)
        if not content.startswith("제"):
            episode_num = len(self.story_memory['episodes']) + 1
            content = f"제{episode_num}화\n\n{content}"
        
        # 문단 정리
        paragraphs = content.split('\n')
        cleaned_paragraphs = []
        
        for para in paragraphs:
            para = para.strip()
            if para:
                # 너무 짧은 문단 합치기
                if len(para) < 50 and cleaned_paragraphs:
                    cleaned_paragraphs[-1] += " " + para
                else:
                    cleaned_paragraphs.append(para)
        
        return '\n\n'.join(cleaned_paragraphs)
    
    def update_story_memory(self, episode: str, episode_number: int):
        """스토리 메모리 업데이트"""
        
        # 에피소드 저장
        self.story_memory['episodes'].append({
            "number": episode_number,
            "content": episode[:500],  # 요약만 저장
            "created_at": datetime.now().isoformat()
        })
        
        # 주요 플롯 포인트 추출 (간단한 키워드 기반)
        plot_keywords = ['결정적', '전환점', '비밀', '발견', '각성']
        for keyword in plot_keywords:
            if keyword in episode:
                self.story_memory['plot_points'].append({
                    "episode": episode_number,
                    "keyword": keyword,
                    "context": episode[max(0, episode.find(keyword)-50):episode.find(keyword)+50]
                })
        
        # 메모리 저장
        self.save_memory("story", self.story_memory)
    
    async def revise_episode(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """에피소드 수정"""
        content = task.get('content', '')
        feedback = task.get('feedback', [])
        
        logger.info("에피소드 수정 시작")
        
        # 수정 프롬프트 생성
        prompt = f"""다음 웹소설 에피소드를 피드백에 따라 수정해주세요.

【원본 에피소드】
{content}

【수정 요청 사항】
"""
        
        for i, fb in enumerate(feedback, 1):
            prompt += f"{i}. {fb}\n"
        
        prompt += """
【수정 지침】
- 원본의 핵심 스토리는 유지
- 피드백 사항 충실히 반영
- 자연스러운 문체 유지
- 분량 유지 ({self.episode_length}자)

수정된 에피소드:
"""
        
        # Claude로 수정
        revised_content = await self.call_claude(prompt, max_tokens=4000)
        
        # 후처리
        revised_content = await self.post_process_episode(revised_content)
        
        return {
            "content": revised_content,
            "revisions_applied": len(feedback),
            "revised_at": datetime.now().isoformat()
        }
    
    async def create_outline(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """에피소드 아웃라인 생성"""
        
        episodes_count = task.get('episodes_count', 10)
        
        prompt = f"""웹소설 '{self.novel_config['title']}'의 향후 {episodes_count}개 에피소드 아웃라인을 작성해주세요.

【현재까지의 진행 상황】
- 완성된 에피소드: {len(self.story_memory['episodes'])}화
- 주요 플롯 포인트: {len(self.story_memory['plot_points'])}개

【아웃라인 형식】
각 에피소드별로:
- 에피소드 번호
- 제목
- 핵심 사건 (2-3문장)
- 캐릭터 발전
- 다음 화로의 연결고리

작성해주세요:
"""
        
        outline = await self.call_claude(prompt, max_tokens=2000)
        
        return {
            "outline": outline,
            "episodes_planned": episodes_count,
            "created_at": datetime.now().isoformat()
        }