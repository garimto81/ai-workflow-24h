"""
새로운 11개 에이전트 통합 시스템
메인 조율 에이전트를 중심으로 한 24시간 무중단 개선 시스템
"""

import asyncio
import logging
import os
from datetime import datetime
from pathlib import Path

from agents.main_coordinator import MainCoordinatorAgent

# 로깅 설정 - 환경에 따라 다르게 설정
handlers = [logging.StreamHandler()]

# GitHub Actions가 아닌 로컬 환경에서는 파일 로깅도 추가
if not os.environ.get('GITHUB_ACTIONS'):
    os.makedirs('logs', exist_ok=True)
    handlers.append(logging.FileHandler('logs/new_agent_system.log', encoding='utf-8'))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=handlers
)
logger = logging.getLogger(__name__)


class NewAgentSystem:
    """새로운 11개 에이전트 통합 시스템"""
    
    def __init__(self):
        self.main_coordinator = None
        self.running = False
        self.stats = {
            'cycles_completed': 0,
            'total_improvements': 0,
            'start_time': None
        }
    
    async def initialize(self):
        """시스템 초기화"""
        logger.info("=" * 80)
        logger.info("🚀 새로운 11개 에이전트 시스템 시작")
        logger.info("=" * 80)
        
        # 디렉토리 생성
        self.ensure_directories()
        
        # 메인 조율 에이전트 초기화
        logger.info("🎯 메인 조율 에이전트 초기화...")
        self.main_coordinator = MainCoordinatorAgent()
        await self.main_coordinator.initialize()
        
        # 통계 초기화
        self.stats['start_time'] = datetime.now()
        
        logger.info("✅ 새로운 에이전트 시스템 초기화 완료")
        
        # 시스템 구성 요약
        await self.print_system_overview()
    
    def ensure_directories(self):
        """필요한 디렉토리들 생성"""
        dirs = [
            'logs', 'reports', 'memory', 'backups',
            'memory/agent_cycles', 'logs/improvements'
        ]
        for dir_name in dirs:
            Path(dir_name).mkdir(parents=True, exist_ok=True)
    
    async def print_system_overview(self):
        """시스템 구성 개요 출력"""
        logger.info("")
        logger.info("🎯 시스템 구성:")
        logger.info("=" * 50)
        logger.info("【사용자 지정 8개 에이전트】")
        logger.info("  1. 📋 메인 에이전트 - 전체 조율")
        logger.info("  2. ✍️ 작가 에이전트 - 스토리 분석")
        logger.info("  3. 📝 문법 에이전트 - 문법/오탈자 검증")
        logger.info("  4. 🌍 세계관 에이전트 - 설정 일관성")
        logger.info("  5. ⏰ 역사 에이전트 - 시간선 관리")
        logger.info("  6. 👥 독자 에이전트 - 10개 페르소나 평가")
        logger.info("  7. 🔗 연관성 에이전트 - 에피소드간 연결")
        logger.info("  8. 🔧 설정개선 에이전트 - 동적 설정 업데이트")
        logger.info("")
        logger.info("【추가 시스템 에이전트】")
        logger.info("  9. 🔍 품질평가 에이전트 - 종합 점수 산정")
        logger.info("  10. ✏️ 에피소드개선 에이전트 - 실제 파일 수정")
        logger.info("  11. 💾 데이터관리 에이전트 - 프로젝트 관리")
        logger.info("")
        logger.info("🔄 운영 방식:")
        logger.info("  • 35분 완전 사이클 (분석→검토→개선→저장)")
        logger.info("  • 1화→2화→3화 순차 처리")
        logger.info("  • 독자 10명이 동시 다각도 평가")
        logger.info("  • 목표 점수 달성까지 무한 반복")
        logger.info("=" * 50)
    
    async def run_infinite_improvement(self, target_episodes: list = [1, 2, 3], target_score: float = 9.5):
        """무한 개선 실행"""
        self.running = True
        logger.info(f"🚀 무한 개선 시작 - 대상: {target_episodes}화, 목표: {target_score}/10")
        
        try:
            while self.running:
                cycle_start = datetime.now()
                logger.info(f"")
                logger.info(f"🔄 ===== 개선 사이클 #{self.stats['cycles_completed'] + 1} =====")
                
                cycle_improvements = 0
                
                # 각 에피소드별로 35분 완전 사이클 실행
                for episode_num in target_episodes:
                    if not self.running:
                        break
                    
                    logger.info(f"")
                    logger.info(f"📖 에피소드 {episode_num}화 처리 시작...")
                    
                    # 메인 조율 에이전트에 작업 요청
                    improvement_task = {
                        'type': 'improve_episode',
                        'episode_number': episode_num,
                        'target_score': target_score
                    }
                    
                    result = await self.main_coordinator.coordinate_episode_improvement(improvement_task)
                    
                    if result.get('status') == 'success':
                        improvements_count = len(result.get('improvements_made', []))
                        final_score = result.get('final_score', 0)
                        
                        logger.info(f"✅ {episode_num}화 처리 완료 - 점수: {final_score:.1f}/10, 개선: {improvements_count}개")
                        
                        cycle_improvements += improvements_count
                        
                        # 목표 달성 체크
                        if final_score >= target_score:
                            logger.info(f"🎉 {episode_num}화 목표 점수 달성! ({final_score:.1f}/10)")
                    else:
                        logger.error(f"❌ {episode_num}화 처리 실패: {result.get('error', 'Unknown error')}")
                    
                    # 에피소드간 1분 대기
                    if self.running:
                        logger.info(f"⏳ 다음 에피소드까지 1분 대기...")
                        await asyncio.sleep(60)
                
                # 사이클 완료
                self.stats['cycles_completed'] += 1
                self.stats['total_improvements'] += cycle_improvements
                
                cycle_end = datetime.now()
                cycle_duration = (cycle_end - cycle_start).total_seconds() / 60  # 분 단위
                
                logger.info(f"")
                logger.info(f"📈 사이클 #{self.stats['cycles_completed']} 완료")
                logger.info(f"   소요 시간: {cycle_duration:.1f}분")
                logger.info(f"   이번 사이클 개선: {cycle_improvements}개")
                logger.info(f"   총 누적 개선: {self.stats['total_improvements']}개")
                
                # 10 사이클마다 상세 리포트
                if self.stats['cycles_completed'] % 10 == 0:
                    await self.print_progress_report()
                
                # 전체 사이클 완료 후 5분 대기
                if self.running:
                    logger.info(f"⏳ 다음 전체 사이클까지 5분 대기...")
                    await asyncio.sleep(300)  # 5분 대기
                
        except KeyboardInterrupt:
            logger.info("사용자 중단 요청")
        except Exception as e:
            logger.error(f"무한 개선 시스템 오류: {e}")
        finally:
            await self.finalize_system()
    
    async def print_progress_report(self):
        """진행 상황 리포트"""
        runtime = datetime.now() - self.stats['start_time']
        runtime_hours = runtime.total_seconds() / 3600
        
        logger.info("")
        logger.info("📊 ===== 진행 상황 리포트 =====")
        logger.info("=" * 50)
        logger.info(f"⏱️  실행 시간: {runtime}")
        logger.info(f"🔄 완료된 사이클: {self.stats['cycles_completed']}")
        logger.info(f"📈 총 개선 횟수: {self.stats['total_improvements']}")
        logger.info(f"📊 평균 사이클당 개선: {self.stats['total_improvements'] / max(self.stats['cycles_completed'], 1):.1f}")
        logger.info(f"⚡ 시간당 개선: {self.stats['total_improvements'] / max(runtime_hours, 0.1):.1f}")
        
        # 각 에피소드 상태 체크 (메인 조율러를 통해)
        logger.info("")
        logger.info("🎯 에피소드별 현재 상태:")
        for episode_num in [1, 2, 3]:
            try:
                # 현재 상태 조회
                status_task = {
                    'type': 'analyze_episode',
                    'episode_number': episode_num
                }
                # 간단한 상태만 체크 (실제 구현에서는 더 정교하게)
                logger.info(f"   📖 {episode_num}화: 처리 중...")
            except Exception as e:
                logger.warning(f"   📖 {episode_num}화 상태 확인 실패: {e}")
        
        logger.info("=" * 50)
    
    async def finalize_system(self):
        """시스템 종료 처리"""
        logger.info("")
        logger.info("🏁 새로운 에이전트 시스템 종료 중...")
        
        # 최종 통계
        if self.stats.get('start_time'):
            runtime = datetime.now() - self.stats['start_time']
        else:
            runtime = datetime.now() - datetime.now()  # 0초
        
        logger.info("")
        logger.info("📈 최종 실행 통계:")
        logger.info(f"   총 실행 시간: {runtime}")
        logger.info(f"   완료된 사이클: {self.stats['cycles_completed']}")
        logger.info(f"   총 개선 횟수: {self.stats['total_improvements']}")
        
        # 시스템 정리
        self.running = False
        
        logger.info("✅ 시스템 종료 완료")
    
    def stop(self):
        """시스템 중지"""
        logger.info("중지 요청 받음...")
        self.running = False


async def main():
    """메인 실행 함수"""
    import sys
    
    # 명령행 인자 처리
    target_episodes = [1, 2, 3]  # 기본값
    target_score = 9.5  # 기본값
    
    if len(sys.argv) >= 2:
        try:
            episodes_str = sys.argv[1]
            target_episodes = [int(x.strip()) for x in episodes_str.split(',')]
        except ValueError:
            logger.error("에피소드 번호 형식이 잘못되었습니다. 예: 1,2,3")
            return
    
    if len(sys.argv) >= 3:
        try:
            target_score = float(sys.argv[2])
        except ValueError:
            logger.error("목표 점수 형식이 잘못되었습니다. 예: 9.5")
            return
    
    # 새로운 에이전트 시스템 시작
    system = NewAgentSystem()
    
    try:
        await system.initialize()
        await system.run_infinite_improvement(target_episodes, target_score)
    except KeyboardInterrupt:
        logger.info("사용자 중단")
    except Exception as e:
        logger.error(f"시스템 오류: {e}")
    finally:
        await system.finalize_system()


if __name__ == "__main__":
    # 실행
    asyncio.run(main())