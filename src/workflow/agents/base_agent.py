"""
베이스 에이전트 클래스 - 모든 에이전트의 부모 클래스
"""

import asyncio
import json
import logging
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, Any, Optional, List
from pathlib import Path
import yaml
from anthropic import Anthropic
from tenacity import retry, stop_after_attempt, wait_exponential

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """모든 에이전트의 기본 클래스"""
    
    def __init__(self, name: str, config_path: str = "config/config.yaml"):
        self.name = name
        self.config = self.load_config(config_path)
        self.memory = {}
        self.message_queue = asyncio.Queue()
        self.status = "idle"
        self.current_task = None
        self.api_client = None
        self.initialize_api()
        
        logger.info(f"{self.name} 에이전트 초기화 완료")
    
    def load_config(self, config_path: str) -> Dict:
        """설정 파일 로드"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def initialize_api(self):
        """Claude API 초기화"""
        api_key = self.config['claude']['api_key']
        if api_key:
            self.api_client = Anthropic(api_key=api_key)
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def call_claude(self, prompt: str, max_tokens: int = None) -> str:
        """Claude API 호출 with 재시도 로직"""
        
        # API 키가 없거나 더미 키인 경우 테스트 응답 반환
        if not self.api_client or self.config['claude']['api_key'] == '${CLAUDE_API_KEY}':
            logger.info("API 키가 설정되지 않음. 테스트 응답 반환")
            return self.get_mock_response(prompt)
        
        try:
            max_tokens = max_tokens or self.config['claude']['max_tokens']
            
            response = self.api_client.messages.create(
                model=self.config['claude']['model'],
                max_tokens=max_tokens,
                temperature=self.config['claude']['temperature'],
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            # API 사용량 로깅
            self.log_api_usage(len(prompt), len(response.content[0].text))
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Claude API 호출 실패: {e}")
            
            # 한도 도달시 대기
            if "rate_limit" in str(e).lower():
                wait_time = self.config['claude']['limits']['retry_delay']
                logger.info(f"API 한도 도달. {wait_time}초 대기...")
                await asyncio.sleep(wait_time)
                return await self.call_claude(prompt, max_tokens)  # 재시도
            
            raise e
    
    def log_api_usage(self, input_tokens: int, output_tokens: int):
        """API 사용량 로깅"""
        usage_log = {
            "timestamp": datetime.now().isoformat(),
            "agent": self.name,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": input_tokens + output_tokens
        }
        
        # 로그 파일에 기록
        log_file = Path(self.config['logging']['api_usage_log'])
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(usage_log, ensure_ascii=False) + '\n')
    
    async def send_message(self, recipient: str, content: Dict[str, Any]):
        """다른 에이전트에게 메시지 전송"""
        message = {
            "sender": self.name,
            "recipient": recipient,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        # 메시지 큐에 추가 (실제 구현시 중앙 메시지 브로커 사용)
        logger.info(f"{self.name} → {recipient}: {content.get('type', 'message')}")
        return message
    
    async def receive_message(self) -> Optional[Dict]:
        """메시지 수신"""
        try:
            message = await asyncio.wait_for(
                self.message_queue.get(), 
                timeout=1.0
            )
            return message
        except asyncio.TimeoutError:
            return None
    
    def save_memory(self, key: str, value: Any):
        """메모리에 데이터 저장"""
        self.memory[key] = value
        self.persist_memory()
    
    def load_memory(self, key: str) -> Any:
        """메모리에서 데이터 로드"""
        return self.memory.get(key)
    
    def persist_memory(self):
        """메모리를 파일로 저장"""
        memory_dir = Path("memory")
        memory_dir.mkdir(exist_ok=True)
        
        memory_file = memory_dir / f"{self.name.lower()}_memory.json"
        with open(memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=2)
    
    def restore_memory(self):
        """파일에서 메모리 복원"""
        memory_file = Path("memory") / f"{self.name.lower()}_memory.json"
        
        if memory_file.exists():
            with open(memory_file, 'r', encoding='utf-8') as f:
                self.memory = json.load(f)
            logger.info(f"{self.name} 메모리 복원 완료")
    
    async def process_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """작업 처리 (각 에이전트가 구현)"""
        self.status = "processing"
        self.current_task = task
        
        try:
            result = await self.execute(task)
            self.status = "completed"
            return {
                "status": "success",
                "agent": self.name,
                "result": result
            }
        except Exception as e:
            self.status = "error"
            logger.error(f"{self.name} 작업 실패: {e}")
            return {
                "status": "error",
                "agent": self.name,
                "error": str(e)
            }
        finally:
            self.current_task = None
            self.status = "idle"
    
    @abstractmethod
    async def execute(self, task: Dict[str, Any]) -> Any:
        """실제 작업 실행 (각 에이전트가 구현해야 함)"""
        pass
    
    async def run(self):
        """에이전트 메인 루프"""
        logger.info(f"{self.name} 에이전트 시작")
        self.restore_memory()
        
        while True:
            try:
                # 메시지 확인
                message = await self.receive_message()
                if message:
                    await self.handle_message(message)
                
                # 상태 업데이트
                await self.update_status()
                
                # 잠시 대기
                await asyncio.sleep(1)
                
            except KeyboardInterrupt:
                logger.info(f"{self.name} 에이전트 종료")
                break
            except Exception as e:
                logger.error(f"{self.name} 에이전트 오류: {e}")
                await asyncio.sleep(5)
    
    async def handle_message(self, message: Dict):
        """메시지 처리"""
        msg_type = message.get('content', {}).get('type')
        
        if msg_type == 'task':
            # 새 작업 수신
            task = message['content']['task']
            result = await self.process_task(task)
            
            # 결과 전송
            await self.send_message(
                message['sender'],
                {'type': 'result', 'result': result}
            )
        
        elif msg_type == 'status_request':
            # 상태 요청
            await self.send_message(
                message['sender'],
                {'type': 'status', 'status': self.status}
            )
    
    async def update_status(self):
        """상태 업데이트 (필요시 오버라이드)"""
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """현재 상태 반환"""
        return {
            "agent": self.name,
            "status": self.status,
            "current_task": self.current_task,
            "memory_size": len(self.memory)
        }
    
    def get_mock_response(self, prompt: str) -> str:
        """테스트용 더미 응답 생성"""
        logger.info("테스트 모드: 더미 응답 반환")
        
        # 프롬프트 키워드 기반으로 적절한 더미 응답 반환
        if "세계관 일관성" in prompt:
            return "8점 - 공명력 시스템이 일관성 있게 설명되어 있으며, 용어 사용이 통일되어 있습니다."
        elif "캐릭터 일관성" in prompt:
            return "8.5점 - 주인공의 성격과 행동이 일치하며, 능력 수준이 적절합니다."
        elif "연속성" in prompt:
            return "8점 - 이전 화와 자연스럽게 연결되며, 시간적 흐름이 적절합니다."
        elif "작문 품질" in prompt:
            return "7.8점 - 전반적으로 좋은 품질이나, 일부 문장 다듬기가 필요합니다."
        elif "페이싱" in prompt:
            return "8.2점 - 전개 속도가 적절하고 긴장감이 잘 유지됩니다."
        elif "장르 적합성" in prompt:
            return "8.7점 - 포스트 아포칼립스 분위기가 잘 표현되고 판타지 요소가 적절합니다."
        else:
            return "7.5점 - 전반적으로 양호한 품질입니다."