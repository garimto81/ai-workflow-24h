"""
메인 오케스트레이터 에이전트
전체 워크플로우를 관리하고 작업을 각 에이전트에게 할당
"""

import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging

from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class FileChangeHandler(FileSystemEventHandler):
    """파일 변경 감지 핸들러"""
    
    def __init__(self, callback):
        self.callback = callback
        self.last_modified = {}
    
    def on_modified(self, event):
        if event.is_directory:
            return
        
        # 중복 이벤트 방지 (1초 이내 재발생 무시)
        current_time = datetime.now()
        if event.src_path in self.last_modified:
            if (current_time - self.last_modified[event.src_path]).total_seconds() < 1:
                return
        
        self.last_modified[event.src_path] = current_time
        
        # 콜백 실행
        asyncio.create_task(self.callback(event.src_path))
    
    def on_created(self, event):
        if not event.is_directory:
            asyncio.create_task(self.callback(event.src_path))


class MainAgent(BaseAgent):
    """메인 오케스트레이터 에이전트"""
    
    def __init__(self):
        super().__init__("MainOrchestrator")
        
        # 에이전트 맵
        self.agents = {
            "pm": None,
            "writer": None,
            "worldbuilding": None,
            "history": None,
            "history_improver": None,
            "grammar": None,
            "ai_detection": None,
            "readers": [],
            "qa": None
        }
        
        # 작업 큐
        self.task_queue = asyncio.Queue()
        self.pending_tasks = {}
        self.completed_tasks = {}
        
        # 파일 감시 설정
        self.file_observer = None
        self.watch_directory = Path(self.config['filesystem']['watch_directory'])
        self.watch_directory.mkdir(parents=True, exist_ok=True)
        
        # 워크플로우 상태
        self.workflow_status = "idle"
        self.current_episode = None
        
    def register_agent(self, agent_type: str, agent_instance):
        """에이전트 등록"""
        if agent_type == "readers":
            self.agents["readers"].append(agent_instance)
        else:
            self.agents[agent_type] = agent_instance
        logger.info(f"{agent_type} 에이전트 등록 완료")
    
    async def file_changed(self, file_path: str):
        """파일 변경 감지시 처리"""
        logger.info(f"파일 변경 감지: {file_path}")
        
        # 파일 읽기
        content = await self.read_file(file_path)
        
        # 작업 유형 판단
        task_type = await self.analyze_content(content, file_path)
        
        # 작업 생성 및 큐에 추가
        task = {
            "id": f"task_{datetime.now().timestamp()}",
            "type": task_type,
            "file_path": file_path,
            "content": content,
            "created_at": datetime.now().isoformat()
        }
        
        await self.task_queue.put(task)
        logger.info(f"작업 생성: {task['id']} ({task_type})")
    
    async def read_file(self, file_path: str) -> str:
        """파일 읽기"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"파일 읽기 실패: {e}")
            return ""
    
    async def analyze_content(self, content: str, file_path: str) -> str:
        """내용 분석하여 작업 유형 결정"""
        
        # 파일 경로로 유형 판단
        file_path = Path(file_path)
        
        if "draft" in file_path.stem.lower():
            return "new_episode"
        elif "revision" in file_path.stem.lower():
            return "revision"
        elif "feedback" in file_path.stem.lower():
            return "feedback_integration"
        else:
            # Claude를 사용한 자동 판단
            prompt = f"""
            다음 문서의 유형을 판단해주세요:
            
            {content[:1000]}
            
            가능한 유형:
            - new_episode: 새로운 에피소드
            - revision: 수정 요청
            - worldbuilding: 세계관 설정
            - character: 캐릭터 설정
            
            응답 형식: 유형만 단어로
            """
            
            response = await self.call_claude(prompt, max_tokens=10)
            return response.strip().lower()
    
    async def process_new_episode(self, task: Dict[str, Any]):
        """새 에피소드 처리 파이프라인"""
        episode_id = task['id']
        content = task['content']
        
        logger.info(f"새 에피소드 처리 시작: {episode_id}")
        
        # 1. 작가 에이전트에게 전달 (내용이 이미 있으면 스킵)
        if not content or len(content) < 100:
            writer_task = {
                "type": "create_episode",
                "previous_content": self.get_previous_episode()
            }
            writer_result = await self.delegate_task("writer", writer_task)
            content = writer_result.get('result', content)
        
        # 2. 세계관 검증
        world_task = {
            "type": "verify_worldbuilding",
            "content": content
        }
        world_result = await self.delegate_task("worldbuilding", world_task)
        
        # 3. 역사 검증
        history_task = {
            "type": "verify_history",
            "content": content
        }
        history_result = await self.delegate_task("history", history_task)
        
        # 4. 역사 개선 판단
        if history_result.get('conflicts'):
            improve_task = {
                "type": "improve_history",
                "content": content,
                "conflicts": history_result['conflicts']
            }
            improve_result = await self.delegate_task("history_improver", improve_task)
            
            if improve_result.get('history_updated'):
                # 역사가 수정되면 다시 검증
                history_result = await self.delegate_task("history", history_task)
        
        # 5. 문법 검사
        grammar_task = {
            "type": "check_grammar",
            "content": content
        }
        grammar_result = await self.delegate_task("grammar", grammar_task)
        
        # 6. AI 화법 검사
        ai_detect_task = {
            "type": "detect_ai_patterns",
            "content": content
        }
        ai_result = await self.delegate_task("ai_detection", ai_detect_task)
        
        # 7. 독자 평가 (병렬 처리)
        reader_tasks = []
        for i, reader in enumerate(self.agents['readers']):
            reader_task = {
                "type": "review_episode",
                "content": content,
                "reader_id": i
            }
            reader_tasks.append(self.delegate_task(f"reader_{i}", reader_task))
        
        reader_results = await asyncio.gather(*reader_tasks)
        
        # 8. QA 최종 검증
        qa_task = {
            "type": "final_validation",
            "content": content,
            "validations": {
                "worldbuilding": world_result,
                "history": history_result,
                "grammar": grammar_result,
                "ai_detection": ai_result,
                "reader_reviews": reader_results
            }
        }
        qa_result = await self.delegate_task("qa", qa_task)
        
        # 9. 결과 종합
        final_result = {
            "episode_id": episode_id,
            "status": "completed" if qa_result.get('passed') else "needs_revision",
            "score": qa_result.get('score', 0),
            "content": content,
            "feedback": self.compile_feedback(
                world_result, history_result, grammar_result, 
                ai_result, reader_results, qa_result
            ),
            "timestamp": datetime.now().isoformat()
        }
        
        # 10. 결과 저장
        await self.save_result(final_result)
        
        logger.info(f"에피소드 처리 완료: {episode_id} (점수: {final_result['score']})")
        
        return final_result
    
    async def delegate_task(self, agent_type: str, task: Dict[str, Any]) -> Dict[str, Any]:
        """특정 에이전트에게 작업 위임"""
        logger.info(f"작업 위임: {agent_type} ← {task['type']}")
        
        # 실제 구현시 메시지 큐를 통해 전달
        # 여기서는 시뮬레이션
        result = {
            "agent": agent_type,
            "task": task['type'],
            "status": "completed",
            "result": f"{agent_type} 처리 완료"
        }
        
        # PM 에이전트에게 상태 보고
        await self.report_to_pm(agent_type, task, result)
        
        return result
    
    async def report_to_pm(self, agent_type: str, task: Dict, result: Dict):
        """PM 에이전트에게 진행 상황 보고"""
        pm_report = {
            "type": "status_update",
            "agent": agent_type,
            "task": task,
            "result": result,
            "timestamp": datetime.now().isoformat()
        }
        
        # PM에게 전송
        if self.agents['pm']:
            await self.send_message("pm", pm_report)
    
    def compile_feedback(self, *results) -> List[Dict]:
        """모든 피드백 종합"""
        feedback = []
        
        for result in results:
            if isinstance(result, list):
                feedback.extend(result)
            elif isinstance(result, dict) and result.get('feedback'):
                feedback.append(result['feedback'])
        
        return feedback
    
    def get_previous_episode(self) -> str:
        """이전 에피소드 가져오기"""
        episodes_dir = Path(self.config['filesystem']['directories']['episodes'])
        
        if episodes_dir.exists():
            episodes = sorted(episodes_dir.glob("*.txt"))
            if episodes:
                with open(episodes[-1], 'r', encoding='utf-8') as f:
                    return f.read()
        
        return ""
    
    async def save_result(self, result: Dict):
        """결과 저장"""
        output_dir = Path(self.config['filesystem']['output_directory'])
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # 에피소드 저장
        if result['status'] == 'completed':
            episode_file = output_dir / f"episode_{result['episode_id']}.txt"
            with open(episode_file, 'w', encoding='utf-8') as f:
                f.write(result['content'])
        
        # 메타데이터 저장
        meta_file = output_dir / f"meta_{result['episode_id']}.json"
        with open(meta_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    
    def start_file_watcher(self):
        """파일 감시 시작"""
        self.file_observer = Observer()
        handler = FileChangeHandler(self.file_changed)
        self.file_observer.schedule(
            handler, 
            str(self.watch_directory), 
            recursive=True
        )
        self.file_observer.start()
        logger.info(f"파일 감시 시작: {self.watch_directory}")
    
    def stop_file_watcher(self):
        """파일 감시 중지"""
        if self.file_observer:
            self.file_observer.stop()
            self.file_observer.join()
            logger.info("파일 감시 중지")
    
    async def execute(self, task: Dict[str, Any]) -> Any:
        """메인 에이전트 실행"""
        task_type = task.get('type')
        
        if task_type == 'new_episode':
            return await self.process_new_episode(task)
        elif task_type == 'revision':
            return await self.process_revision(task)
        else:
            logger.warning(f"알 수 없는 작업 유형: {task_type}")
            return {"status": "unknown_task_type"}
    
    async def process_revision(self, task: Dict[str, Any]):
        """수정 작업 처리"""
        # 구현 예정
        pass
    
    async def run(self):
        """메인 에이전트 실행"""
        logger.info("메인 오케스트레이터 시작")
        
        # 파일 감시 시작
        if self.config['workflow']['mode'] == 'file_watch':
            self.start_file_watcher()
        
        try:
            while True:
                # 작업 큐 확인
                try:
                    task = await asyncio.wait_for(
                        self.task_queue.get(), 
                        timeout=1.0
                    )
                    
                    # 작업 처리
                    result = await self.execute(task)
                    
                    # 완료 작업 저장
                    self.completed_tasks[task['id']] = result
                    
                except asyncio.TimeoutError:
                    pass
                
                # 상태 업데이트
                await self.update_status()
                
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("메인 오케스트레이터 종료")
        finally:
            self.stop_file_watcher()