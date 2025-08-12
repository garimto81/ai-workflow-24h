"""
무료 AI 모델 통합 모듈
Ollama, Hugging Face 등 로컬에서 실행 가능한 무료 모델 사용
"""

import os
import json
from typing import Dict, List, Optional, Any
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class ModelProvider(Enum):
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"
    GPT4ALL = "gpt4all"

class FreeAIManager:
    """무료 AI 모델 관리자"""
    
    def __init__(self):
        self.providers = {}
        self._initialize_providers()
    
    def _initialize_providers(self):
        """사용 가능한 프로바이더 초기화"""
        
        # Ollama 초기화
        try:
            import ollama
            self.providers[ModelProvider.OLLAMA] = OllamaProvider()
            logger.info("Ollama provider initialized")
        except ImportError:
            logger.warning("Ollama not available")
        
        # Hugging Face 초기화
        try:
            from transformers import pipeline
            self.providers[ModelProvider.HUGGINGFACE] = HuggingFaceProvider()
            logger.info("HuggingFace provider initialized")
        except ImportError:
            logger.warning("HuggingFace not available")
    
    def generate(self, prompt: str, provider: ModelProvider = ModelProvider.OLLAMA) -> str:
        """텍스트 생성"""
        if provider not in self.providers:
            raise ValueError(f"Provider {provider} not available")
        
        return self.providers[provider].generate(prompt)
    
    def analyze_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """작업 분석 및 우선순위 결정"""
        prompt = f"""
        다음 작업을 분석하고 우선순위를 결정하세요:
        작업: {json.dumps(task, ensure_ascii=False)}
        
        응답 형식:
        - priority: 1-10 (높을수록 중요)
        - estimated_time: 예상 소요 시간(분)
        - category: 작업 카테고리
        - suggestions: 개선 제안
        """
        
        response = self.generate(prompt)
        
        # 간단한 파싱 (실제로는 더 정교한 파싱 필요)
        return {
            "priority": 5,
            "estimated_time": 30,
            "category": "general",
            "suggestions": response[:200]
        }

class OllamaProvider:
    """Ollama 로컬 모델 프로바이더"""
    
    def __init__(self, model: str = "llama2:7b"):
        try:
            import ollama
            self.client = ollama.Client()
            self.model = model
            self.available = True
        except Exception as e:
            logger.error(f"Failed to initialize Ollama: {e}")
            self.available = False
    
    def generate(self, prompt: str, max_tokens: int = 500) -> str:
        """텍스트 생성"""
        if not self.available:
            return "Ollama not available. Please install and run Ollama."
        
        try:
            response = self.client.generate(
                model=self.model,
                prompt=prompt,
                options={
                    "num_predict": max_tokens,
                    "temperature": 0.7
                }
            )
            return response.get('response', '')
        except Exception as e:
            logger.error(f"Ollama generation error: {e}")
            return f"Error: {str(e)}"
    
    def list_models(self) -> List[str]:
        """사용 가능한 모델 목록"""
        if not self.available:
            return []
        
        try:
            models = self.client.list()
            return [m['name'] for m in models.get('models', [])]
        except:
            return []

class HuggingFaceProvider:
    """Hugging Face 로컬 모델 프로바이더"""
    
    def __init__(self, model: str = "microsoft/DialoGPT-small"):
        try:
            from transformers import pipeline, AutoTokenizer, AutoModelForCausalLM
            
            # 작은 모델 사용 (메모리 절약)
            self.model_name = model
            self.pipe = pipeline(
                "text-generation",
                model=model,
                max_length=500,
                device=-1  # CPU 사용
            )
            self.available = True
        except Exception as e:
            logger.error(f"Failed to initialize HuggingFace: {e}")
            self.available = False
    
    def generate(self, prompt: str, max_tokens: int = 200) -> str:
        """텍스트 생성"""
        if not self.available:
            return "HuggingFace not available. Please install transformers."
        
        try:
            result = self.pipe(
                prompt,
                max_new_tokens=max_tokens,
                temperature=0.7,
                do_sample=True
            )
            return result[0]['generated_text'][len(prompt):]
        except Exception as e:
            logger.error(f"HuggingFace generation error: {e}")
            return f"Error: {str(e)}"

class TaskPrioritizer:
    """AI 기반 작업 우선순위 결정"""
    
    def __init__(self, ai_manager: FreeAIManager):
        self.ai = ai_manager
    
    def prioritize(self, tasks: List[Dict]) -> List[Dict]:
        """작업 목록 우선순위 정렬"""
        
        # 간단한 규칙 기반 우선순위 (AI 부하 감소)
        for task in tasks:
            # 긴급 키워드 체크
            if any(keyword in str(task).lower() for keyword in ['urgent', '긴급', 'critical']):
                task['priority'] = 10
            # 오류 관련
            elif any(keyword in str(task).lower() for keyword in ['error', 'fail', '오류']):
                task['priority'] = 8
            # 일반 작업
            else:
                task['priority'] = 5
        
        # 우선순위로 정렬
        return sorted(tasks, key=lambda x: x.get('priority', 0), reverse=True)

class LocalEmbeddings:
    """로컬 임베딩 생성 (문서 검색용)"""
    
    def __init__(self):
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer('all-MiniLM-L6-v2')  # 작은 모델
            self.available = True
        except:
            self.available = False
    
    def embed(self, texts: List[str]) -> List[List[float]]:
        """텍스트를 벡터로 변환"""
        if not self.available:
            return []
        
        return self.model.encode(texts).tolist()

# 싱글톤 인스턴스
ai_manager = FreeAIManager()