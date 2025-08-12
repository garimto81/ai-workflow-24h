"""
완전 자동화 시스템
파일 모니터링 + 스케줄링 + 웹 대시보드를 결합한 24시간 자동화
"""

import asyncio
import logging
import signal
import sys
from datetime import datetime
from pathlib import Path

# 우리가 만든 모듈들
from auto_monitor import AutoMonitorSystem
from scheduler import ScheduledReviewSystem
from classic_isekai_main import ClassicIsekaiSystem

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/full_automation.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class FullAutomationSystem:
    """완전 자동화 시스템"""
    
    def __init__(self):
        self.monitor_system = None
        self.scheduler_system = None
        self.main_system = None
        self.running = False
        
    async def initialize(self):
        """전체 시스템 초기화"""
        logger.info("=" * 80)
        logger.info("🚀 CLASSIC ISEKAI 완전 자동화 시스템 시작")
        logger.info("=" * 80)
        
        # 디렉토리 생성
        self.ensure_directories()
        
        # 메인 시스템 초기화
        logger.info("📚 Classic Isekai 시스템 초기화...")
        self.main_system = ClassicIsekaiSystem()
        await self.main_system.initialize()
        
        # 파일 모니터링 시스템 초기화
        logger.info("👀 파일 모니터링 시스템 초기화...")
        self.monitor_system = AutoMonitorSystem()
        await self.monitor_system.initialize()
        
        # 스케줄링 시스템 초기화
        logger.info("⏰ 스케줄링 시스템 초기화...")
        self.scheduler_system = ScheduledReviewSystem()
        await self.scheduler_system.initialize()
        
        # 시그널 핸들러 설정 (Ctrl+C 처리)
        self.setup_signal_handlers()
        
        logger.info("✅ 전체 시스템 초기화 완료")
        
    def ensure_directories(self):
        """필요한 디렉토리들 생성"""
        dirs = ['logs', 'reports', 'memory', 'backups']
        for dir_name in dirs:
            Path(dir_name).mkdir(exist_ok=True)
    
    def setup_signal_handlers(self):
        """시그널 핸들러 설정"""
        def signal_handler(signum, frame):
            logger.info("종료 신호 수신. 시스템 정리 중...")
            self.running = False
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    async def run_automation(self):
        """완전 자동화 실행"""
        self.running = True
        
        # 초기 상태 리포트
        await self.print_startup_report()
        
        # 각 시스템을 병렬로 실행
        tasks = []
        
        # 1. 파일 모니터링 시스템 시작
        monitor_task = asyncio.create_task(self.run_monitor_system())
        tasks.append(monitor_task)
        
        # 2. 스케줄링 시스템 시작  
        scheduler_task = asyncio.create_task(self.run_scheduler_system())
        tasks.append(scheduler_task)
        
        # 3. 상태 모니터링 시작
        status_task = asyncio.create_task(self.run_status_monitor())
        tasks.append(status_task)
        
        try:
            # 모든 시스템이 동시에 실행되도록
            await asyncio.gather(*tasks)
            
        except KeyboardInterrupt:
            logger.info("사용자 중단 요청")
        except Exception as e:
            logger.error(f"자동화 시스템 오류: {e}")
        finally:
            await self.cleanup()
    
    async def run_monitor_system(self):
        """파일 모니터링 시스템 실행"""
        try:
            await self.monitor_system.start_monitoring()
        except Exception as e:
            logger.error(f"파일 모니터링 시스템 오류: {e}")
    
    async def run_scheduler_system(self):
        """스케줄링 시스템 실행"""
        try:
            await self.scheduler_system.run_forever()
        except Exception as e:
            logger.error(f"스케줄링 시스템 오류: {e}")
    
    async def run_status_monitor(self):
        """시스템 상태 모니터링"""
        while self.running:
            try:
                # 5분마다 상태 체크
                await asyncio.sleep(300)  # 5분
                
                # 시스템 상태 로깅
                await self.log_system_status()
                
            except Exception as e:
                logger.error(f"상태 모니터링 오류: {e}")
                await asyncio.sleep(60)  # 오류시 1분 대기
    
    async def print_startup_report(self):
        """시작시 현재 상태 리포트"""
        logger.info("")
        logger.info("📊 현재 시스템 상태:")
        
        try:
            # 현재 에피소드 상황
            episodes = self.main_system.project_loader.get_all_episodes()
            logger.info(f"   📖 총 에피소드: {len(episodes)}개")
            
            # 마지막 검토 실행
            result = await self.main_system.review_all_episodes()
            logger.info(f"   ⭐ 평균 품질: {result.get('average_score', 0):.1f}/10")
            logger.info(f"   ✅ 양호한 에피소드: {len(episodes) - result.get('episodes_needing_improvement', 0)}개")
            logger.info(f"   ⚠️ 개선 필요: {result.get('episodes_needing_improvement', 0)}개")
            
        except Exception as e:
            logger.error(f"초기 상태 리포트 생성 실패: {e}")
        
        logger.info("")
        logger.info("🔄 자동화 기능:")
        logger.info("   👀 파일 변경 실시간 감지")
        logger.info("   ⏰ 스케줄 기반 정기 검토")
        logger.info("   📈 자동 품질 평가 및 개선 제안")
        logger.info("   📊 주간/일일 리포트 자동 생성")
        logger.info("")
        logger.info("🚀 24시간 자동화 시작!")
        logger.info("=" * 60)
    
    async def log_system_status(self):
        """시스템 상태 로깅"""
        try:
            current_time = datetime.now()
            
            # 간단한 상태 체크
            episodes_count = len(self.main_system.project_loader.get_all_episodes())
            
            logger.info(f"🔄 {current_time.strftime('%H:%M')} 상태: 정상 | 에피소드 {episodes_count}개 | 모니터링 활성")
            
        except Exception as e:
            logger.error(f"상태 로깅 오류: {e}")
    
    async def cleanup(self):
        """시스템 정리"""
        logger.info("🧹 시스템 정리 시작...")
        
        try:
            # 각 시스템 정리
            if self.monitor_system:
                self.monitor_system.stop_monitoring()
            
            if self.scheduler_system:
                self.scheduler_system.stop_scheduler()
            
            # 프로젝트 상태 저장
            if self.main_system:
                self.main_system.project_loader.save_project_state()
            
            logger.info("✅ 시스템 정리 완료")
            
        except Exception as e:
            logger.error(f"시스템 정리 중 오류: {e}")


