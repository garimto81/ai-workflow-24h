# 🌐 온라인 배포 가이드

## 📊 플랫폼 비교

| 플랫폼 | 무료 제공 | 24시간 실행 | 설정 난이도 | 추천도 |
|--------|----------|-------------|-------------|---------|
| **Google Colab** | ✅ 완전 무료 | ⚠️ 12시간 제한 | ⭐ 매우 쉬움 | ⭐⭐⭐⭐⭐ |
| **GitHub Actions** | ✅ 월 2000분 무료 | ✅ 스케줄 가능 | ⭐⭐ 쉬움 | ⭐⭐⭐⭐ |
| **Render.com** | ✅ 월 750시간 무료 | ✅ 가능 | ⭐⭐⭐ 보통 | ⭐⭐⭐ |
| **Railway.app** | ⚠️ $5 크레딧 | ✅ 가능 | ⭐⭐ 쉬움 | ⭐⭐⭐ |
| **Replit** | ⚠️ 제한적 무료 | ⚠️ 제한 있음 | ⭐ 매우 쉬움 | ⭐⭐⭐ |

## 🚀 빠른 시작 (추천)

### 1. Google Colab (가장 쉬움)
1. [Google Colab](https://colab.research.google.com/) 접속
2. `webnovel_automation_colab.ipynb` 파일 업로드
3. API 키 입력 후 실행
4. **장점**: 무료, GPU 지원, 설정 불필요
5. **단점**: 12시간마다 재시작 필요

### 2. GitHub Actions (자동화 최적)
1. GitHub 저장소 Settings → Secrets → New repository secret
2. `ANTHROPIC_API_KEY` 추가
3. Actions 탭에서 수동 실행 또는 자동 스케줄
4. **장점**: 완전 자동화, 커밋 자동화
5. **단점**: 월 2000분 제한

## 🔧 상세 설정 가이드

### GitHub Actions 설정
```bash
1. GitHub 저장소로 이동
2. Settings → Secrets and variables → Actions
3. New repository secret 클릭
4. Name: ANTHROPIC_API_KEY
5. Value: [본인의 API 키]
6. Actions 탭 → Webnovel Automation 24/7 → Run workflow
```

### Render.com 설정
```bash
1. https://render.com 가입
2. New → Background Worker
3. GitHub 저장소 연결
4. Environment Variables에 ANTHROPIC_API_KEY 추가
5. Deploy 클릭
```

### Railway.app 설정
```bash
1. https://railway.app 가입
2. New Project → Deploy from GitHub repo
3. 저장소 선택
4. Variables에 ANTHROPIC_API_KEY 추가
5. Deploy 클릭
```

### Replit 설정
```bash
1. https://replit.com 가입
2. Import from GitHub
3. Secrets에 ANTHROPIC_API_KEY 추가
4. Run 버튼 클릭
```

## 📱 모바일에서 실행하기

### Termux (Android)
```bash
pkg install python git
git clone https://github.com/garimto81/ai-workflow-24h
cd ai-workflow-24h/src/workflow
pip install -r requirements.txt
python new_agent_system.py 1,2,3 9.0
```

### Pythonista (iOS)
```python
import requests
import os

# GitHub에서 코드 다운로드
url = "https://raw.githubusercontent.com/garimto81/ai-workflow-24h/master/src/workflow/new_agent_system.py"
code = requests.get(url).text

# 실행
exec(code)
```

## 🔄 자동 재시작 설정

### systemd (Linux VPS)
```ini
[Unit]
Description=Webnovel Automation
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/ai-workflow-24h/src/workflow
ExecStart=/usr/bin/python3 new_agent_system.py 1,2,3 9.0
Restart=always
Environment="ANTHROPIC_API_KEY=your_key_here"

[Install]
WantedBy=multi-user.target
```

### PM2 (Node.js)
```javascript
module.exports = {
  apps: [{
    name: 'webnovel-automation',
    script: 'python',
    args: 'new_agent_system.py 1,2,3 9.0',
    cwd: './src/workflow',
    autorestart: true,
    watch: false,
    max_memory_restart: '1G',
    env: {
      ANTHROPIC_API_KEY: 'your_key_here'
    }
  }]
}
```

## 💰 비용 최적화 팁

1. **Google Colab Pro** ($10/월): 24시간 실행 가능
2. **GitHub Actions**: 여러 계정으로 무료 시간 확장
3. **Render.com**: 무료 플랜으로 충분
4. **자체 서버**: Raspberry Pi로 홈서버 구축

## 🔐 보안 주의사항

1. **절대 API 키를 코드에 직접 입력하지 마세요**
2. 항상 환경 변수나 Secrets 사용
3. 공개 저장소에 민감한 정보 업로드 금지
4. 정기적으로 API 키 교체

## 📞 지원

문제가 있으시면 GitHub Issues에 문의해주세요:
https://github.com/garimto81/ai-workflow-24h/issues