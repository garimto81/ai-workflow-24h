"""
연관성 분석 에이전트 - 에피소드 간 일관성 및 연결성 분석
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import logging
from collections import defaultdict, Counter
import networkx as nx

from base_agent import BaseAgent

logger = logging.getLogger(__name__)


class StoryGraph:
    """스토리 요소 간 관계를 그래프로 관리"""
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.character_arcs = defaultdict(list)
        self.plot_threads = defaultdict(dict)
        self.foreshadowing = defaultdict(list)
        
    def add_episode_node(self, episode_id: int, metadata: Dict):
        """에피소드 노드 추가"""
        self.graph.add_node(f"ep_{episode_id}", **metadata)
        
    def add_connection(self, from_ep: int, to_ep: int, connection_type: str, strength: float):
        """에피소드 간 연결 추가"""
        self.graph.add_edge(
            f"ep_{from_ep}", 
            f"ep_{to_ep}",
            type=connection_type,
            strength=strength
        )
        
    def analyze_connectivity(self) -> Dict:
        """전체 연결성 분석"""
        return {
            'density': nx.density(self.graph),
            'components': list(nx.weakly_connected_components(self.graph)),
            'central_episodes': nx.degree_centrality(self.graph)
        }


class CorrelationAnalystAgent(BaseAgent):
    """에피소드 간 연관성 및 일관성 분석 에이전트"""
    
    def __init__(self):
        super().__init__("CorrelationAnalystAgent")
        
        self.story_graph = StoryGraph()
        
        # 추적 요소들
        self.tracked_elements = {
            'characters': {},      # 캐릭터별 상태 추적
            'plot_points': [],     # 주요 플롯 포인트
            'world_rules': {},     # 세계관 규칙
            'power_levels': {},    # 파워 레벨 추적
            'relationships': {},   # 캐릭터 간 관계
            'timeline': [],        # 시간선
            'locations': {},       # 장소 정보
            'items': {},          # 아이템/물건
            'foreshadowing': [],  # 복선
            'mysteries': {}       # 미해결 미스터리
        }
        
        self.correlation_thresholds = {
            'minimum': 0.6,    # 최소 연관성
            'good': 0.75,      # 양호
            'excellent': 0.9   # 우수
        }
        
        self.restore_memory()
        
    async def execute(self, task: Dict[str, Any]) -> Any:
        """작업 실행"""
        task_type = task.get('type')
        
        if task_type == 'analyze_correlation':
            return await self.analyze_episode_correlation(task)
        elif task_type == 'check_consistency':
            return await self.check_consistency(task)
        elif task_type == 'track_development':
            return await self.track_character_development(task)
        elif task_type == 'find_plot_holes':
            return await self.find_plot_holes(task)
        else:
            return {"error": f"Unknown task type: {task_type}"}
    
    async def analyze_episode_correlation(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """에피소드 간 연관성 분석"""
        
        current_episode = task.get('current_episode')
        episode_number = task.get('episode_number')
        previous_episodes = task.get('previous_episodes', [])
        
        logger.info(f"에피소드 {episode_number} 연관성 분석 시작")
        
        # 1. 요소 추출
        current_elements = await self.extract_story_elements(current_episode)
        
        # 2. 이전 에피소드들과 비교
        correlations = []
        issues = []
        
        for prev_ep in previous_episodes[-5:]:  # 최근 5개 에피소드
            prev_elements = await self.extract_story_elements(prev_ep['content'])
            correlation = self.calculate_correlation(current_elements, prev_elements)
            correlations.append(correlation)
            
            # 불일치 찾기
            inconsistencies = self.find_inconsistencies(current_elements, prev_elements)
            if inconsistencies:
                issues.extend(inconsistencies)
        
        # 3. 캐릭터 성장 궤적 분석
        character_arc = await self.analyze_character_arc(
            current_elements['characters'],
            episode_number
        )
        
        # 4. 플롯 연속성 체크
        plot_continuity = await self.check_plot_continuity(
            current_elements['plot_points'],
            self.tracked_elements['plot_points']
        )
        
        # 5. 복선 추적
        foreshadowing_status = self.track_foreshadowing(
            current_elements,
            episode_number
        )
        
        # 6. 점수 계산
        overall_score = self.calculate_correlation_score(
            correlations,
            character_arc,
            plot_continuity,
            foreshadowing_status
        )
        
        # 7. 스토리 그래프 업데이트
        self.update_story_graph(episode_number, current_elements, overall_score)
        
        result = {
            'episode_number': episode_number,
            'correlation_score': overall_score,
            'character_arc_consistency': character_arc['consistency_score'],
            'plot_continuity_score': plot_continuity['score'],
            'foreshadowing_tracking': foreshadowing_status,
            'issues_found': issues,
            'recommendations': self.generate_recommendations(issues, overall_score),
            'story_graph_density': self.story_graph.analyze_connectivity()['density']
        }
        
        logger.info(f"연관성 분석 완료. 점수: {overall_score:.1f}/10")
        
        return result
    
    async def extract_story_elements(self, episode_content: str) -> Dict[str, Any]:
        """에피소드에서 주요 스토리 요소 추출"""
        
        prompt = f"""
        다음 웹소설 에피소드에서 주요 요소를 추출해주세요:
        
        {episode_content[:2000]}
        
        추출할 요소:
        1. 등장 캐릭터와 상태
        2. 주요 사건/플롯 포인트
        3. 장소
        4. 시간대
        5. 파워 레벨 변화
        6. 새로운 아이템/능력
        7. 캐릭터 간 관계 변화
        8. 복선이나 떡밥
        
        JSON 형식으로 응답하세요.
        """
        
        response = await self.call_claude(prompt, max_tokens=1500)
        
        try:
            elements = json.loads(response)
        except:
            # 파싱 실패시 기본 구조
            elements = {
                'characters': [],
                'plot_points': [],
                'locations': [],
                'timeline': '',
                'power_changes': {},
                'items': [],
                'relationships': {},
                'foreshadowing': []
            }
        
        return elements
    
    def calculate_correlation(self, current: Dict, previous: Dict) -> float:
        """두 에피소드 간 연관성 계산"""
        
        score = 0.0
        weights = {
            'characters': 0.3,
            'locations': 0.2,
            'plot_points': 0.3,
            'timeline': 0.2
        }
        
        # 캐릭터 연속성
        if current.get('characters') and previous.get('characters'):
            char_overlap = len(set(current['characters']) & set(previous['characters']))
            char_total = len(set(current['characters']) | set(previous['characters']))
            if char_total > 0:
                score += weights['characters'] * (char_overlap / char_total)
        
        # 장소 연속성
        if current.get('locations') and previous.get('locations'):
            loc_overlap = len(set(current['locations']) & set(previous['locations']))
            loc_total = len(set(current['locations']) | set(previous['locations']))
            if loc_total > 0:
                score += weights['locations'] * (loc_overlap / loc_total)
        
        # 플롯 연결성
        plot_connection = self.check_plot_connection(
            current.get('plot_points', []),
            previous.get('plot_points', [])
        )
        score += weights['plot_points'] * plot_connection
        
        # 시간선 연속성
        timeline_continuity = self.check_timeline_continuity(
            current.get('timeline'),
            previous.get('timeline')
        )
        score += weights['timeline'] * timeline_continuity
        
        return min(score * 10, 10.0)  # 0-10 점수로 변환
    
    def find_inconsistencies(self, current: Dict, previous: Dict) -> List[Dict]:
        """불일치 요소 찾기"""
        
        issues = []
        
        # 파워 레벨 급변
        if 'power_changes' in current and 'power_changes' in previous:
            for char, level in current['power_changes'].items():
                if char in previous.get('power_changes', {}):
                    prev_level = previous['power_changes'][char]
                    if isinstance(level, (int, float)) and isinstance(prev_level, (int, float)):
                        if level > prev_level * 2:  # 2배 이상 증가
                            issues.append({
                                'type': 'power_spike',
                                'character': char,
                                'previous': prev_level,
                                'current': level,
                                'severity': 'high'
                            })
        
        # 캐릭터 위치 모순
        for char in current.get('characters', []):
            if char in previous.get('characters', []):
                curr_loc = self.get_character_location(char, current)
                prev_loc = self.get_character_location(char, previous)
                
                if curr_loc and prev_loc and not self.is_travel_possible(prev_loc, curr_loc):
                    issues.append({
                        'type': 'location_inconsistency',
                        'character': char,
                        'previous_location': prev_loc,
                        'current_location': curr_loc,
                        'severity': 'medium'
                    })
        
        return issues
    
    async def analyze_character_arc(self, characters: List, episode_num: int) -> Dict:
        """캐릭터 성장 궤적 분석"""
        
        arc_analysis = {
            'consistency_score': 0,
            'development_rate': {},
            'stagnant_characters': [],
            'overdeveloped_characters': []
        }
        
        for character in characters:
            if character not in self.story_graph.character_arcs:
                self.story_graph.character_arcs[character] = []
            
            # 성장 추적
            self.story_graph.character_arcs[character].append({
                'episode': episode_num,
                'state': 'active'  # 실제로는 더 상세한 상태
            })
            
            # 성장률 계산
            if len(self.story_graph.character_arcs[character]) > 3:
                development = self.calculate_development_rate(
                    self.story_graph.character_arcs[character]
                )
                arc_analysis['development_rate'][character] = development
                
                if development < 0.1:
                    arc_analysis['stagnant_characters'].append(character)
                elif development > 0.8:
                    arc_analysis['overdeveloped_characters'].append(character)
        
        # 일관성 점수 계산
        if arc_analysis['development_rate']:
            avg_development = sum(arc_analysis['development_rate'].values()) / len(arc_analysis['development_rate'])
            arc_analysis['consistency_score'] = min(avg_development * 10, 10)
        
        return arc_analysis
    
    async def check_plot_continuity(self, current_plots: List, tracked_plots: List) -> Dict:
        """플롯 연속성 체크"""
        
        continuity = {
            'score': 0,
            'resolved_plots': [],
            'new_plots': [],
            'ongoing_plots': [],
            'abandoned_plots': []
        }
        
        current_set = set(current_plots) if current_plots else set()
        tracked_set = set(tuple(p) if isinstance(p, list) else p for p in tracked_plots)
        
        # 새로운 플롯
        continuity['new_plots'] = list(current_set - tracked_set)
        
        # 진행 중인 플롯
        continuity['ongoing_plots'] = list(current_set & tracked_set)
        
        # 방치된 플롯 (3화 이상 언급 없음)
        for plot in tracked_plots:
            if plot not in current_plots:
                # 실제로는 더 정교한 추적 필요
                continuity['abandoned_plots'].append(plot)
        
        # 점수 계산
        if tracked_plots:
            continuity_ratio = len(continuity['ongoing_plots']) / len(tracked_plots)
            continuity['score'] = min(continuity_ratio * 10, 10)
        else:
            continuity['score'] = 10  # 첫 에피소드
        
        # 추적 플롯 업데이트
        self.tracked_elements['plot_points'].extend(continuity['new_plots'])
        
        return continuity
    
    def track_foreshadowing(self, elements: Dict, episode_num: int) -> Dict:
        """복선 추적"""
        
        foreshadowing = {
            'new_hints': [],
            'resolved': [],
            'pending': [],
            'abandoned': []
        }
        
        # 새로운 복선
        if 'foreshadowing' in elements:
            for hint in elements['foreshadowing']:
                self.tracked_elements['foreshadowing'].append({
                    'hint': hint,
                    'episode': episode_num,
                    'resolved': False
                })
                foreshadowing['new_hints'].append(hint)
        
        # 해결된 복선 체크
        for tracked in self.tracked_elements['foreshadowing']:
            if not tracked['resolved']:
                # 실제로는 더 정교한 해결 감지 필요
                if episode_num - tracked['episode'] > 10:
                    foreshadowing['abandoned'].append(tracked['hint'])
                else:
                    foreshadowing['pending'].append(tracked['hint'])
        
        return foreshadowing
    
    def calculate_correlation_score(self, correlations: List, character_arc: Dict, 
                                   plot_continuity: Dict, foreshadowing: Dict) -> float:
        """전체 연관성 점수 계산"""
        
        weights = {
            'correlation': 0.3,
            'character': 0.25,
            'plot': 0.25,
            'foreshadowing': 0.2
        }
        
        # 에피소드 간 연관성
        corr_score = sum(correlations) / len(correlations) if correlations else 0
        
        # 캐릭터 아크
        char_score = character_arc['consistency_score']
        
        # 플롯 연속성
        plot_score = plot_continuity['score']
        
        # 복선 관리
        if foreshadowing['pending']:
            foreshadow_score = 7  # 진행 중
        elif foreshadowing['abandoned']:
            foreshadow_score = 3  # 방치됨
        else:
            foreshadow_score = 10  # 잘 관리됨
        
        total = (
            weights['correlation'] * corr_score +
            weights['character'] * char_score +
            weights['plot'] * plot_score +
            weights['foreshadowing'] * foreshadow_score
        )
        
        return min(total, 10.0)
    
    def update_story_graph(self, episode_num: int, elements: Dict, score: float):
        """스토리 그래프 업데이트"""
        
        # 에피소드 노드 추가
        self.story_graph.add_episode_node(episode_num, {
            'score': score,
            'characters': elements.get('characters', []),
            'locations': elements.get('locations', []),
            'timestamp': datetime.now().isoformat()
        })
        
        # 이전 에피소드와 연결
        if episode_num > 1:
            self.story_graph.add_connection(
                episode_num - 1,
                episode_num,
                'sequential',
                score / 10
            )
        
        # 메모리 저장
        self.save_memory('story_graph', {
            'nodes': list(self.story_graph.graph.nodes(data=True)),
            'edges': list(self.story_graph.graph.edges(data=True))
        })
    
    def generate_recommendations(self, issues: List[Dict], score: float) -> List[str]:
        """개선 권장사항 생성"""
        
        recommendations = []
        
        if score < self.correlation_thresholds['minimum']:
            recommendations.append("전체적인 스토리 연결성 강화 필요")
        
        for issue in issues:
            if issue['type'] == 'power_spike':
                recommendations.append(
                    f"{issue['character']}의 파워 상승 과정 추가 설명 필요"
                )
            elif issue['type'] == 'location_inconsistency':
                recommendations.append(
                    f"{issue['character']}의 이동 경로 설명 추가 필요"
                )
        
        if len(self.tracked_elements['foreshadowing']) > 10:
            recommendations.append("미해결 복선 정리 필요")
        
        return recommendations
    
    # 유틸리티 메서드들
    def get_character_location(self, character: str, elements: Dict) -> Optional[str]:
        """캐릭터 위치 추출"""
        # 실제 구현 필요
        return elements.get('locations', [None])[0] if elements.get('locations') else None
    
    def is_travel_possible(self, from_loc: str, to_loc: str) -> bool:
        """이동 가능 여부 판단"""
        # 실제 구현 필요 - 거리/시간 계산
        return True  # 임시
    
    def calculate_development_rate(self, character_arc: List) -> float:
        """캐릭터 성장률 계산"""
        if len(character_arc) < 2:
            return 0.5
        
        # 실제로는 더 정교한 계산 필요
        changes = len([1 for i in range(1, len(character_arc)) 
                      if character_arc[i] != character_arc[i-1]])
        
        return min(changes / len(character_arc), 1.0)
    
    def check_plot_connection(self, current_plots: List, previous_plots: List) -> float:
        """플롯 연결성 체크"""
        if not current_plots or not previous_plots:
            return 0.5
        
        # 실제로는 더 정교한 연결성 분석 필요
        connections = 0
        for curr in current_plots:
            for prev in previous_plots:
                if self.are_plots_related(curr, prev):
                    connections += 1
        
        max_connections = min(len(current_plots), len(previous_plots))
        return connections / max_connections if max_connections > 0 else 0
    
    def are_plots_related(self, plot1: Any, plot2: Any) -> bool:
        """두 플롯의 관련성 판단"""
        # 실제 구현 필요
        return False  # 임시
    
    def check_timeline_continuity(self, current_time: Any, previous_time: Any) -> float:
        """시간선 연속성 체크"""
        # 실제 구현 필요
        return 0.8  # 임시