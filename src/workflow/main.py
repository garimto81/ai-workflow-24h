"""
웹소설 24시간 자동 생성 시스템 - 메인 실행 파일
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path
from datetime import datetime
import yaml
from typing import List, Dict, Any

# 에이전트 임포트
from agents.main_agent import MainAgent
from agents.writer_agent import WriterAgent
# from agents.pm_agent import PMAgent
# from agents.worldbuilding_agent import WorldbuildingAgent
# from agents.history_agent import HistoryAgent
# from agents.grammar_agent import GrammarAgent
# from agents.ai_detection_agent import AIDetectionAgent
# from agents.reader_agent import ReaderAgent
# from agents.qa_agent import QAAgent

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/webnovel.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class WebNovelAutomationSystem:
    """웹소설 자동화 시스템 메인 클래스"""
    
    def __init__(self, config_path: str = "config/config.yaml"):
        self.config = self.load_config(config_path)
        self.agents = {}
        self.running = False
        
        # 디렉토리 생성
        self.setup_directories()
        
        logger.info("웹소설 자동화 시스템 초기화")
    
    def load_config(self, config_path: str) -> Dict:
        """설정 파일 로드"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def setup_directories(self):
        """필요한 디렉토리 생성"""
        directories = [
            "documents/worldbuilding",
            "documents/history",
            "documents/episodes",
            "documents/drafts",
            "documents/reviews",
            "memory",
            "logs/agents",
        ]
        
        for dir_path in directories:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
        
        logger.info("디렉토리 구조 생성 완료")
    
    async def initialize_agents(self):
        """모든 에이전트 초기화"""
        logger.info("에이전트 초기화 시작...")
        
        # 메인 에이전트
        self.agents['main'] = MainAgent()
        
        # 작가 에이전트
        self.agents['writer'] = WriterAgent()
        
        # PM 에이전트 (구현 예정)
        # self.agents['pm'] = PMAgent()
        
        # 세계관 담당 (구현 예정)
        # self.agents['worldbuilding'] = WorldbuildingAgent()
        
        # 역사 담당 (구현 예정)
        # self.agents['history'] = HistoryAgent()
        
        # 문법 담당 (구현 예정)
        # self.agents['grammar'] = GrammarAgent()
        
        # AI 화법 감지 (구현 예정)
        # self.agents['ai_detection'] = AIDetectionAgent()
        
        # 독자 에이전트들 (구현 예정)
        # reader_count = self.config['agents']['readers']['count']
        # self.agents['readers'] = []
        # for i in range(reader_count):
        #     reader = ReaderAgent(persona=self.config['agents']['readers']['personas'][i])
        #     self.agents['readers'].append(reader)
        
        # QA 담당 (구현 예정)
        # self.agents['qa'] = QAAgent()
        
        # 에이전트 등록
        for agent_type, agent in self.agents.items():
            if agent_type != 'main' and agent:
                self.agents['main'].register_agent(agent_type, agent)
        
        logger.info(f"총 {len(self.agents)}개 에이전트 초기화 완료")
    
    async def start_agents(self):
        """모든 에이전트 시작"""
        tasks = []
        
        for agent_name, agent in self.agents.items():
            if agent:
                task = asyncio.create_task(agent.run())
                tasks.append(task)
                logger.info(f"{agent_name} 에이전트 시작")
        
        return tasks
    
    async def create_sample_episode(self):
        """테스트용 샘플 에피소드 생성"""
        logger.info("샘플 에피소드 생성 테스트")
        
        # 작가 에이전트 직접 호출
        writer = self.agents.get('writer')
        if writer:
            task = {
                'type': 'create_episode',
                'previous_content': ''
            }
            
            result = await writer.execute(task)
            
            # 결과 저장
            if result.get('content'):
                output_file = Path("documents/drafts") / f"episode_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(result['content'])
                
                logger.info(f"샘플 에피소드 저장: {output_file}")
                return result
        
        return None
    
    async def run(self):
        """시스템 실행"""
        self.running = True
        logger.info("=" * 50)
        logger.info("웹소설 24시간 자동 생성 시스템 시작")
        logger.info("=" * 50)
        
        try:
            # 에이전트 초기화
            await self.initialize_agents()
            
            # 에이전트 시작
            agent_tasks = await self.start_agents()
            
            # 초기 테스트 (옵션)
            if "--test" in sys.argv:
                await asyncio.sleep(2)  # 에이전트 준비 대기
                await self.create_sample_episode()
            
            # 메인 루프
            while self.running:
                await asyncio.sleep(10)
                
                # 상태 체크
                status = self.get_system_status()
                if datetime.now().second == 0:  # 매 분마다
                    logger.info(f"시스템 상태: {status}")
            
        except KeyboardInterrupt:
            logger.info("시스템 종료 신호 수신")
        except Exception as e:
            logger.error(f"시스템 오류: {e}")
        finally:
            await self.shutdown()
    
    def get_system_status(self) -> Dict[str, Any]:
        """시스템 상태 확인"""
        status = {
            "running": self.running,
            "agents": {},
            "timestamp": datetime.now().isoformat()
        }
        
        for name, agent in self.agents.items():
            if agent:
                status["agents"][name] = agent.get_status()
        
        return status
    
    async def shutdown(self):
        """시스템 종료"""
        logger.info("시스템 종료 중...")
        self.running = False
        
        # 모든 에이전트 종료
        for agent in self.agents.values():
            if agent and hasattr(agent, 'shutdown'):
                await agent.shutdown()
        
        logger.info("시스템 종료 완료")


def signal_handler(signum, frame):
    """시그널 핸들러"""
    logger.info(f"Signal {signum} received")
    sys.exit(0)


async def main():
    """메인 함수"""
    # 시그널 핸들러 등록
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 시스템 실행
    system = WebNovelAutomationSystem()
    await system.run()


if __name__ == "__main__":
    # 커맨드라인 인자 처리
    if "--help" in sys.argv:
        print("""
웹소설 24시간 자동 생성 시스템

사용법:
  python main.py           # 일반 실행
  python main.py --test    # 테스트 모드 (샘플 에피소드 생성)
  python main.py --help    # 도움말

설정 파일: config/config.yaml
로그 파일: logs/webnovel.log
        """)
        sys.exit(0)
    
    # 실행
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("프로그램 종료")
    except Exception as e:
        logger.error(f"실행 오류: {e}")
        sys.exit(1)