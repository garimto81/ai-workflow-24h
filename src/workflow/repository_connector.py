"""
Classic Isekai 저장소 연결 시스템
실제 웹소설 저장소에서 데이터를 가져오고 개선 결과를 푸시
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Optional
import aiohttp
import asyncio
from datetime import datetime

class ClassicIsekaiConnector:
    """Classic Isekai 저장소 연결자"""
    
    def __init__(self, github_token: Optional[str] = None):
        self.repo_owner = "garimto81"
        self.repo_name = "classic-isekai"
        self.repo_url = f"https://github.com/{self.repo_owner}/{self.repo_name}"
        self.api_url = f"https://api.github.com/repos/{self.repo_owner}/{self.repo_name}"
        self.episodes_path = "webnovel_episodes"
        # Private repo를 위한 토큰 우선순위: 인자 > CLASSIC_ISEKAI_TOKEN > GITHUB_TOKEN
        self.github_token = (github_token or 
                           os.environ.get('CLASSIC_ISEKAI_TOKEN') or 
                           os.environ.get('GITHUB_TOKEN'))
        self.local_path = Path("classic-isekai-workspace")
        
    async def setup_workspace(self) -> bool:
        """작업 공간 설정"""
        try:
            # 기존 작업 공간 삭제
            if self.local_path.exists():
                subprocess.run(["rm", "-rf", str(self.local_path)], check=True)
            
            # 저장소 클론
            clone_cmd = [
                "git", "clone",
                f"https://{self.github_token}@github.com/{self.repo_owner}/{self.repo_name}.git",
                str(self.local_path)
            ] if self.github_token else [
                "git", "clone",
                f"{self.repo_url}.git",
                str(self.local_path)
            ]
            
            subprocess.run(clone_cmd, check=True)
            print(f"✅ Classic Isekai 저장소 클론 완료: {self.local_path}")
            
            return True
        except Exception as e:
            print(f"❌ 저장소 클론 실패: {e}")
            return False
    
    async def fetch_episode_list(self) -> List[Dict[str, Any]]:
        """에피소드 목록 가져오기"""
        episodes = []
        
        # GitHub API로 파일 목록 가져오기
        headers = {
            'Accept': 'application/vnd.github.v3+json',
        }
        if self.github_token:
            headers['Authorization'] = f'token {self.github_token}'
        
        async with aiohttp.ClientSession() as session:
            url = f"{self.api_url}/contents/{self.episodes_path}"
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    files = await response.json()
                    
                    for file in files:
                        if file['name'].endswith('.md') and '에피소드' in file['name']:
                            # 에피소드 번호 추출
                            episode_num = self._extract_episode_number(file['name'])
                            if episode_num:
                                episodes.append({
                                    'number': episode_num,
                                    'filename': file['name'],
                                    'path': file['path'],
                                    'url': file['download_url'],
                                    'sha': file['sha']
                                })
                    
                    episodes.sort(key=lambda x: x['number'])
                    print(f"📚 {len(episodes)}개 에피소드 발견")
                else:
                    print(f"❌ API 요청 실패: {response.status}")
        
        return episodes
    
    async def fetch_episode_content(self, episode_number: int) -> Optional[str]:
        """특정 에피소드 내용 가져오기"""
        episodes = await self.fetch_episode_list()
        
        for episode in episodes:
            if episode['number'] == episode_number:
                async with aiohttp.ClientSession() as session:
                    async with session.get(episode['url']) as response:
                        if response.status == 200:
                            content = await response.text()
                            print(f"✅ {episode_number}화 내용 로드 완료")
                            return content
        
        print(f"❌ {episode_number}화를 찾을 수 없습니다")
        return None
    
    async def fetch_project_documents(self) -> Dict[str, str]:
        """프로젝트 문서들 가져오기"""
        documents = {}
        
        # 중요 문서 목록
        important_docs = [
            "README.md",
            "PROJECT_OVERVIEW.md",
            "WORLDBUILDING_RULES.md",
            "world_setting/000_INDEX.md",
            "world_setting/001_world_overview.md",
            "world_setting/021_resonance_system.md",
            "world_setting/100_protagonist.md",
            "world_setting/110_story_bible.md",
            "docs/episode_guide.md"
        ]
        
        async with aiohttp.ClientSession() as session:
            for doc_path in important_docs:
                url = f"{self.api_url}/contents/{doc_path}"
                headers = {'Accept': 'application/vnd.github.v3+json'}
                if self.github_token:
                    headers['Authorization'] = f'token {self.github_token}'
                
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        content_url = data.get('download_url')
                        if content_url:
                            async with session.get(content_url) as content_response:
                                if content_response.status == 200:
                                    documents[doc_path] = await content_response.text()
                                    print(f"📄 문서 로드: {doc_path}")
        
        print(f"📚 총 {len(documents)}개 문서 로드 완료")
        return documents
    
    async def save_improved_episode(self, episode_number: int, improved_content: str, 
                                   commit_message: str = None) -> bool:
        """개선된 에피소드 저장 및 커밋"""
        if not self.local_path.exists():
            await self.setup_workspace()
        
        # 파일 경로 찾기
        episodes = await self.fetch_episode_list()
        target_episode = None
        
        for episode in episodes:
            if episode['number'] == episode_number:
                target_episode = episode
                break
        
        if not target_episode:
            print(f"❌ {episode_number}화를 찾을 수 없습니다")
            return False
        
        # 파일 저장
        file_path = self.local_path / target_episode['path']
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(improved_content)
        
        print(f"💾 {episode_number}화 파일 저장: {file_path}")
        
        # Git 커밋 및 푸시
        try:
            os.chdir(self.local_path)
            
            # Git 설정
            subprocess.run(["git", "config", "user.name", "AI Workflow Bot"], check=True)
            subprocess.run(["git", "config", "user.email", "bot@ai-workflow.com"], check=True)
            
            # 변경사항 추가
            subprocess.run(["git", "add", str(target_episode['path'])], check=True)
            
            # 커밋
            if not commit_message:
                commit_message = f"Auto: Improve episode {episode_number} - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            
            subprocess.run(["git", "commit", "-m", commit_message], check=True)
            
            # 푸시
            subprocess.run(["git", "push"], check=True)
            
            print(f"✅ {episode_number}화 개선 사항 푸시 완료")
            return True
            
        except Exception as e:
            print(f"❌ Git 작업 실패: {e}")
            return False
    
    def _extract_episode_number(self, filename: str) -> Optional[int]:
        """파일명에서 에피소드 번호 추출 - webnovel_episodes 폴더용"""
        import re
        
        # webnovel_episodes 폴더의 실제 파일명 패턴들
        patterns = [
            r'(\d+)화',                    # "1화", "2화" 등
            r'에피소드[_\s]*(\d+)',         # "에피소드_1", "에피소드 1" 등  
            r'^(\d+)[_-]',                 # "001_", "1-" 등으로 시작
            r'[Ee]pisode[_\s]*(\d+)',      # "Episode_1", "episode 1" 등
            r'[Cc]hapter[_\s]*(\d+)',      # "Chapter_1", "chapter 1" 등
            r'제(\d+)화',                  # "제1화", "제2화" 등
        ]
        
        for pattern in patterns:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                num = int(match.group(1))
                if 1 <= num <= 100:  # 에피소드 번호 범위 제한
                    return num
        
        return None
    
    async def create_pull_request(self, branch_name: str, title: str, body: str) -> Dict[str, Any]:
        """Pull Request 생성"""
        if not self.github_token:
            print("❌ GitHub 토큰이 필요합니다")
            return {}
        
        # 브랜치 생성
        try:
            os.chdir(self.local_path)
            subprocess.run(["git", "checkout", "-b", branch_name], check=True)
            subprocess.run(["git", "push", "-u", "origin", branch_name], check=True)
        except Exception as e:
            print(f"❌ 브랜치 생성 실패: {e}")
            return {}
        
        # PR 생성 (GitHub API)
        async with aiohttp.ClientSession() as session:
            url = f"{self.api_url}/pulls"
            headers = {
                'Authorization': f'token {self.github_token}',
                'Accept': 'application/vnd.github.v3+json'
            }
            data = {
                'title': title,
                'body': body,
                'head': branch_name,
                'base': 'master'
            }
            
            async with session.post(url, headers=headers, json=data) as response:
                if response.status == 201:
                    pr_data = await response.json()
                    print(f"✅ PR 생성 완료: {pr_data['html_url']}")
                    return pr_data
                else:
                    print(f"❌ PR 생성 실패: {response.status}")
                    return {}


class EpisodeValidator:
    """에피소드 검증 시스템"""
    
    def __init__(self, connector: ClassicIsekaiConnector):
        self.connector = connector
        self.validation_rules = {}
        
    async def validate_episode(self, episode_number: int) -> Dict[str, Any]:
        """에피소드 검증"""
        content = await self.connector.fetch_episode_content(episode_number)
        if not content:
            return {'valid': False, 'error': '에피소드를 찾을 수 없음'}
        
        validation_results = {
            'episode_number': episode_number,
            'valid': True,
            'checks': {}
        }
        
        # 1. 길이 체크
        word_count = len(content)
        validation_results['checks']['length'] = {
            'value': word_count,
            'min': 5000,
            'max': 10000,
            'passed': 5000 <= word_count <= 10000
        }
        
        # 2. 구조 체크
        has_title = '제' in content[:100] and '화' in content[:100]
        validation_results['checks']['structure'] = {
            'has_title': has_title,
            'passed': has_title
        }
        
        # 3. 세계관 일관성 체크
        required_terms = ['공명력', 'Resonance']
        found_terms = [term for term in required_terms if term in content]
        validation_results['checks']['worldbuilding'] = {
            'required_terms': required_terms,
            'found_terms': found_terms,
            'passed': len(found_terms) > 0
        }
        
        # 4. 캐릭터 체크
        # 주인공 이름은 실제 스토리에 맞게 수정 필요
        # TODO: 실제 주인공 이름으로 변경
        main_character = ''  # 주인공 이름 (저장소 확인 후 설정)
        if main_character:
            validation_results['checks']['character'] = {
                'main_character_mentioned': main_character in content,
                'passed': main_character in content
            }
        
        # 전체 유효성
        validation_results['valid'] = all(
            check.get('passed', True) 
            for check in validation_results['checks'].values()
        )
        
        return validation_results
    
    async def validate_all_episodes(self) -> Dict[str, Any]:
        """모든 에피소드 검증"""
        episodes = await self.connector.fetch_episode_list()
        
        results = {
            'total_episodes': len(episodes),
            'valid_episodes': 0,
            'invalid_episodes': 0,
            'details': []
        }
        
        for episode in episodes:
            validation = await self.validate_episode(episode['number'])
            results['details'].append(validation)
            
            if validation['valid']:
                results['valid_episodes'] += 1
            else:
                results['invalid_episodes'] += 1
        
        results['validation_rate'] = (
            results['valid_episodes'] / results['total_episodes'] * 100
            if results['total_episodes'] > 0 else 0
        )
        
        return results


# 사용 예제
async def main():
    # 연결자 초기화
    connector = ClassicIsekaiConnector()
    
    # 작업 공간 설정
    await connector.setup_workspace()
    
    # 에피소드 목록 가져오기
    episodes = await connector.fetch_episode_list()
    print(f"발견된 에피소드: {[ep['number'] for ep in episodes]}")
    
    # 1화 내용 가져오기
    content = await connector.fetch_episode_content(1)
    if content:
        print(f"1화 길이: {len(content)}자")
    
    # 프로젝트 문서 가져오기
    docs = await connector.fetch_project_documents()
    print(f"로드된 문서: {list(docs.keys())}")
    
    # 검증
    validator = EpisodeValidator(connector)
    validation = await validator.validate_episode(1)
    print(f"1화 검증 결과: {validation}")


if __name__ == "__main__":
    asyncio.run(main())