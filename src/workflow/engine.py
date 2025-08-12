"""
워크플로우 엔진 - 24시간 자동 작업 처리 핵심
"""

import asyncio
import json
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Callable
from enum import Enum
import logging
from dataclasses import dataclass, asdict

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    RETRY = "retry"
    CANCELLED = "cancelled"

class TaskPriority(Enum):
    LOW = 1
    NORMAL = 5
    HIGH = 7
    CRITICAL = 10

@dataclass
class Task:
    """작업 단위"""
    id: str
    name: str
    type: str
    payload: Dict[str, Any]
    status: TaskStatus = TaskStatus.PENDING
    priority: int = TaskPriority.NORMAL.value
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    retry_count: int = 0
    max_retries: int = 3
    result: Optional[Any] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.now()
        if not self.id:
            self.id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict:
        data = asdict(self)
        data['status'] = self.status.value
        data['created_at'] = self.created_at.isoformat()
        if self.started_at:
            data['started_at'] = self.started_at.isoformat()
        if self.completed_at:
            data['completed_at'] = self.completed_at.isoformat()
        return data

class WorkflowEngine:
    """24시간 워크플로우 처리 엔진"""
    
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.workers: List[asyncio.Task] = []
        self.running = False
        self.task_handlers: Dict[str, Callable] = {}
        self.worker_count = 5  # 동시 처리 워커 수
        
        # 통계
        self.stats = {
            "total_tasks": 0,
            "completed_tasks": 0,
            "failed_tasks": 0,
            "retry_tasks": 0,
            "avg_processing_time": 0
        }
    
    def register_handler(self, task_type: str, handler: Callable):
        """작업 타입별 핸들러 등록"""
        self.task_handlers[task_type] = handler
        logger.info(f"Registered handler for task type: {task_type}")
    
    async def add_task(self, task: Task) -> str:
        """작업 추가"""
        self.tasks[task.id] = task
        await self.task_queue.put(task)
        self.stats["total_tasks"] += 1
        logger.info(f"Task added: {task.id} - {task.name}")
        return task.id
    
    async def process_task(self, task: Task) -> bool:
        """개별 작업 처리"""
        try:
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.now()
            
            # 작업 타입에 맞는 핸들러 실행
            handler = self.task_handlers.get(task.type)
            if not handler:
                raise ValueError(f"No handler for task type: {task.type}")
            
            # 핸들러 실행
            result = await handler(task.payload)
            
            # 성공 처리
            task.status = TaskStatus.SUCCESS
            task.result = result
            task.completed_at = datetime.now()
            self.stats["completed_tasks"] += 1
            
            logger.info(f"Task completed: {task.id}")
            return True
            
        except Exception as e:
            logger.error(f"Task failed: {task.id} - {str(e)}")
            task.error = str(e)
            
            # 재시도 로직
            if task.retry_count < task.max_retries:
                task.retry_count += 1
                task.status = TaskStatus.RETRY
                self.stats["retry_tasks"] += 1
                
                # 재시도 대기 (지수 백오프)
                await asyncio.sleep(2 ** task.retry_count)
                await self.task_queue.put(task)
                logger.info(f"Task retry scheduled: {task.id} (attempt {task.retry_count})")
            else:
                task.status = TaskStatus.FAILED
                task.completed_at = datetime.now()
                self.stats["failed_tasks"] += 1
                logger.error(f"Task permanently failed: {task.id}")
            
            return False
    
    async def worker(self, worker_id: int):
        """워커 프로세스 - 작업 처리"""
        logger.info(f"Worker {worker_id} started")
        
        while self.running:
            try:
                # 작업 대기 (타임아웃으로 주기적 체크)
                task = await asyncio.wait_for(
                    self.task_queue.get(),
                    timeout=1.0
                )
                
                logger.info(f"Worker {worker_id} processing task: {task.id}")
                await self.process_task(task)
                
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                logger.error(f"Worker {worker_id} error: {e}")
        
        logger.info(f"Worker {worker_id} stopped")
    
    async def start(self):
        """엔진 시작 - 24시간 실행"""
        if self.running:
            logger.warning("Engine already running")
            return
        
        self.running = True
        logger.info("Starting workflow engine...")
        
        # 워커 생성
        for i in range(self.worker_count):
            worker = asyncio.create_task(self.worker(i))
            self.workers.append(worker)
        
        logger.info(f"Started {self.worker_count} workers")
        
        # 상태 모니터링 시작
        asyncio.create_task(self.monitor())
    
    async def stop(self):
        """엔진 중지"""
        logger.info("Stopping workflow engine...")
        self.running = False
        
        # 모든 워커 종료 대기
        await asyncio.gather(*self.workers, return_exceptions=True)
        self.workers.clear()
        
        logger.info("Workflow engine stopped")
    
    async def monitor(self):
        """시스템 모니터링 - 5초마다"""
        while self.running:
            await asyncio.sleep(5)
            
            # 통계 출력
            queue_size = self.task_queue.qsize()
            running_tasks = sum(1 for t in self.tasks.values() if t.status == TaskStatus.RUNNING)
            
            logger.info(f"Stats - Queue: {queue_size}, Running: {running_tasks}, "
                       f"Completed: {self.stats['completed_tasks']}, "
                       f"Failed: {self.stats['failed_tasks']}")
    
    def get_task_status(self, task_id: str) -> Optional[Dict]:
        """작업 상태 조회"""
        task = self.tasks.get(task_id)
        if task:
            return task.to_dict()
        return None
    
    def get_stats(self) -> Dict:
        """통계 조회"""
        return {
            **self.stats,
            "queue_size": self.task_queue.qsize(),
            "active_workers": len(self.workers),
            "tasks_by_status": self._count_by_status()
        }
    
    def _count_by_status(self) -> Dict[str, int]:
        """상태별 작업 수 계산"""
        counts = {}
        for task in self.tasks.values():
            status = task.status.value
            counts[status] = counts.get(status, 0) + 1
        return counts

# 샘플 핸들러들
async def data_processing_handler(payload: Dict) -> Dict:
    """데이터 처리 핸들러 예시"""
    await asyncio.sleep(2)  # 처리 시뮬레이션
    return {"processed": True, "records": payload.get("count", 0)}

async def email_handler(payload: Dict) -> Dict:
    """이메일 발송 핸들러 예시"""
    await asyncio.sleep(1)
    return {"sent": True, "to": payload.get("recipient")}

async def backup_handler(payload: Dict) -> Dict:
    """백업 핸들러 예시"""
    await asyncio.sleep(3)
    return {"backed_up": True, "size": "100MB"}

# 엔진 인스턴스 생성
engine = WorkflowEngine()

# 기본 핸들러 등록
engine.register_handler("data_processing", data_processing_handler)
engine.register_handler("email", email_handler)
engine.register_handler("backup", backup_handler)