"""
메인 에이전트 (Main Coordinator Agent)
리뷰 문서를 읽고 알맞은 에이전트에게 작업을 할당하는 중앙 조율 에이전트
"""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, List
from pathlib import Path

from .base_agent import BaseAgent
from .project_loader import project_loader

logger = logging.getLogger(__name__)


class MainCoordinatorAgent(BaseAgent):
    """메인 조율 에이전트"""
    
    def __init__(self):
        super().__init__("MainCoordinator")
        self.agents = {}  # 다른 에이전트들 참조
        self.shared_memory = {}  # 에이전트간 공유 메모리
        self.current_tasks = {}  # 현재 실행 중인 작업들
        
    async def initialize(self):
        """메인 에이전트 초기화"""
        logger.info("메인 조율 에이전트 초기화 시작")
        
        # 프로젝트 로더 초기화
        await project_loader.initialize_project()
        
        # 다른 에이전트들 초기화
        await self.initialize_sub_agents()
        
        logger.info("메인 조율 에이전트 초기화 완료")
    
    async def initialize_sub_agents(self):
        """하위 에이전트들 초기화"""
        try:
            # 동적 import로 각 에이전트 로드
            from .writer_agent import WriterAgent
            from .grammar_agent import GrammarAgent
            from .world_setting_agent import WorldSettingAgent
            from .history_agent import HistoryAgent
            from .correlation_agent import CorrelationAgent
            from .reader_agent import ReaderAgent
            from .setting_improvement_agent import SettingImprovementAgent
            from .episode_reviewer import EpisodeReviewerAgent
            from .episode_improver import EpisodeImproverAgent
            
            # 에이전트 인스턴스 생성
            self.agents = {
                'writer': WriterAgent(),
                'grammar': GrammarAgent(),
                'world_setting': WorldSettingAgent(),
                'history': HistoryAgent(),
                'correlation': CorrelationAgent(),
                'reader': ReaderAgent(),
                'setting_improvement': SettingImprovementAgent(),
                'quality_reviewer': EpisodeReviewerAgent(),
                'episode_improver': EpisodeImproverAgent()
            }
            
            # 각 에이전트 초기화
            for name, agent in self.agents.items():
                try:
                    if hasattr(agent, 'initialize'):
                        await agent.initialize()
                    logger.info(f"{name} 에이전트 초기화 완료")
                except Exception as e:
                    logger.error(f"{name} 에이전트 초기화 실패: {e}")
                    # 기본 에이전트로 대체
                    self.agents[name] = BaseAgent(name)
            
        except ImportError as e:
            logger.warning(f"일부 에이전트를 불러올 수 없습니다: {e}")
            # 기본 에이전트들로 대체
            self.agents = {name: BaseAgent(name) for name in [
                'writer', 'grammar', 'world_setting', 'history', 
                'correlation', 'reader', 'setting_improvement',
                'quality_reviewer', 'episode_improver'
            ]}
    
    async def execute(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """작업 실행"""
        task_type = task.get('type')
        
        if task_type == 'improve_episode':
            return await self.coordinate_episode_improvement(task)
        elif task_type == 'analyze_episode':
            return await self.coordinate_episode_analysis(task)
        elif task_type == 'full_review_cycle':
            return await self.coordinate_full_review_cycle(task)
        else:
            return {"error": f"Unknown task type: {task_type}"}
    
    async def coordinate_episode_improvement(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """에피소드 개선 작업 조율 (35분 완전 사이클)"""
        episode_num = task.get('episode_number')
        target_score = task.get('target_score', 9.5)
        
        if not episode_num:
            return {"error": "에피소드 번호가 필요합니다"}
        
        cycle_start = datetime.now()
        logger.info(f"🎯 에피소드 {episode_num}화 개선 사이클 시작")
        
        try:
            # Phase 1: 초기 분석 (2분)
            logger.info("📊 Phase 1: 초기 상태 분석")
            current_status = await self.analyze_episode_status(episode_num)
            priority_areas = self.determine_priority_areas(current_status)
            
            # Phase 2: 병렬 검토 (15분) 
            logger.info("🔄 Phase 2: 전문 에이전트 병렬 검토")
            parallel_results = await self.execute_parallel_analysis(episode_num, priority_areas)
            
            # Phase 3: 통합 분석 (5분)
            logger.info("🔍 Phase 3: 통합 분석 및 평가")
            integrated_results = await self.integrate_analysis_results(parallel_results)
            
            # Phase 4: 실제 개선 (10분)
            logger.info("✏️ Phase 4: 실제 개선 작업")
            improvement_results = await self.execute_improvements(episode_num, integrated_results)
            
            # Phase 5: 결과 저장 (3분)
            logger.info("💾 Phase 5: 결과 저장")
            await self.save_cycle_results(episode_num, {
                'initial_status': current_status,
                'parallel_results': parallel_results,
                'integrated_results': integrated_results,
                'improvements': improvement_results
            })
            
            cycle_end = datetime.now()
            cycle_duration = (cycle_end - cycle_start).total_seconds() / 60  # 분 단위
            
            logger.info(f"✅ 에피소드 {episode_num}화 개선 사이클 완료 ({cycle_duration:.1f}분)")
            
            return {
                'episode_number': episode_num,
                'cycle_duration_minutes': cycle_duration,
                'improvements_made': improvement_results.get('improvements_made', []),
                'final_score': integrated_results.get('overall_score', 0),
                'status': 'success'
            }
            
        except Exception as e:
            logger.error(f"에피소드 {episode_num}화 개선 사이클 오류: {e}")
            return {
                'episode_number': episode_num,
                'status': 'error',
                'error': str(e)
            }
    
    async def analyze_episode_status(self, episode_num: int) -> Dict[str, Any]:
        """에피소드 현재 상태 분석"""
        
        # 에피소드 내용 로드
        episode_content = project_loader.get_episode_content(episode_num)
        if not episode_content:
            return {'error': f'에피소드 {episode_num}화를 찾을 수 없습니다'}
        
        # 기본 상태 정보 수집
        status = {
            'episode_number': episode_num,
            'content_length': len(episode_content),
            'paragraph_count': len(episode_content.split('\n\n')),
            'word_count': len(episode_content.split()),
            'last_modified': datetime.now().isoformat(),
            'content_preview': episode_content[:500] + '...' if len(episode_content) > 500 else episode_content
        }
        
        logger.info(f"에피소드 {episode_num}화 상태: {status['word_count']}자, {status['paragraph_count']}문단")
        
        return status
    
    def determine_priority_areas(self, current_status: Dict[str, Any]) -> List[str]:
        """우선순위 영역 결정"""
        priority_areas = []
        
        # 내용 길이 기반 우선순위
        word_count = current_status.get('word_count', 0)
        if word_count < 1000:
            priority_areas.append('content_expansion')
        elif word_count > 5000:
            priority_areas.append('content_optimization')
        
        # 문단 구조 기반 우선순위  
        paragraph_count = current_status.get('paragraph_count', 0)
        if paragraph_count < 5:
            priority_areas.append('structure_improvement')
        
        # 기본 우선순위 영역들
        priority_areas.extend(['world_consistency', 'character_development', 'plot_flow'])
        
        return priority_areas
    
    async def execute_parallel_analysis(self, episode_num: int, priority_areas: List[str]) -> Dict[str, Any]:
        """병렬 분석 실행"""
        
        # 각 에이전트별 작업 생성
        tasks = []
        
        # 1. 작가 에이전트
        tasks.append(self.run_agent_task('writer', {
            'type': 'analyze_story',
            'episode_number': episode_num,
            'priority_areas': priority_areas
        }))
        
        # 2. 문법 에이전트
        tasks.append(self.run_agent_task('grammar', {
            'type': 'check_grammar',
            'episode_number': episode_num
        }))
        
        # 3. 세계관 에이전트
        tasks.append(self.run_agent_task('world_setting', {
            'type': 'verify_world_consistency',
            'episode_number': episode_num
        }))
        
        # 4. 역사 에이전트
        tasks.append(self.run_agent_task('history', {
            'type': 'validate_timeline',
            'episode_number': episode_num
        }))
        
        # 5. 연관성 에이전트
        tasks.append(self.run_agent_task('correlation', {
            'type': 'analyze_episode_correlation',
            'episode_number': episode_num
        }))
        
        # 6. 독자 에이전트 (10개 페르소나)
        for persona_id in range(1, 11):
            tasks.append(self.run_agent_task('reader', {
                'type': 'evaluate_from_reader_perspective',
                'episode_number': episode_num,
                'persona_id': persona_id
            }))
        
        # 7. 설정 개선 에이전트
        tasks.append(self.run_agent_task('setting_improvement', {
            'type': 'scan_for_improvements',
            'episode_number': episode_num
        }))
        
        # 병렬 실행
        logger.info(f"🚀 {len(tasks)}개 작업 병렬 실행 중...")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 결과 정리
        parallel_results = {
            'writer': results[0] if not isinstance(results[0], Exception) else {'error': str(results[0])},
            'grammar': results[1] if not isinstance(results[1], Exception) else {'error': str(results[1])},
            'world_setting': results[2] if not isinstance(results[2], Exception) else {'error': str(results[2])},
            'history': results[3] if not isinstance(results[3], Exception) else {'error': str(results[3])},
            'correlation': results[4] if not isinstance(results[4], Exception) else {'error': str(results[4])},
            'readers': [results[5+i] if not isinstance(results[5+i], Exception) else {'error': str(results[5+i])} 
                       for i in range(10)],
            'setting_improvement': results[15] if not isinstance(results[15], Exception) else {'error': str(results[15])}
        }
        
        logger.info("✅ 병렬 분석 완료")
        
        return parallel_results
    
    async def run_agent_task(self, agent_name: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """개별 에이전트 작업 실행"""
        try:
            agent = self.agents.get(agent_name)
            if not agent:
                return {'error': f'에이전트 {agent_name}을 찾을 수 없습니다'}
            
            # 작업 실행
            if hasattr(agent, 'execute'):
                result = await agent.execute(task)
            else:
                # 기본 에이전트인 경우 시뮬레이션
                result = await self.simulate_agent_work(agent_name, task)
            
            return result
            
        except Exception as e:
            logger.error(f"{agent_name} 에이전트 작업 실패: {e}")
            return {'error': str(e)}
    
    async def simulate_agent_work(self, agent_name: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """에이전트 작업 시뮬레이션 (개발/테스트용)"""
        await asyncio.sleep(1)  # 작업 시간 시뮬레이션
        
        episode_num = task.get('episode_number', 0)
        
        # 에이전트별 시뮬레이션 결과
        simulations = {
            'writer': {
                'story_score': 7.5,
                'plot_issues': ['캐릭터 동기 부족', '전개 속도 개선 필요'],
                'suggestions': ['주인공 내적 갈등 추가', '액션 장면 강화']
            },
            'grammar': {
                'grammar_score': 8.2,
                'errors_found': 3,
                'error_types': ['맞춤법 오류', '문장 구조'],
                'corrections': ['오타 수정', '문장 다듬기']
            },
            'world_setting': {
                'consistency_score': 7.8,
                'issues': ['공명력 설명 불일치'],
                'improvements': ['설정 문서와 일치하도록 수정']
            },
            'history': {
                'timeline_score': 8.0,
                'continuity_issues': ['시간 흐름 애매'],
                'suggestions': ['시간 표현 명확화']
            },
            'correlation': {
                'correlation_score': 7.3,
                'connection_issues': ['이전 화와 연결성 부족'],
                'improvements': ['연결 문구 추가']
            },
            'reader': {
                'reader_score': 7.6,
                'engagement_level': 'medium',
                'feedback': '흥미롭지만 몰입도 개선 필요'
            },
            'setting_improvement': {
                'improvement_potential': 'medium',
                'new_elements_detected': False,
                'suggestions': []
            }
        }
        
        return simulations.get(agent_name, {'status': 'simulation', 'score': 7.5})
    
    async def integrate_analysis_results(self, parallel_results: Dict[str, Any]) -> Dict[str, Any]:
        """분석 결과 통합"""
        
        # 각 영역별 점수 수집
        scores = {}
        issues = []
        suggestions = []
        
        # 작가 에이전트 결과
        if 'writer' in parallel_results and 'story_score' in parallel_results['writer']:
            scores['story'] = parallel_results['writer']['story_score']
            issues.extend(parallel_results['writer'].get('plot_issues', []))
            suggestions.extend(parallel_results['writer'].get('suggestions', []))
        
        # 문법 에이전트 결과
        if 'grammar' in parallel_results and 'grammar_score' in parallel_results['grammar']:
            scores['grammar'] = parallel_results['grammar']['grammar_score']
            issues.extend(parallel_results['grammar'].get('error_types', []))
        
        # 세계관 에이전트 결과
        if 'world_setting' in parallel_results and 'consistency_score' in parallel_results['world_setting']:
            scores['world_consistency'] = parallel_results['world_setting']['consistency_score']
            issues.extend(parallel_results['world_setting'].get('issues', []))
        
        # 역사 에이전트 결과
        if 'history' in parallel_results and 'timeline_score' in parallel_results['history']:
            scores['timeline'] = parallel_results['history']['timeline_score']
            issues.extend(parallel_results['history'].get('continuity_issues', []))
        
        # 연관성 에이전트 결과
        if 'correlation' in parallel_results and 'correlation_score' in parallel_results['correlation']:
            scores['correlation'] = parallel_results['correlation']['correlation_score']
            issues.extend(parallel_results['correlation'].get('connection_issues', []))
        
        # 독자 에이전트 결과 (10개 평균)
        reader_scores = []
        if 'readers' in parallel_results:
            for reader_result in parallel_results['readers']:
                if 'reader_score' in reader_result:
                    reader_scores.append(reader_result['reader_score'])
        
        if reader_scores:
            scores['reader_average'] = sum(reader_scores) / len(reader_scores)
        
        # 전체 점수 계산
        if scores:
            overall_score = sum(scores.values()) / len(scores)
        else:
            overall_score = 7.0  # 기본 점수
        
        # 우선순위 개선 영역 결정
        priority_fixes = []
        for area, score in scores.items():
            if score < 8.0:
                priority_fixes.append({
                    'area': area,
                    'score': score,
                    'priority': 'high' if score < 7.0 else 'medium'
                })
        
        integrated_result = {
            'overall_score': overall_score,
            'detailed_scores': scores,
            'priority_fixes': priority_fixes,
            'total_issues': len(issues),
            'issues_summary': issues[:5],  # 상위 5개만
            'improvement_suggestions': suggestions[:10],  # 상위 10개만
            'reader_feedback_count': len(reader_scores),
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"📊 통합 분석 완료 - 전체 점수: {overall_score:.1f}/10, 개선 필요 영역: {len(priority_fixes)}개")
        
        return integrated_result
    
    async def execute_improvements(self, episode_num: int, integrated_results: Dict[str, Any]) -> Dict[str, Any]:
        """실제 개선 작업 실행"""
        
        # 에피소드 개선 에이전트에 작업 위임
        improvement_task = {
            'type': 'improve_episode',
            'episode_number': episode_num,
            'target_areas': integrated_results.get('priority_fixes', []),
            'target_score': 9.0,
            'analysis_results': integrated_results
        }
        
        improvement_result = await self.run_agent_task('episode_improver', improvement_task)
        
        return improvement_result
    
    async def save_cycle_results(self, episode_num: int, cycle_data: Dict[str, Any]):
        """사이클 결과 저장"""
        
        # 결과 디렉토리 생성
        results_dir = Path("memory/agent_cycles")
        results_dir.mkdir(parents=True, exist_ok=True)
        
        # 결과 파일 저장
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        result_file = results_dir / f"episode_{episode_num}_cycle_{timestamp}.json"
        
        import json
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump(cycle_data, f, ensure_ascii=False, indent=2)
        
        logger.debug(f"사이클 결과 저장: {result_file}")
    
    async def coordinate_full_review_cycle(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """전체 에피소드 검토 사이클 (1-3화 순차)"""
        target_episodes = task.get('target_episodes', [1, 2, 3])
        target_score = task.get('target_score', 9.5)
        
        logger.info(f"🔄 전체 검토 사이클 시작: {target_episodes}")
        
        cycle_results = []
        
        for episode_num in target_episodes:
            episode_task = {
                'type': 'improve_episode',
                'episode_number': episode_num,
                'target_score': target_score
            }
            
            result = await self.coordinate_episode_improvement(episode_task)
            cycle_results.append(result)
            
            # 에피소드간 1분 대기
            await asyncio.sleep(60)
        
        return {
            'cycle_results': cycle_results,
            'total_episodes': len(target_episodes),
            'average_score': sum(r.get('final_score', 0) for r in cycle_results) / len(cycle_results),
            'total_improvements': sum(len(r.get('improvements_made', [])) for r in cycle_results),
            'status': 'completed'
        }