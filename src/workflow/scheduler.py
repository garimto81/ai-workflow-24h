"""
스케줄링 기반 자동화 시스템
정해진 시간에 자동으로 검토 및 작업 실행
"""

import asyncio
import schedule
import time
import logging
from datetime import datetime
from threading import Thread
from classic_isekai_main import ClassicIsekaiSystem

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scheduler.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ScheduledReviewSystem:
    """스케줄 기반 검토 시스템"""
    
    def __init__(self):
        self.system = None
        self.running = False
        self.scheduler_thread = None
    
    async def initialize(self):
        """시스템 초기화"""
        logger.info("=" * 60)
        logger.info("스케줄 기반 자동화 시스템 초기화")
        logger.info("=" * 60)
        
        # Classic Isekai 시스템 초기화
        self.system = ClassicIsekaiSystem()
        await self.system.initialize()
        
        # 스케줄 설정
        self.setup_schedules()
        
        logger.info("스케줄링 시스템 초기화 완료")
    
    def setup_schedules(self):
        """스케줄 설정"""
        
        # ⏰ 매일 오전 9시 - 전체 검토
        schedule.every().day.at("09:00").do(self.run_async_job, self.daily_full_review)
        
        # ⏰ 매일 오후 6시 - 새 에피소드 체크
        schedule.every().day.at("18:00").do(self.run_async_job, self.check_new_episodes)
        
        # ⏰ 매일 자정 - 시스템 상태 체크 및 정리
        schedule.every().day.at("00:00").do(self.run_async_job, self.midnight_maintenance)
        
        # ⏰ 매주 일요일 오후 8시 - 주간 요약 리포트
        schedule.every().sunday.at("20:00").do(self.run_async_job, self.weekly_report)
        
        # ⏰ 매시간 정각 - 시스템 헬스체크
        schedule.every().hour.at(":00").do(self.run_async_job, self.hourly_health_check)
        
        logger.info("스케줄 설정 완료:")
        logger.info("  - 09:00: 일일 전체 검토")
        logger.info("  - 18:00: 새 에피소드 체크")
        logger.info("  - 00:00: 시스템 정리")
        logger.info("  - 매시 정각: 헬스체크")
        logger.info("  - 일요일 20:00: 주간 리포트")
    
    def run_async_job(self, coro_func):
        """비동기 함수를 스케줄에서 실행"""
        def job():
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(coro_func())
            except Exception as e:
                logger.error(f"스케줄 작업 실행 오류: {e}")
            finally:
                loop.close()
        
        # 백그라운드 스레드에서 실행
        thread = Thread(target=job)
        thread.daemon = True
        thread.start()
    
    async def daily_full_review(self):
        """일일 전체 검토"""
        logger.info("🌅 일일 전체 검토 시작")
        
        try:
            result = await self.system.review_all_episodes()
            
            avg_score = result.get('average_score', 0)
            total_episodes = result.get('total_episodes', 0)
            needs_improvement = result.get('episodes_needing_improvement', 0)
            
            logger.info(f"📊 일일 검토 완료:")
            logger.info(f"   총 에피소드: {total_episodes}개")
            logger.info(f"   평균 점수: {avg_score:.1f}/10")
            logger.info(f"   개선 필요: {needs_improvement}개")
            
            # 개선이 필요한 에피소드가 있으면 처리
            if needs_improvement > 0:
                await self.handle_improvement_needed(result)
                
        except Exception as e:
            logger.error(f"일일 전체 검토 중 오류: {e}")
    
    async def check_new_episodes(self):
        """새 에피소드 체크"""
        logger.info("🔍 새 에피소드 체크 시작")
        
        try:
            # 프로젝트 로더를 통해 에피소드 목록 확인
            await self.system.project_loader.scan_episodes()
            episodes = self.system.project_loader.get_all_episodes()
            
            logger.info(f"현재 총 {len(episodes)}개 에피소드 확인")
            
            # 각 에피소드 간단 체크
            for ep_num in episodes.keys():
                # 최근 수정된 에피소드만 재검토 (예: 오늘 수정된 파일)
                # 실제로는 파일 수정 시간을 확인하는 로직 필요
                pass
                
        except Exception as e:
            logger.error(f"새 에피소드 체크 중 오류: {e}")
    
    async def midnight_maintenance(self):
        """자정 정리 작업"""
        logger.info("🌙 자정 시스템 정리 시작")
        
        try:
            # 메모리 상태 저장
            self.system.project_loader.save_project_state()
            
            # 로그 파일 정리 (7일 이상 된 로그 삭제)
            self.cleanup_old_logs()
            
            logger.info("시스템 정리 완료")
            
        except Exception as e:
            logger.error(f"자정 정리 작업 중 오류: {e}")
    
    async def weekly_report(self):
        """주간 요약 리포트"""
        logger.info("📈 주간 요약 리포트 생성")
        
        try:
            # 전체 검토 실행
            result = await self.system.review_all_episodes()
            
            # 리포트 생성
            report = self.generate_weekly_report(result)
            
            # 리포트 파일로 저장
            from datetime import datetime
            report_file = f"reports/weekly_report_{datetime.now().strftime('%Y%m%d')}.md"
            
            import os
            os.makedirs("reports", exist_ok=True)
            
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)
            
            logger.info(f"주간 리포트 저장: {report_file}")
            
        except Exception as e:
            logger.error(f"주간 리포트 생성 중 오류: {e}")
    
    async def hourly_health_check(self):
        """시간당 헬스체크"""
        current_time = datetime.now().strftime("%H:%M")
        logger.info(f"💚 {current_time} - 시스템 정상 작동 중")
        
        # 시스템 상태 간단 체크
        try:
            # 프로젝트 로더 상태 확인
            if self.system and self.system.project_loader:
                episodes_count = len(self.system.project_loader.documents.get('episodes_list', []))
                logger.debug(f"   현재 {episodes_count}개 에피소드 로드됨")
        except Exception as e:
            logger.warning(f"헬스체크 중 경고: {e}")
    
    async def handle_improvement_needed(self, review_result):
        """개선 필요한 에피소드 처리"""
        detailed_results = review_result.get('detailed_results', {})
        
        for ep_num, ep_result in detailed_results.items():
            if ep_result.get('overall_score', 10) < 7.5:
                logger.info(f"🔧 에피소드 {ep_num}화 개선 계획 생성 중...")
                try:
                    await self.system.improve_episode(ep_num)
                except Exception as e:
                    logger.error(f"에피소드 {ep_num}화 개선 계획 생성 실패: {e}")
    
    def generate_weekly_report(self, review_result) -> str:
        """주간 리포트 생성"""
        from datetime import datetime, timedelta
        
        week_start = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        week_end = datetime.now().strftime("%Y-%m-%d")
        
        report = f"""# 📊 Classic Isekai 주간 리포트
**기간**: {week_start} ~ {week_end}

## 전체 현황
- **총 에피소드**: {review_result.get('total_episodes', 0)}개
- **평균 품질**: {review_result.get('average_score', 0):.1f}/10
- **최고 점수**: {review_result.get('highest_score', 0):.1f}/10
- **최저 점수**: {review_result.get('lowest_score', 0):.1f}/10
- **개선 필요**: {review_result.get('episodes_needing_improvement', 0)}개

## 에피소드별 상세
"""
        
        detailed_results = review_result.get('detailed_results', {})
        for ep_num in sorted(detailed_results.keys()):
            ep_result = detailed_results[ep_num]
            status_icon = "✅" if ep_result.get('overall_score', 0) >= 7.5 else "⚠️"
            report += f"- **{ep_num}화**: {ep_result.get('overall_score', 0):.1f}/10 {status_icon}\\n"
        
        report += f"""

## 시스템 상태
- **마지막 업데이트**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **자동화 상태**: 정상 작동 중

---
*자동 생성된 리포트입니다.*
"""
        
        return report
    
    def cleanup_old_logs(self):
        """오래된 로그 파일 정리"""
        try:
            import os
            from pathlib import Path
            
            logs_dir = Path("logs")
            if logs_dir.exists():
                for log_file in logs_dir.glob("*.log.*"):
                    # 7일 이상 된 로그 파일 삭제
                    file_age = time.time() - log_file.stat().st_mtime
                    if file_age > 7 * 24 * 3600:  # 7일
                        log_file.unlink()
                        logger.debug(f"오래된 로그 파일 삭제: {log_file.name}")
        except Exception as e:
            logger.warning(f"로그 정리 중 오류: {e}")
    
    def start_scheduler(self):
        """스케줄러 시작"""
        def run_scheduler():
            logger.info("📅 스케줄러 시작")
            while self.running:
                schedule.run_pending()
                time.sleep(1)
            logger.info("스케줄러 종료")
        
        self.running = True
        self.scheduler_thread = Thread(target=run_scheduler)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
    
    def stop_scheduler(self):
        """스케줄러 중지"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join()
    
    async def run_forever(self):
        """무한 실행"""
        self.start_scheduler()
        
        try:
            logger.info("🚀 24시간 스케줄링 시스템 시작")
            logger.info("Ctrl+C로 종료할 수 있습니다")
            
            while self.running:
                await asyncio.sleep(10)  # 10초마다 체크
                
        except KeyboardInterrupt:
            logger.info("사용자 중단 요청")
        finally:
            self.stop_scheduler()


async def main():
    """메인 실행 함수"""
    scheduler_system = ScheduledReviewSystem()
    
    try:
        await scheduler_system.initialize()
        await scheduler_system.run_forever()
    except Exception as e:
        logger.error(f"스케줄링 시스템 오류: {e}")
    finally:
        scheduler_system.stop_scheduler()


if __name__ == "__main__":
    # 필요한 패키지 설치
    try:
        import schedule
    except ImportError:
        logger.error("schedule 패키지가 필요합니다: pip install schedule")
        exit(1)
    
    # 실행
    asyncio.run(main())