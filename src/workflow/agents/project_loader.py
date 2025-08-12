"""
Classic Isekai 프로젝트 로더
기존 프로젝트의 문서들을 읽고 각 에이전트에게 필요한 정보 제공
"""

import os
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
import json

logger = logging.getLogger(__name__)


class ProjectDocumentLoader:
    """프로젝트 문서 로더 및 관리자"""
    
    def __init__(self, config_path: str = "config/classic_isekai_project.yaml"):
        self.config = self.load_config(config_path)
        self.base_path = Path(self.config['project']['base_path'])
        self.documents = {}
        self.episode_cache = {}
        
    def load_config(self, config_path: str) -> Dict:
        """설정 파일 로드"""
        with open(config_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    async def initialize_project(self):
        """프로젝트 초기화 및 문서 로드"""
        logger.info("Classic Isekai 프로젝트 초기화 시작")
        
        # 기본 문서들 로드
        await self.load_core_documents()
        
        # 에피소드 목록 스캔
        await self.scan_episodes()
        
        # 세계관 문서들 로드
        await self.load_worldbuilding_documents()
        
        logger.info("프로젝트 초기화 완료")
    
    async def load_core_documents(self):
        """핵심 문서들 로드"""
        core_files = [
            "PROJECT_OVERVIEW.md",
            "WORLDBUILDING_RULES.md", 
            "CLAUDE.md",
            "README.md"
        ]
        
        for filename in core_files:
            file_path = self.base_path / filename
            if file_path.exists():
                content = self.read_file(file_path)
                self.documents[filename] = content
                logger.info(f"로드됨: {filename}")
    
    async def scan_episodes(self):
        """에피소드 파일들 스캔"""
        episodes_dir = self.base_path / self.config['project']['universes']['terra_antica']['episodes_path']
        
        if not episodes_dir.exists():
            logger.warning(f"에피소드 디렉토리를 찾을 수 없음: {episodes_dir}")
            return
        
        episode_files = []
        for file_path in episodes_dir.glob("제*화_*.md"):
            episode_info = {
                'path': str(file_path),
                'filename': file_path.name,
                'size': file_path.stat().st_size,
                'episode_number': self.extract_episode_number(file_path.name)
            }
            episode_files.append(episode_info)
        
        # 에피소드 번호 순으로 정렬
        episode_files.sort(key=lambda x: x['episode_number'])
        
        self.documents['episodes_list'] = episode_files
        logger.info(f"에피소드 {len(episode_files)}개 발견")
    
    def extract_episode_number(self, filename: str) -> int:
        """파일명에서 에피소드 번호 추출"""
        try:
            # "제1화_학살의_밤.md" -> 1
            import re
            match = re.search(r'제(\d+)화', filename)
            if match:
                return int(match.group(1))
        except:
            pass
        return 0
    
    async def load_worldbuilding_documents(self):
        """세계관 문서들 로드"""
        world_setting_dir = self.base_path / "world_setting"
        
        if not world_setting_dir.exists():
            logger.warning("world_setting 디렉토리를 찾을 수 없음")
            return
        
        # 중요한 세계관 문서들 우선 로드
        priority_files = [
            "000_INDEX.md",
            "010_overview.md",
            "011_terra_antica_system.md",
            "021_resonance_system.md",
            "100_protagonist.md",
            "101_main_characters.md",
            "110_story_bible.md"
        ]
        
        for filename in priority_files:
            file_path = world_setting_dir / filename
            if file_path.exists():
                content = self.read_file(file_path)
                self.documents[f"world_setting/{filename}"] = content
        
        logger.info("세계관 문서 로드 완료")
    
    def read_file(self, file_path: Path) -> str:
        """파일 읽기"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except UnicodeDecodeError:
            # UTF-8 실패시 다른 인코딩 시도
            try:
                with open(file_path, 'r', encoding='cp949') as f:
                    return f.read()
            except:
                logger.error(f"파일 읽기 실패: {file_path}")
                return ""
        except Exception as e:
            logger.error(f"파일 읽기 오류 {file_path}: {e}")
            return ""
    
    def get_agent_documents(self, agent_name: str) -> Dict[str, str]:
        """특정 에이전트가 읽어야 할 문서들 반환"""
        agent_config = self.config['agent_documents'].get(agent_name, {})
        agent_docs = {}
        
        # 각 카테고리별 문서들 로드
        for category, file_list in agent_config.items():
            if isinstance(file_list, list):
                for filename in file_list:
                    # 전체 경로 또는 상대 경로 처리
                    if filename.endswith('/'):
                        # 디렉토리 전체
                        dir_docs = self.get_directory_documents(filename)
                        agent_docs.update(dir_docs)
                    else:
                        # 개별 파일
                        full_path = self.resolve_file_path(filename)
                        if full_path and full_path.exists():
                            content = self.read_file(full_path)
                            agent_docs[filename] = content
        
        logger.info(f"{agent_name} 에이전트: {len(agent_docs)}개 문서 로드")
        return agent_docs
    
    def resolve_file_path(self, filename: str) -> Optional[Path]:
        """파일 경로 해석"""
        # 이미 로드된 문서에서 찾기
        if filename in self.documents:
            return None  # 캐시된 내용 사용
        
        # 절대 경로인 경우
        if filename.startswith('/') or filename.startswith('C:'):
            return Path(filename)
        
        # 상대 경로인 경우
        full_path = self.base_path / filename
        if full_path.exists():
            return full_path
        
        return None
    
    def get_directory_documents(self, dirname: str) -> Dict[str, str]:
        """디렉토리 내 모든 문서 반환"""
        dir_path = self.base_path / dirname.rstrip('/')
        docs = {}
        
        if dir_path.exists() and dir_path.is_dir():
            for file_path in dir_path.glob("*.md"):
                content = self.read_file(file_path)
                docs[f"{dirname}{file_path.name}"] = content
        
        return docs
    
    def get_episode_content(self, episode_number: int) -> Optional[str]:
        """특정 에피소드 내용 반환"""
        if episode_number in self.episode_cache:
            return self.episode_cache[episode_number]
        
        # 에피소드 파일 찾기
        episodes_list = self.documents.get('episodes_list', [])
        for episode_info in episodes_list:
            if episode_info['episode_number'] == episode_number:
                content = self.read_file(Path(episode_info['path']))
                self.episode_cache[episode_number] = content
                return content
        
        return None
    
    def get_all_episodes(self) -> Dict[int, str]:
        """모든 에피소드 내용 반환"""
        all_episodes = {}
        episodes_list = self.documents.get('episodes_list', [])
        
        for episode_info in episodes_list:
            episode_num = episode_info['episode_number']
            if episode_num not in self.episode_cache:
                content = self.read_file(Path(episode_info['path']))
                self.episode_cache[episode_num] = content
            
            all_episodes[episode_num] = self.episode_cache[episode_num]
        
        return all_episodes
    
    def get_project_summary(self) -> Dict[str, Any]:
        """프로젝트 요약 정보 반환"""
        episodes_list = self.documents.get('episodes_list', [])
        
        summary = {
            'project_name': self.config['project']['name'],
            'universe': self.config['project']['current_universe'],
            'total_episodes': len(episodes_list),
            'completed_episodes': self.config['episode_processing']['current_status']['completed'],
            'available_documents': list(self.documents.keys()),
            'worldbuilding_files_count': len([k for k in self.documents.keys() if k.startswith('world_setting/')]),
            'base_path': str(self.base_path)
        }
        
        return summary
    
    def update_episode_status(self, episode_number: int, status: str):
        """에피소드 상태 업데이트"""
        status_config = self.config['episode_processing']['current_status']
        
        # 모든 상태에서 제거
        for status_list in status_config.values():
            if episode_number in status_list:
                status_list.remove(episode_number)
        
        # 새 상태에 추가
        if status in status_config:
            if episode_number not in status_config[status]:
                status_config[status].append(episode_number)
                status_config[status].sort()
    
    def get_next_episode_to_review(self) -> Optional[int]:
        """다음 검토할 에피소드 번호 반환"""
        completed = set(self.config['episode_processing']['current_status']['completed'])
        in_review = set(self.config['episode_processing']['current_status']['in_review'])
        
        episodes_list = self.documents.get('episodes_list', [])
        available_episodes = set(ep['episode_number'] for ep in episodes_list)
        
        # 완료되지 않고 검토 중이 아닌 에피소드 중 가장 작은 번호
        candidates = available_episodes - completed - in_review
        
        if candidates:
            return min(candidates)
        
        return None
    
    def save_project_state(self):
        """프로젝트 상태 저장"""
        state_file = Path("memory/project_state.json")
        state_file.parent.mkdir(exist_ok=True)
        
        state = {
            'episode_status': self.config['episode_processing']['current_status'],
            'last_updated': str(Path().cwd()),
            'cache_info': {
                'episodes_cached': list(self.episode_cache.keys()),
                'documents_loaded': list(self.documents.keys())
            }
        }
        
        with open(state_file, 'w', encoding='utf-8') as f:
            json.dump(state, f, ensure_ascii=False, indent=2)


# 싱글톤 인스턴스
project_loader = ProjectDocumentLoader()