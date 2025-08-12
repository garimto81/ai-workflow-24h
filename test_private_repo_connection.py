#!/usr/bin/env python3
"""
테스트 스크립트: Classic Isekai Private 저장소 연결 테스트
이 스크립트는 PAT 토큰을 사용하여 private 저장소에 접근할 수 있는지 확인합니다.
"""

import os
import sys
import asyncio
import aiohttp
from pathlib import Path

# 프로젝트 경로 추가
sys.path.append('src/workflow')

from repository_connector import ClassicIsekaiConnector, EpisodeValidator


async def test_private_repo_connection():
    """Private 저장소 연결 테스트"""
    
    print("=" * 60)
    print("🔐 Classic Isekai Private 저장소 연결 테스트")
    print("=" * 60)
    
    # 1. 환경 변수 확인
    print("\n1️⃣ 환경 변수 확인")
    print("-" * 40)
    
    tokens = {
        'CLASSIC_ISEKAI_TOKEN': os.environ.get('CLASSIC_ISEKAI_TOKEN'),
        'GITHUB_TOKEN': os.environ.get('GITHUB_TOKEN'),
        'ANTHROPIC_API_KEY': os.environ.get('ANTHROPIC_API_KEY')
    }
    
    for name, value in tokens.items():
        if value:
            masked = value[:4] + "*" * (len(value) - 8) + value[-4:] if len(value) > 8 else "*" * len(value)
            print(f"✅ {name}: {masked}")
        else:
            print(f"❌ {name}: Not set")
    
    # 2. Repository Connector 초기화
    print("\n2️⃣ Repository Connector 초기화")
    print("-" * 40)
    
    try:
        connector = ClassicIsekaiConnector()
        print(f"✅ Connector 생성 완료")
        print(f"   - Owner: {connector.repo_owner}")
        print(f"   - Repo: {connector.repo_name}")
        print(f"   - Token: {'설정됨' if connector.github_token else '없음'}")
    except Exception as e:
        print(f"❌ Connector 생성 실패: {e}")
        return False
    
    # 3. API 접근 테스트
    print("\n3️⃣ GitHub API 접근 테스트")
    print("-" * 40)
    
    try:
        # 저장소 정보 가져오기
        headers = {'Accept': 'application/vnd.github.v3+json'}
        if connector.github_token:
            headers['Authorization'] = f'token {connector.github_token}'
        
        async with aiohttp.ClientSession() as session:
            url = f"https://api.github.com/repos/{connector.repo_owner}/{connector.repo_name}"
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    repo_data = await response.json()
                    print(f"✅ 저장소 접근 성공")
                    print(f"   - Name: {repo_data.get('name')}")
                    print(f"   - Private: {repo_data.get('private')}")
                    print(f"   - Description: {repo_data.get('description', 'No description')}")
                    print(f"   - Default Branch: {repo_data.get('default_branch')}")
                elif response.status == 404:
                    print(f"❌ 저장소를 찾을 수 없음 (404)")
                    print(f"   - 저장소가 private이고 토큰이 없거나 권한이 부족할 수 있습니다")
                    return False
                elif response.status == 401:
                    print(f"❌ 인증 실패 (401)")
                    print(f"   - 토큰이 유효하지 않거나 만료되었습니다")
                    return False
                else:
                    print(f"❌ API 요청 실패: {response.status}")
                    text = await response.text()
                    print(f"   - Response: {text[:200]}")
                    return False
    except Exception as e:
        print(f"❌ API 테스트 실패: {e}")
        return False
    
    # 4. 에피소드 목록 가져오기
    print("\n4️⃣ 에피소드 목록 가져오기")
    print("-" * 40)
    
    try:
        episodes = await connector.fetch_episode_list()
        if episodes:
            print(f"✅ {len(episodes)}개 에피소드 발견")
            for ep in episodes[:3]:  # 처음 3개만 표시
                print(f"   - {ep['number']}화: {ep['filename']}")
        else:
            print(f"⚠️ 에피소드를 찾을 수 없음")
            print(f"   - webnovel_episodes 폴더가 없거나 비어있을 수 있습니다")
    except Exception as e:
        print(f"❌ 에피소드 목록 가져오기 실패: {e}")
        return False
    
    # 5. 프로젝트 문서 가져오기
    print("\n5️⃣ 프로젝트 문서 접근 테스트")
    print("-" * 40)
    
    try:
        docs = await connector.fetch_project_documents()
        if docs:
            print(f"✅ {len(docs)}개 문서 로드 완료")
            for doc_path in list(docs.keys())[:3]:  # 처음 3개만 표시
                print(f"   - {doc_path}")
        else:
            print(f"⚠️ 문서를 찾을 수 없음")
    except Exception as e:
        print(f"❌ 문서 가져오기 실패: {e}")
        return False
    
    # 6. 에피소드 내용 가져오기 (1화)
    print("\n6️⃣ 에피소드 내용 접근 테스트 (1화)")
    print("-" * 40)
    
    try:
        content = await connector.fetch_episode_content(1)
        if content:
            print(f"✅ 1화 내용 로드 성공")
            print(f"   - 길이: {len(content)}자")
            print(f"   - 시작: {content[:50]}...")
        else:
            print(f"⚠️ 1화 내용을 가져올 수 없음")
    except Exception as e:
        print(f"❌ 에피소드 내용 가져오기 실패: {e}")
        return False
    
    # 7. 검증 시스템 테스트
    print("\n7️⃣ 에피소드 검증 시스템 테스트")
    print("-" * 40)
    
    try:
        validator = EpisodeValidator(connector)
        validation = await validator.validate_episode(1)
        if validation:
            print(f"✅ 검증 시스템 작동")
            print(f"   - Episode: {validation.get('episode_number')}")
            print(f"   - Valid: {validation.get('valid')}")
            for check_name, check_result in validation.get('checks', {}).items():
                status = "✅" if check_result.get('passed') else "❌"
                print(f"   {status} {check_name}")
    except Exception as e:
        print(f"❌ 검증 시스템 테스트 실패: {e}")
        return False
    
    # 최종 결과
    print("\n" + "=" * 60)
    print("✅ 모든 테스트 통과! Private 저장소 연결 성공")
    print("=" * 60)
    
    return True


async def main():
    """메인 함수"""
    
    # 테스트 실행
    success = await test_private_repo_connection()
    
    if not success:
        print("\n" + "=" * 60)
        print("❌ 테스트 실패")
        print("=" * 60)
        print("\n🔧 해결 방법:")
        print("1. Personal Access Token (PAT) 생성:")
        print("   - GitHub → Settings → Developer settings → Personal access tokens")
        print("   - 'Generate new token (classic)' 클릭")
        print("   - 'repo' 권한 체크")
        print("\n2. 환경 변수 설정:")
        print("   - Windows: set CLASSIC_ISEKAI_TOKEN=your_token")
        print("   - Mac/Linux: export CLASSIC_ISEKAI_TOKEN=your_token")
        print("\n3. GitHub Actions Secret 설정:")
        print("   - ai-workflow-24h 저장소 → Settings → Secrets → Actions")
        print("   - 'CLASSIC_ISEKAI_TOKEN' 추가")
        print("\n자세한 내용은 docs/PRIVATE_REPO_SETUP.md 참조")
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())