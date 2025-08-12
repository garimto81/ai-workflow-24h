"""
24시간 자동 모니터링 시스템
새로운 에피소드가 추가되면 자동으로 검토 실행
"""

import asyncio
import time
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime, timedelta
from classic_isekai_main import ClassicIsekaiSystem

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/auto_monitor.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class EpisodeFileHandler(FileSystemEventHandler):
    """에피소드 파일 변경 감지 핸들러"""
    
    def __init__(self, system: ClassicIsekaiSystem):
        self.system = system
        self.last_processed = {}  # 중복 처리 방지
        
    def on_created(self, event):
        """새 파일 생성 감지"""
        if not event.is_directory and event.src_path.endswith('.md'):
            file_path = Path(event.src_path)
            if self.is_episode_file(file_path):
                logger.info(f"새 에피소드 감지: {file_path.name}")
                asyncio.create_task(self.process_new_episode(file_path))
    
    def on_modified(self, event):
        """파일 수정 감지"""
        if not event.is_directory and event.src_path.endswith('.md'):
            file_path = Path(event.src_path)
            if self.is_episode_file(file_path):
                # 중복 처리 방지 (파일이 수정될 때 여러 이벤트 발생)
                now = datetime.now()
                if file_path in self.last_processed:
                    if now - self.last_processed[file_path] < timedelta(seconds=5):
                        return
                
                self.last_processed[file_path] = now
                logger.info(f"에피소드 수정 감지: {file_path.name}")
                asyncio.create_task(self.process_modified_episode(file_path))
    
    def is_episode_file(self, file_path: Path) -> bool:
        """에피소드 파일인지 확인"""
        filename = file_path.name
        # "제N화_제목.md" 형식인지 확인
        import re
        return bool(re.match(r'제\d+화_.*\.md', filename))
    
    async def process_new_episode(self, file_path: Path):
        """새 에피소드 처리"""
        try:
            # 파일이 완전히 생성될 때까지 잠시 대기
            await asyncio.sleep(2)
            
            episode_number = self.extract_episode_number(file_path.name)
            if episode_number:
                logger.info(f"새 에피소드 {episode_number}화 자동 검토 시작")
                result = await self.system.review_single_episode(episode_number)
                
                # 검토 결과에 따른 알림
                score = result.get('overall_score', 0)
                if score >= 8.0:
                    logger.info(f"✅ 에피소드 {episode_number}화 검토 완료 - 우수 ({score}/10)")
                elif score >= 7.0:
                    logger.info(f"⚠️ 에피소드 {episode_number}화 검토 완료 - 양호 ({score}/10)")
                else:
                    logger.warning(f"❌ 에피소드 {episode_number}화 검토 완료 - 개선 필요 ({score}/10)")
                    # 개선 계획 자동 생성
                    await self.system.improve_episode(episode_number)
                
        except Exception as e:
            logger.error(f"새 에피소드 처리 중 오류: {e}")
    
    async def process_modified_episode(self, file_path: Path):
        """수정된 에피소드 처리"""
        try:
            episode_number = self.extract_episode_number(file_path.name)
            if episode_number:
                logger.info(f"수정된 에피소드 {episode_number}화 재검토 시작")
                result = await self.system.review_single_episode(episode_number)
                
                score = result.get('overall_score', 0)
                logger.info(f"재검토 완료 - 에피소드 {episode_number}화: {score}/10")
                
        except Exception as e:
            logger.error(f"수정된 에피소드 처리 중 오류: {e}")
    
    def extract_episode_number(self, filename: str) -> int:
        """파일명에서 에피소드 번호 추출"""
        try:
            import re
            match = re.search(r'제(\d+)화', filename)
            if match:
                return int(match.group(1))
        except:
            pass
        return 0


class AutoMonitorSystem:
    """24시간 자동 모니터링 시스템"""
    
    def __init__(self):
        self.system = None
        self.observer = None
        self.running = False
        
    async def initialize(self):
        """시스템 초기화"""
        logger.info("=" * 60)
        logger.info("24시간 자동 모니터링 시스템 시작")
        logger.info("=" * 60)
        
        # Classic Isekai 시스템 초기화
        self.system = ClassicIsekaiSystem()
        await self.system.initialize()
        
        # 파일 모니터링 설정
        self.setup_file_monitoring()
        
        logger.info("자동 모니터링 시스템 초기화 완료")
    
    def setup_file_monitoring(self):
        """파일 모니터링 설정"""
        episodes_path = Path("C:/claude04/classic-isekai/webnovel_episodes")
        
        if not episodes_path.exists():
            logger.error(f"에피소드 디렉토리를 찾을 수 없음: {episodes_path}")
            return
        
        # 파일 이벤트 핸들러 생성
        event_handler = EpisodeFileHandler(self.system)
        
        # Observer 설정
        self.observer = Observer()
        self.observer.schedule(event_handler, str(episodes_path), recursive=False)
        
        logger.info(f"파일 모니터링 설정 완료: {episodes_path}")
    
    async def start_monitoring(self):
        """모니터링 시작"""
        if not self.observer:
            logger.error("파일 모니터링이 설정되지 않았습니다")
            return
        
        # 파일 감시자 시작
        self.observer.start()
        self.running = True
        
        logger.info("🔄 24시간 자동 모니터링 시작")
        logger.info("새 에피소드 추가나 수정을 감지하면 자동으로 검토합니다")
        
        try:
            # 주기적 작업들
            while self.running:
                # 1시간마다 전체 상태 체크
                await self.hourly_check()
                
                # 60초 대기
                await asyncio.sleep(60)
                
        except KeyboardInterrupt:
            logger.info("사용자에 의한 중단 요청")
        finally:
            self.stop_monitoring()
    
    async def hourly_check(self):
        """시간당 체크 작업"""
        current_hour = datetime.now().hour
        
        # 매일 오전 9시에 전체 검토
        if current_hour == 9:
            logger.info("📊 일일 전체 검토 실행")
            await self.system.review_all_episodes()
        
        # 상태 로깅
        logger.info(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')} - 시스템 정상 작동 중")
    
    def stop_monitoring(self):
        """모니터링 중지"""
        if self.observer:
            self.observer.stop()
            self.observer.join()
        
        self.running = False
        logger.info("자동 모니터링 시스템 종료")


async def main():
    """메인 실행 함수"""
    monitor = AutoMonitorSystem()
    
    try:
        await monitor.initialize()
        await monitor.start_monitoring()
    except Exception as e:
        logger.error(f"자동 모니터링 시스템 오류: {e}")
    finally:
        monitor.stop_monitoring()


if __name__ == "__main__":
    # 실행
    asyncio.run(main())