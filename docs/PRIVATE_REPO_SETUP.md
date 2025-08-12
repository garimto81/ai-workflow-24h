# 🔐 Private 저장소 연결 가이드

## 📋 3가지 연결 방법

### 방법 1: Personal Access Token (PAT) 사용 ⭐추천
가장 안전하고 쉬운 방법입니다.

### 방법 2: Deploy Key 사용
특정 저장소만 접근 가능하게 설정

### 방법 3: GitHub App 사용
고급 사용자용

---

## 🚀 방법 1: Personal Access Token (가장 쉬움)

### Step 1: PAT 생성하기
```
1. GitHub.com 로그인
2. Settings → Developer settings → Personal access tokens → Tokens (classic)
3. "Generate new token (classic)" 클릭
4. 설정:
   - Note: "AI Workflow Access"
   - Expiration: 90 days (또는 원하는 기간)
   - 권한 체크:
     ✅ repo (전체)
     ✅ workflow
5. "Generate token" 클릭
6. 토큰 복사 (한 번만 보임!) 예: ghp_xxxxxxxxxxxxxxxxxxxx
```

### Step 2: AI Workflow 저장소에 토큰 저장
```
1. ai-workflow-24h 저장소로 이동
2. Settings → Secrets and variables → Actions
3. "New repository secret" 클릭
4. 설정:
   - Name: CLASSIC_ISEKAI_TOKEN
   - Value: [복사한 PAT 토큰]
5. "Add secret" 클릭
```

### Step 3: Workflow 파일 수정
```yaml
# .github/workflows/classic-isekai-automation.yml 수정

- name: Checkout Classic Isekai
  uses: actions/checkout@v3
  with:
    repository: garimto81/classic-isekai
    token: ${{ secrets.CLASSIC_ISEKAI_TOKEN }}  # PAT 토큰 사용
    path: classic-isekai
```

---

## 🔑 방법 2: Deploy Key 사용

### Step 1: SSH 키 생성
```bash
# 로컬에서 실행
ssh-keygen -t ed25519 -C "ai-workflow-deploy-key" -f deploy_key

# 두 개 파일 생성됨:
# deploy_key (private key)
# deploy_key.pub (public key)
```

### Step 2: Classic Isekai에 Deploy Key 추가
```
1. classic-isekai 저장소 → Settings → Deploy keys
2. "Add deploy key" 클릭
3. 설정:
   - Title: "AI Workflow Access"
   - Key: [deploy_key.pub 내용 붙여넣기]
   - ✅ Allow write access 체크
4. "Add key" 클릭
```

### Step 3: AI Workflow에 Private Key 저장
```
1. ai-workflow-24h 저장소 → Settings → Secrets
2. "New repository secret"
3. 설정:
   - Name: DEPLOY_KEY
   - Value: [deploy_key 내용 전체]
```

### Step 4: Workflow에서 SSH 사용
```yaml
- name: Setup SSH
  run: |
    mkdir -p ~/.ssh
    echo "${{ secrets.DEPLOY_KEY }}" > ~/.ssh/deploy_key
    chmod 600 ~/.ssh/deploy_key
    ssh-keyscan github.com >> ~/.ssh/known_hosts

- name: Clone Classic Isekai
  run: |
    GIT_SSH_COMMAND="ssh -i ~/.ssh/deploy_key" \
    git clone git@github.com:garimto81/classic-isekai.git
```

---

## 🤖 방법 3: GitHub App 사용 (고급)

### Step 1: GitHub App 생성
```
1. Settings → Developer settings → GitHub Apps
2. "New GitHub App" 클릭
3. 설정:
   - Name: "AI Workflow Bot"
   - Homepage URL: https://github.com/garimto81/ai-workflow-24h
   - Permissions:
     - Repository permissions:
       - Contents: Read & Write
       - Pull requests: Write
4. "Create GitHub App" 클릭
```

### Step 2: App 설치
```
1. 생성된 App 페이지 → "Install App"
2. classic-isekai 저장소 선택
3. 설치 완료
```

---

## 🎯 간단한 해결책: Repository Secrets 공유

### 가장 빠른 방법:
두 저장소를 같은 Organization에 넣고 Organization Secrets 사용

```
1. Organization 생성 (무료)
2. 두 저장소를 Organization으로 이동
3. Organization Settings → Secrets
4. ANTHROPIC_API_KEY 등록
5. 두 저장소에서 동시 사용 가능
```

---

## ✅ 권장 설정 (PAT 방식)

### 1. PAT 토큰 생성 후 저장
```yaml
# ai-workflow-24h/.github/workflows/classic-isekai-automation.yml

env:
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
  CLASSIC_TOKEN: ${{ secrets.CLASSIC_ISEKAI_TOKEN }}

steps:
  - name: Checkout AI Workflow
    uses: actions/checkout@v3
    with:
      path: ai-workflow

  - name: Checkout Classic Isekai (Private)
    uses: actions/checkout@v3
    with:
      repository: garimto81/classic-isekai
      token: ${{ secrets.CLASSIC_ISEKAI_TOKEN }}
      path: classic-isekai
```

### 2. API 호출 시 토큰 사용
```python
# repository_connector.py 수정

class ClassicIsekaiConnector:
    def __init__(self, github_token: Optional[str] = None):
        self.github_token = github_token or os.environ.get('CLASSIC_TOKEN')
        
    async def fetch_episode_content(self, episode_number: int):
        headers = {
            'Authorization': f'token {self.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        # Private repo API 호출
```

---

## 🔒 보안 주의사항

### DO ✅
- PAT 토큰은 최소 권한만 부여
- 토큰 만료 기간 설정
- Secrets에만 저장 (절대 코드에 직접 입력 금지)

### DON'T ❌
- 토큰을 코드에 하드코딩
- 토큰을 로그에 출력
- 토큰을 커밋에 포함

---

## 🚦 테스트 방법

### 연결 테스트
```bash
# GitHub Actions에서 테스트
- name: Test Private Repo Access
  run: |
    echo "Testing access to private repo..."
    if [ -d "classic-isekai" ]; then
      echo "✅ Successfully accessed private repo"
      ls -la classic-isekai/
    else
      echo "❌ Failed to access private repo"
      exit 1
    fi
```

---

## 💡 추가 팁

### 로컬 개발 시
```bash
# .env 파일 생성
CLASSIC_ISEKAI_TOKEN=ghp_xxxxxxxxxxxx
ANTHROPIC_API_KEY=sk-xxxxxxxxxxxx

# Python에서 사용
from dotenv import load_dotenv
load_dotenv()
```

### 다중 Private 저장소
여러 private 저장소 접근이 필요한 경우:
1. 각각 다른 토큰 생성
2. 각각 다른 Secret 이름으로 저장
3. Workflow에서 개별 사용

---

## 📞 문제 해결

### "Bad credentials" 오류
- 토큰이 올바른지 확인
- 토큰 권한 확인 (repo 권한 필요)
- Secret 이름 오타 확인

### "Repository not found" 오류
- 저장소 이름/소유자 확인
- 토큰에 private repo 접근 권한 있는지 확인

### "Permission denied" 오류
- 토큰에 write 권한 있는지 확인
- Deploy key의 경우 "Allow write access" 체크 확인