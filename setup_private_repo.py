#!/usr/bin/env python3
"""
Classic Isekai Private 저장소 연결 설정 도우미
이 스크립트는 사용자가 PAT 토큰을 설정하는 것을 도와줍니다.
"""

import os
import sys
import json
import subprocess
from pathlib import Path
import getpass


def main():
    print("=" * 60)
    print("🔐 Classic Isekai Private 저장소 연결 설정")
    print("=" * 60)
    
    print("\n이 스크립트는 private 저장소 연결을 위한 설정을 도와드립니다.")
    print("필요한 것: GitHub Personal Access Token (PAT)")
    
    # 1. PAT 토큰 생성 안내
    print("\n" + "=" * 60)
    print("📝 Step 1: Personal Access Token 생성")
    print("=" * 60)
    
    print("""
1. GitHub.com에 로그인
2. 우측 상단 프로필 클릭 → Settings
3. 좌측 메뉴 하단 → Developer settings
4. Personal access tokens → Tokens (classic)
5. "Generate new token (classic)" 클릭
6. 설정:
   - Note: "AI Workflow Classic Isekai Access"
   - Expiration: 90 days (또는 원하는 기간)
   - Scopes: ✅ repo (전체 체크)
7. "Generate token" 클릭
8. 토큰 복사 (ghp_로 시작하는 문자열)
""")
    
    input("위 단계를 완료하셨으면 Enter를 누르세요...")
    
    # 2. 토큰 입력 받기
    print("\n" + "=" * 60)
    print("🔑 Step 2: Token 입력")
    print("=" * 60)
    
    token = getpass.getpass("GitHub PAT Token (ghp_...): ").strip()
    
    if not token:
        print("❌ 토큰이 입력되지 않았습니다.")
        sys.exit(1)
    
    if not token.startswith("ghp_"):
        print("⚠️ 주의: 일반적으로 PAT 토큰은 'ghp_'로 시작합니다.")
        confirm = input("계속하시겠습니까? (y/n): ")
        if confirm.lower() != 'y':
            sys.exit(1)
    
    # 3. 환경 변수 설정 방법 선택
    print("\n" + "=" * 60)
    print("⚙️ Step 3: 설정 방법 선택")
    print("=" * 60)
    
    print("""
어떻게 설정하시겠습니까?

1. 로컬 환경 변수 (.env 파일)
2. GitHub Actions Secret (온라인 실행용)
3. 둘 다 설정
""")
    
    choice = input("선택 (1/2/3): ").strip()
    
    # 4. 로컬 환경 설정
    if choice in ['1', '3']:
        print("\n📁 로컬 환경 설정 중...")
        
        env_file = Path(".env")
        env_content = []
        
        # 기존 .env 파일 읽기
        if env_file.exists():
            with open(env_file, 'r') as f:
                for line in f:
                    if not line.startswith("CLASSIC_ISEKAI_TOKEN"):
                        env_content.append(line.rstrip())
        
        # 새 토큰 추가
        env_content.append(f"CLASSIC_ISEKAI_TOKEN={token}")
        
        # .env 파일 쓰기
        with open(env_file, 'w') as f:
            f.write('\n'.join(env_content) + '\n')
        
        print(f"✅ .env 파일에 토큰 저장 완료")
        
        # .gitignore 확인
        gitignore = Path(".gitignore")
        if gitignore.exists():
            with open(gitignore, 'r') as f:
                content = f.read()
                if '.env' not in content:
                    with open(gitignore, 'a') as f:
                        f.write('\n.env\n')
                    print("✅ .gitignore에 .env 추가")
    
    # 5. GitHub Actions Secret 설정 안내
    if choice in ['2', '3']:
        print("\n🌐 GitHub Actions Secret 설정")
        print("-" * 40)
        print("""
수동으로 설정해야 합니다:

1. https://github.com/garimto81/ai-workflow-24h 접속
2. Settings 탭 클릭
3. 좌측 메뉴: Secrets and variables → Actions
4. "New repository secret" 버튼 클릭
5. 설정:
   - Name: CLASSIC_ISEKAI_TOKEN
   - Secret: [토큰 붙여넣기]
6. "Add secret" 클릭
""")
        
        # 클립보드에 복사 시도
        try:
            if sys.platform == "win32":
                subprocess.run(["clip"], input=token.encode(), check=True)
                print("\n✅ 토큰이 클립보드에 복사되었습니다. (Ctrl+V로 붙여넣기)")
            elif sys.platform == "darwin":
                subprocess.run(["pbcopy"], input=token.encode(), check=True)
                print("\n✅ 토큰이 클립보드에 복사되었습니다. (Cmd+V로 붙여넣기)")
        except:
            pass
        
        print(f"\n토큰: {token[:10]}...{token[-4:]}")
        input("\nGitHub에서 설정을 완료하셨으면 Enter를 누르세요...")
    
    # 6. 연결 테스트
    print("\n" + "=" * 60)
    print("🧪 Step 4: 연결 테스트")
    print("=" * 60)
    
    test = input("\n연결을 테스트하시겠습니까? (y/n): ")
    if test.lower() == 'y':
        print("\n테스트 실행 중...")
        
        # 환경 변수 설정
        os.environ['CLASSIC_ISEKAI_TOKEN'] = token
        
        # 테스트 스크립트 실행
        result = subprocess.run(
            [sys.executable, "test_private_repo_connection.py"],
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        if result.returncode != 0:
            print(result.stderr)
    
    # 7. 완료
    print("\n" + "=" * 60)
    print("✅ 설정 완료!")
    print("=" * 60)
    
    print("""
다음 단계:

1. 로컬 테스트:
   python test_private_repo_connection.py

2. GitHub Actions 실행:
   - Actions 탭 → "🚀 Classic Isekai 웹소설 개선"
   - Run workflow 클릭

3. 미션 실행:
   - 미션: "1~3화 반복 개선"
   - 목표 점수: 8.5
""")


if __name__ == "__main__":
    main()