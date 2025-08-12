"""
FastAPI 메인 애플리케이션 - 24시간 AI 워크플로우 시스템
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
from datetime import datetime
import asyncio
import logging

from src.workflow.engine import WorkflowEngine, Task, TaskStatus, TaskPriority
from src.ai.free_models import ai_manager, TaskPrioritizer

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(
    title="AI Workflow 24H",
    description="24시간 무중단 AI 워크플로우 자동화 시스템",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 워크플로우 엔진
workflow_engine = WorkflowEngine()
task_prioritizer = TaskPrioritizer(ai_manager)

# Pydantic 모델
class TaskCreate(BaseModel):
    name: str
    type: str
    payload: Dict[str, Any]
    priority: Optional[int] = TaskPriority.NORMAL.value

class TaskResponse(BaseModel):
    id: str
    status: str
    message: str

# 시작 이벤트
@app.on_event("startup")
async def startup_event():
    """앱 시작시 워크플로우 엔진 시작"""
    await workflow_engine.start()
    logger.info("AI Workflow system started - Running 24/7")

# 종료 이벤트
@app.on_event("shutdown")
async def shutdown_event():
    """앱 종료시 정리"""
    await workflow_engine.stop()
    logger.info("AI Workflow system stopped")

# 헬스체크
@app.get("/health")
async def health_check():
    """시스템 상태 확인"""
    stats = workflow_engine.get_stats()
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "engine_running": workflow_engine.running,
        "stats": stats
    }

# 작업 생성
@app.post("/tasks", response_model=TaskResponse)
async def create_task(task_data: TaskCreate):
    """새 작업 생성"""
    try:
        # AI로 우선순위 분석 (선택적)
        if task_data.priority == TaskPriority.NORMAL.value:
            analysis = ai_manager.analyze_task({
                "name": task_data.name,
                "type": task_data.type,
                "payload": task_data.payload
            })
            task_data.priority = analysis.get("priority", 5)
        
        # 작업 생성
        task = Task(
            id="",
            name=task_data.name,
            type=task_data.type,
            payload=task_data.payload,
            priority=task_data.priority
        )
        
        # 작업 추가
        task_id = await workflow_engine.add_task(task)
        
        return TaskResponse(
            id=task_id,
            status="created",
            message=f"Task {task_id} created successfully"
        )
    
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 작업 상태 조회
@app.get("/tasks/{task_id}")
async def get_task(task_id: str):
    """작업 상태 조회"""
    task_status = workflow_engine.get_task_status(task_id)
    if not task_status:
        raise HTTPException(status_code=404, detail="Task not found")
    return task_status

# 작업 목록 조회
@app.get("/tasks")
async def list_tasks(status: Optional[str] = None, limit: int = 100):
    """작업 목록 조회"""
    tasks = []
    for task in workflow_engine.tasks.values():
        if status and task.status.value != status:
            continue
        tasks.append(task.to_dict())
        if len(tasks) >= limit:
            break
    
    return {
        "total": len(workflow_engine.tasks),
        "tasks": tasks
    }

# 통계 조회
@app.get("/stats")
async def get_stats():
    """시스템 통계"""
    return workflow_engine.get_stats()

# AI 분석
@app.post("/analyze")
async def analyze_task(data: Dict[str, Any]):
    """AI를 사용한 작업 분석"""
    try:
        result = ai_manager.analyze_task(data)
        return result
    except Exception as e:
        logger.error(f"Analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# 대량 작업 생성 (테스트용)
@app.post("/tasks/bulk")
async def create_bulk_tasks(count: int = 10, task_type: str = "data_processing"):
    """테스트용 대량 작업 생성"""
    created_tasks = []
    
    for i in range(count):
        task = Task(
            id="",
            name=f"Bulk Task {i+1}",
            type=task_type,
            payload={"index": i, "count": 100},
            priority=TaskPriority.NORMAL.value
        )
        task_id = await workflow_engine.add_task(task)
        created_tasks.append(task_id)
    
    return {
        "message": f"Created {count} tasks",
        "task_ids": created_tasks
    }

# 워크플로우 일시정지/재개
@app.post("/engine/pause")
async def pause_engine():
    """엔진 일시정지"""
    workflow_engine.running = False
    return {"status": "paused"}

@app.post("/engine/resume")
async def resume_engine():
    """엔진 재개"""
    workflow_engine.running = True
    return {"status": "resumed"}

# 루트 경로
@app.get("/")
async def root():
    """API 정보"""
    return {
        "name": "AI Workflow 24H",
        "version": "1.0.0",
        "status": "running" if workflow_engine.running else "stopped",
        "docs": "/docs",
        "health": "/health",
        "description": "24/7 AI-powered workflow automation system"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )