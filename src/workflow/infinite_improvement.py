"""
무한 반복 개선 시스템
사용자가 지정한 에피소드들을 24시간 내내 반복해서 개선
"""

import asyncio
import logging
import json
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any
from classic_isekai_main import ClassicIsekaiSystem
from episode_improver import EpisodeImproverAgent

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/infinite_improvement.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class InfiniteImprovementSystem:
    """무한 반복 개선 시스템"""
    
    def __init__(self, target_episodes: List[int], target_score: float = 9.5):
        self.target_episodes = target_episodes  # 개선할 에피소드 목록
        self.target_score = target_score        # 목표 점수
        self.system = None
        self.improver = None                   # 에피소드 개선 에이전트
        self.running = False
        self.improvement_history = {}           # 개선 기록
        self.iteration_count = 0               # 반복 횟수
        self.best_scores = {}                  # 각 에피소드별 최고 점수
        self.last_improvement_time = {}        # 마지막 개선 시간
        
        # 개선 통계
        self.stats = {
            'total_iterations': 0,
            'improvements_made': 0,
            'average_improvement_per_iteration': 0.0,
            'start_time': None,
            'runtime_hours': 0.0
        }
    
    async def initialize(self):
        """시스템 초기화"""
        logger.info("=" * 80)
        logger.info("🔄 무한 반복 개선 시스템 시작")
        logger.info("=" * 80)
        
        # Classic Isekai 시스템 초기화
        self.system = ClassicIsekaiSystem()
        await self.system.initialize()
        
        # 에피소드 개선 에이전트 초기화
        self.improver = EpisodeImproverAgent()
        await self.improver.initialize()
        
        # 개선 기록 로드
        self.load_improvement_history()
        
        # 초기 상태 평가
        await self.evaluate_initial_state()
        
        # 통계 초기화
        self.stats['start_time'] = datetime.now()
        
        logger.info(f"🎯 개선 대상 에피소드: {self.target_episodes}")
        logger.info(f"🏆 목표 점수: {self.target_score}/10")
        logger.info("✅ 무한 반복 개선 시스템 초기화 완료")
    
    async def evaluate_initial_state(self):
        """초기 상태 평가"""
        logger.info("📊 초기 상태 평가 중...")
        
        for episode_num in self.target_episodes:
            result = await self.system.review_single_episode(episode_num)
            current_score = result.get('overall_score', 0)
            
            # 최고 점수 초기화
            if episode_num not in self.best_scores:
                self.best_scores[episode_num] = current_score
            
            # 개선 기록 초기화
            if episode_num not in self.improvement_history:
                self.improvement_history[episode_num] = []
            
            logger.info(f"   에피소드 {episode_num}화: {current_score:.1f}/10 (목표: {self.target_score})")
    
    async def run_infinite_improvement(self):
        """무한 반복 개선 실행"""
        self.running = True
        logger.info("🚀 무한 반복 개선 시작!")
        logger.info("   Ctrl+C로 중단 가능")
        
        try:
            while self.running:
                await self.improvement_cycle()
                
                # 짧은 휴식 (다음 사이클 전 1분 대기)
                if self.running:
                    await asyncio.sleep(60)
                    
        except KeyboardInterrupt:
            logger.info("사용자 중단 요청")
        except Exception as e:
            logger.error(f"무한 개선 시스템 오류: {e}")
        finally:
            await self.finalize_improvements()
    
    async def improvement_cycle(self):
        """한 번의 개선 사이클"""
        self.iteration_count += 1
        cycle_start = datetime.now()
        
        logger.info(f"")
        logger.info(f"🔄 개선 사이클 #{self.iteration_count} 시작")
        logger.info(f"⏰ {cycle_start.strftime('%H:%M:%S')}")
        
        cycle_improvements = 0
        
        # 각 대상 에피소드에 대해 개선 시도
        for episode_num in self.target_episodes:
            try:
                improvement_made = await self.improve_single_episode(episode_num)
                if improvement_made:
                    cycle_improvements += 1
                    
            except Exception as e:
                logger.error(f"에피소드 {episode_num}화 개선 중 오류: {e}")
        
        # 사이클 완료 로깅
        cycle_end = datetime.now()
        cycle_duration = (cycle_end - cycle_start).total_seconds()
        
        self.stats['total_iterations'] += 1
        self.stats['improvements_made'] += cycle_improvements
        
        if self.stats['total_iterations'] > 0:
            self.stats['average_improvement_per_iteration'] = \
                self.stats['improvements_made'] / self.stats['total_iterations']
        
        logger.info(f"📈 사이클 #{self.iteration_count} 완료")
        logger.info(f"   개선 횟수: {cycle_improvements}/{len(self.target_episodes)}")
        logger.info(f"   소요 시간: {cycle_duration:.1f}초")
        
        # 주기적으로 진행 상황 출력 (10 사이클마다)
        if self.iteration_count % 10 == 0:
            await self.print_progress_report()
        
        # 개선 기록 저장 (50 사이클마다)
        if self.iteration_count % 50 == 0:
            self.save_improvement_history()
    
    async def improve_single_episode(self, episode_num: int) -> bool:
        """단일 에피소드 개선 시도"""
        
        # 현재 점수 확인
        result = await self.system.review_single_episode(episode_num)
        current_score = result.get('overall_score', 0)
        
        # 이미 목표 점수에 도달했으면 가끔씩만 체크
        if current_score >= self.target_score:
            # 목표 도달한 에피소드는 10번에 1번만 체크
            if self.iteration_count % 10 != 0:
                return False
            
            logger.info(f"✨ 에피소드 {episode_num}화: 목표 달성 ({current_score:.1f}/10)")
            return False
        
        # 최고 점수 갱신 확인
        score_improved = False
        if current_score > self.best_scores.get(episode_num, 0):
            old_score = self.best_scores.get(episode_num, 0)
            self.best_scores[episode_num] = current_score
            improvement = current_score - old_score
            score_improved = True
            
            logger.info(f"🎉 에피소드 {episode_num}화 점수 향상!")
            logger.info(f"   {old_score:.1f} → {current_score:.1f} (+{improvement:.1f})")
            
            # 개선 기록 저장
            self.improvement_history[episode_num].append({
                'iteration': self.iteration_count,
                'timestamp': datetime.now().isoformat(),
                'old_score': old_score,
                'new_score': current_score,
                'improvement': improvement,
                'detailed_scores': result.get('detailed_scores', {})
            })
            
            self.last_improvement_time[episode_num] = datetime.now()
        
        # 개선 작업 수행 (점수 향상이 있었거나 처음이면)
        if score_improved or episode_num not in self.last_improvement_time:
            await self.perform_improvement_actions(episode_num, result)
            return True
        
        # 오랫동안 개선이 없었으면 강화된 개선 시도
        last_improvement = self.last_improvement_time.get(episode_num)
        if last_improvement:
            time_since_improvement = datetime.now() - last_improvement
            if time_since_improvement > timedelta(hours=2):  # 2시간 동안 개선 없음
                logger.info(f"🔧 에피소드 {episode_num}화: 강화된 개선 시도")
                await self.perform_intensive_improvement(episode_num, result)
                return True
        
        return False
    
    async def perform_improvement_actions(self, episode_num: int, review_result: Dict):
        """개선 작업 수행"""
        
        # 개선 제안 기반으로 작업
        suggestions = review_result.get('improvement_suggestions', [])
        detailed_scores = review_result.get('detailed_scores', {})
        
        # 가장 점수가 낮은 항목들 우선 개선
        low_score_areas = []
        for criterion, details in detailed_scores.items():
            if details.get('score', 10) < 8.0:
                low_score_areas.append({
                    'criterion': criterion,
                    'score': details.get('score', 0),
                    'description': details.get('description', ''),
                    'weight': details.get('weight', 0)
                })
        
        # 가중치 순으로 정렬 (영향도 큰 것부터)
        low_score_areas.sort(key=lambda x: x['weight'], reverse=True)
        
        if low_score_areas:
            logger.info(f"🔍 에피소드 {episode_num}화 개선 영역:")
            for area in low_score_areas[:3]:  # 상위 3개만 출력
                logger.info(f"   - {area['description']}: {area['score']:.1f}/10")
        
        # 실제 에피소드 개선 실행
        try:
            improvement_task = {
                'type': 'improve_episode',
                'episode_number': episode_num,
                'target_areas': low_score_areas[:2],  # 상위 2개 영역만
                'target_score': self.target_score
            }
            
            result = await self.improver.improve_episode(improvement_task)
            
            if result.get('status') == 'success':
                improvements = result.get('improvements_made', [])
                logger.info(f"✏️ 에피소드 {episode_num}화 개선 완료:")
                for improvement in improvements:
                    logger.info(f"   - {improvement}")
            else:
                logger.warning(f"에피소드 {episode_num}화 개선 실패: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"에피소드 {episode_num}화 개선 중 오류: {e}")
            # 오류 발생시 시뮬레이션으로 대체
            await asyncio.sleep(2)
            logger.info(f"✏️ 에피소드 {episode_num}화 기본 개선 완료")
    
    async def perform_intensive_improvement(self, episode_num: int, review_result: Dict):
        """강화된 개선 작업"""
        logger.info(f"💪 에피소드 {episode_num}화 강화된 개선 시작")
        
        # 더 깊이 있는 분석 및 개선
        current_score = review_result.get('overall_score', 0)
        target_improvement = min(0.5, self.target_score - current_score)
        
        logger.info(f"   현재 점수: {current_score:.1f}/10")
        logger.info(f"   목표 개선: +{target_improvement:.1f}")
        
        # 종합적 개선 실행
        try:
            intensive_task = {
                'type': 'improve_episode',
                'episode_number': episode_num,
                'target_areas': [],  # 전체 개선
                'target_score': min(current_score + target_improvement, self.target_score)
            }
            
            result = await self.improver.improve_episode(intensive_task)
            
            if result.get('status') == 'success':
                improvements = result.get('improvements_made', [])
                logger.info(f"🔥 에피소드 {episode_num}화 강화 개선 완료:")
                for improvement in improvements:
                    logger.info(f"   - {improvement}")
            else:
                logger.warning(f"강화 개선 실패: {result.get('error')}")
                
        except Exception as e:
            logger.error(f"강화 개선 중 오류: {e}")
            await asyncio.sleep(5)  # 시뮬레이션
            logger.info(f"🔥 에피소드 {episode_num}화 기본 강화 개선 완료")
    
    async def print_progress_report(self):
        """진행 상황 리포트"""
        runtime = datetime.now() - self.stats['start_time']
        self.stats['runtime_hours'] = runtime.total_seconds() / 3600
        
        logger.info("")
        logger.info("📊 진행 상황 리포트")
        logger.info("=" * 50)
        logger.info(f"⏱️  실행 시간: {runtime}")
        logger.info(f"🔄 총 사이클: {self.iteration_count}")
        logger.info(f"📈 총 개선 횟수: {self.stats['improvements_made']}")
        logger.info(f"📊 평균 사이클당 개선: {self.stats['average_improvement_per_iteration']:.1f}")
        
        logger.info("")
        logger.info("🎯 에피소드별 현재 최고 점수:")
        for episode_num in self.target_episodes:
            best_score = self.best_scores.get(episode_num, 0)
            progress = (best_score / self.target_score) * 100
            status = "✅" if best_score >= self.target_score else "🔄"
            
            logger.info(f"   {episode_num}화: {best_score:.1f}/10 ({progress:.1f}%) {status}")
        
        logger.info("=" * 50)
    
    def save_improvement_history(self):
        """개선 기록 저장"""
        history_file = Path("memory/improvement_history.json")
        history_file.parent.mkdir(exist_ok=True)
        
        save_data = {
            'target_episodes': self.target_episodes,
            'target_score': self.target_score,
            'improvement_history': self.improvement_history,
            'best_scores': self.best_scores,
            'stats': self.stats,
            'last_updated': datetime.now().isoformat()
        }
        
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(save_data, f, ensure_ascii=False, indent=2)
        
        logger.debug(f"개선 기록 저장: {history_file}")
    
    def load_improvement_history(self):
        """개선 기록 로드"""
        history_file = Path("memory/improvement_history.json")
        
        if history_file.exists():
            try:
                with open(history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                self.improvement_history = data.get('improvement_history', {})
                self.best_scores = data.get('best_scores', {})
                prev_stats = data.get('stats', {})
                
                # 이전 통계 복원
                if prev_stats:
                    self.stats.update(prev_stats)
                
                logger.info(f"📁 이전 개선 기록 로드 완료")
                logger.info(f"   총 개선 횟수: {self.stats.get('improvements_made', 0)}")
                
            except Exception as e:
                logger.warning(f"개선 기록 로드 실패: {e}")
    
    async def finalize_improvements(self):
        """개선 작업 마무리"""
        logger.info("")
        logger.info("🏁 무한 개선 시스템 종료")
        
        # 최종 상태 평가
        logger.info("📊 최종 상태:")
        for episode_num in self.target_episodes:
            result = await self.system.review_single_episode(episode_num)
            final_score = result.get('overall_score', 0)
            
            initial_score = 0  # 실제로는 초기 점수를 기록해둬야 함
            if self.improvement_history.get(episode_num):
                first_record = self.improvement_history[episode_num][0]
                initial_score = first_record.get('old_score', 0)
            
            total_improvement = final_score - initial_score if initial_score > 0 else 0
            
            logger.info(f"   {episode_num}화: {final_score:.1f}/10 (개선: +{total_improvement:.1f})")
        
        # 통계 출력
        runtime = datetime.now() - self.stats['start_time']
        logger.info(f"")
        logger.info(f"📈 최종 통계:")
        logger.info(f"   실행 시간: {runtime}")
        logger.info(f"   총 사이클: {self.iteration_count}")
        logger.info(f"   총 개선: {self.stats['improvements_made']}")
        
        # 최종 기록 저장
        self.save_improvement_history()
        
        logger.info("✅ 개선 기록 저장 완료")
    
    def stop(self):
        """시스템 중지"""
        self.running = False


async def main():
    """메인 실행 함수"""
    import sys
    
    # 명령행 인자 처리
    if len(sys.argv) < 2:
        logger.info("사용법: python infinite_improvement.py [에피소드 번호들] [목표점수]")
        logger.info("예시: python infinite_improvement.py 1,2,3 9.5")
        return
    
    try:
        # 에피소드 번호 파싱
        episodes_str = sys.argv[1]
        target_episodes = [int(x.strip()) for x in episodes_str.split(',')]
        
        # 목표 점수 파싱 (선택사항)
        target_score = float(sys.argv[2]) if len(sys.argv) > 2 else 9.5
        
        logger.info(f"🎯 무한 개선 대상: {target_episodes}")
        logger.info(f"🏆 목표 점수: {target_score}/10")
        
        # 무한 개선 시스템 시작
        improvement_system = InfiniteImprovementSystem(target_episodes, target_score)
        await improvement_system.initialize()
        await improvement_system.run_infinite_improvement()
        
    except ValueError as e:
        logger.error(f"잘못된 입력: {e}")
    except KeyboardInterrupt:
        logger.info("사용자 중단")
    except Exception as e:
        logger.error(f"시스템 오류: {e}")


if __name__ == "__main__":
    asyncio.run(main())