# 사용법 안내 함수들
def print_usage():
    """사용법 출력"""
    logger.info("Classic Isekai 완전 자동화 시스템")
    logger.info("")
    logger.info("사용법:")
    logger.info("  python full_automation.py                # 완전 자동화 시작")
    logger.info("  python full_automation.py --help         # 도움말")
    logger.info("  python full_automation.py --status       # 현재 상태만 확인")
    logger.info("")
    logger.info("자동화 기능:")
    logger.info("  - 새 에피소드 자동 감지 및 검토")
    logger.info("  - 에피소드 수정시 자동 재검토")
    logger.info("  - 스케줄 기반 정기 검토 (매일 09:00, 18:00)")
    logger.info("  - 자정 시스템 정리 및 백업")
    logger.info("  - 주간 리포트 자동 생성 (일요일 20:00)")
    logger.info("  - 시간당 헬스체크")
    logger.info("")
    logger.info("종료: Ctrl+C를 눌러 안전하게 종료")


async def check_status_only():
    """상태만 확인"""
    system = ClassicIsekaiSystem()
    await system.initialize()
    
    result = await system.review_all_episodes()
    
    logger.info("Classic Isekai 현재 상태")
    logger.info("================================")
    logger.info(f"총 에피소드: {result.get('total_episodes', 0)}개")
    logger.info(f"평균 품질: {result.get('average_score', 0):.1f}/10")
    logger.info(f"최고 점수: {result.get('highest_score', 0):.1f}/10")
    logger.info(f"최저 점수: {result.get('lowest_score', 0):.1f}/10")
    logger.info(f"개선 필요: {result.get('episodes_needing_improvement', 0)}개")


async def main():
    """메인 실행 함수"""
    # 명령행 인자 처리
    if "--help" in sys.argv or "-h" in sys.argv:
        print_usage()
        return
    
    if "--status" in sys.argv:
        await check_status_only()
        return
    
    # 완전 자동화 시스템 시작
    automation = FullAutomationSystem()
    
    try:
        await automation.initialize()
        await automation.run_automation()
    except KeyboardInterrupt:
        logger.info("사용자 중단")
    except Exception as e:
        logger.error(f"시스템 실행 오류: {e}")
    finally:
        await automation.cleanup()
        logger.info("Complete Isekai 자동화 시스템 종료")


if __name__ == "__main__":
    # 필요한 패키지 확인
    try:
        import schedule
        import watchdog
    except ImportError as e:
        print(f"필요한 패키지가 없습니다: pip install schedule watchdog")
        print(f"오류: {e}")
        sys.exit(1)
    
    # 실행
    asyncio.run(main())