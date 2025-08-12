"""
Classic Isekai 프로젝트 전용 메인 실행 파일
기존 에피소드들을 검토하고 개선하는 시스템
"""

import asyncio
import logging
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# 에이전트 임포트
from agents.episode_reviewer import EpisodeReviewerAgent
from agents.project_loader import project_loader
from agents.main_agent import MainAgent
from agents.writer_agent import WriterAgent

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/classic_isekai.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class ClassicIsekaiSystem:
    """Classic Isekai 프로젝트 전용 시스템"""
    
    def __init__(self):
        self.project_loader = project_loader
        self.episode_reviewer = None
        self.running = False
        
    async def initialize(self):
        """시스템 초기화"""
        logger.info("=" * 60)
        logger.info("Classic Isekai 웹소설 검토 시스템 초기화")
        logger.info("=" * 60)
        
        # 프로젝트 로더 초기화
        await self.project_loader.initialize_project()
        
        # 에피소드 리뷰어 초기화
        self.episode_reviewer = EpisodeReviewerAgent()
        await self.episode_reviewer.initialize()
        
        # 프로젝트 요약 출력
        summary = self.project_loader.get_project_summary()
        logger.info(f"프로젝트: {summary['project_name']}")
        logger.info(f"우주관: {summary['universe']}")
        logger.info(f"총 에피소드: {summary['total_episodes']}개")
        logger.info(f"완료된 에피소드: {summary['completed_episodes']}")
        logger.info(f"로드된 문서: {summary['available_documents']} 개")
        
        logger.info("시스템 초기화 완료")
    
    async def review_single_episode(self, episode_number: int) -> Dict[str, Any]:
        """단일 에피소드 검토"""
        logger.info(f"에피소드 {episode_number}화 검토 시작")
        
        result = await self.episode_reviewer.review_episode({
            'type': 'review_episode',
            'episode_number': episode_number
        })
        
        if 'error' in result:
            logger.error(f"에피소드 {episode_number}화 검토 실패: {result['error']}")
            return result
        
        # 결과 요약 출력
        logger.info(f"에피소드 {episode_number}화 검토 결과:")
        logger.info(f"  전체 점수: {result['overall_score']}/10")
        logger.info(f"  상태: {result['status']}")
        logger.info(f"  분량: {result['word_count']}자")
        
        # 상세 점수
        logger.info("  상세 점수:")
        for criterion, details in result['detailed_scores'].items():
            logger.info(f"    {details['description']}: {details['score']:.1f}/10")
        
        # 개선 제안
        if result['improvement_suggestions']:
            logger.info("  개선 제안:")
            for suggestion in result['improvement_suggestions']:
                logger.info(f"    - {suggestion}")
        
        return result
    
    async def review_all_episodes(self) -> Dict[str, Any]:
        """모든 에피소드 검토"""
        logger.info("전체 에피소드 검토 시작")
        
        result = await self.episode_reviewer.review_all_episodes({
            'type': 'review_all_episodes'
        })
        
        # 전체 요약 출력
        logger.info("=" * 50)
        logger.info("전체 검토 결과 요약")
        logger.info("=" * 50)
        logger.info(f"총 검토 에피소드: {result['total_episodes']}개")
        logger.info(f"평균 점수: {result['average_score']:.1f}/10")
        logger.info(f"최고 점수: {result['highest_score']:.1f}/10")
        logger.info(f"최저 점수: {result['lowest_score']:.1f}/10")
        logger.info(f"개선 필요: {result['episodes_needing_improvement']}개")
        
        # 에피소드별 점수 요약
        logger.info("\n에피소드별 점수:")
        for ep_num, ep_result in sorted(result['detailed_results'].items()):
            status_icon = "✅" if ep_result['overall_score'] >= 7.5 else "⚠️"
            logger.info(f"  {ep_num}화: {ep_result['overall_score']:.1f}/10 {status_icon}")
        
        return result
    
    async def improve_episode(self, episode_number: int, target_score: float = 8.5) -> Dict[str, Any]:
        """에피소드 개선"""
        logger.info(f"에피소드 {episode_number}화 개선 시작 (목표: {target_score}/10)")
        
        # 현재 상태 검토
        current_review = await self.review_single_episode(episode_number)
        current_score = current_review.get('overall_score', 0)
        
        if current_score >= target_score:
            logger.info(f"이미 목표 점수 달성: {current_score}/10")
            return current_review
        
        # 개선 필요
        improvement_needed = target_score - current_score
        logger.info(f"개선 필요 점수: +{improvement_needed:.1f}")
        
        # 개선 제안 기반으로 수정 계획 생성
        suggestions = current_review.get('improvement_suggestions', [])
        
        improvement_plan = {
            'episode_number': episode_number,
            'current_score': current_score,
            'target_score': target_score,
            'improvement_needed': improvement_needed,
            'suggestions': suggestions,
            'priority_areas': self.identify_priority_areas(current_review['detailed_scores'])
        }
        
        logger.info("개선 계획:")
        for area in improvement_plan['priority_areas']:
            logger.info(f"  우선순위: {area['criterion']} ({area['current_score']:.1f}/10)")
        
        return improvement_plan
    
    def identify_priority_areas(self, detailed_scores: Dict) -> List[Dict]:
        """개선 우선순위 영역 식별"""
        priority_areas = []
        
        for criterion, details in detailed_scores.items():
            if details['score'] < 7.5:
                priority_areas.append({
                    'criterion': details['description'],
                    'current_score': details['score'],
                    'weight': details['weight'],
                    'impact': details['score'] * details['weight']  # 개선 시 전체 점수 영향도
                })
        
        # 영향도 순으로 정렬
        priority_areas.sort(key=lambda x: x['impact'])
        
        return priority_areas
    
    async def run_interactive_mode(self):
        """대화형 모드 실행"""
        logger.info("\n" + "=" * 50)
        logger.info("대화형 모드 시작")
        logger.info("명령어:")
        logger.info("  1 - 에피소드 1화 검토")
        logger.info("  2 - 에피소드 2화 검토")
        logger.info("  3 - 에피소드 3화 검토")
        logger.info("  all - 전체 에피소드 검토")
        logger.info("  improve N - N화 개선")
        logger.info("  quit - 종료")
        logger.info("=" * 50)
        
        while True:
            try:
                command = input("\n명령어를 입력하세요: ").strip().lower()
                
                if command == 'quit':
                    break
                elif command in ['1', '2', '3']:
                    ep_num = int(command)
                    await self.review_single_episode(ep_num)
                elif command == 'all':
                    await self.review_all_episodes()
                elif command.startswith('improve'):
                    try:
                        ep_num = int(command.split()[1])
                        await self.improve_episode(ep_num)
                    except (IndexError, ValueError):
                        logger.error("사용법: improve N (N은 에피소드 번호)")
                else:
                    logger.info("알 수 없는 명령어입니다.")
                    
            except KeyboardInterrupt:
                break
            except Exception as e:
                logger.error(f"명령어 실행 오류: {e}")
        
        logger.info("대화형 모드 종료")
    
    async def run_auto_review(self):
        """자동 검토 모드"""
        logger.info("자동 검토 모드 시작")
        
        # 모든 에피소드 검토
        await self.review_all_episodes()
        
        # 개선이 필요한 에피소드들 식별
        all_episodes = project_loader.get_all_episodes()
        for episode_num in sorted(all_episodes.keys()):
            review_result = await self.review_single_episode(episode_num)
            
            if review_result.get('overall_score', 0) < 7.5:
                logger.info(f"에피소드 {episode_num}화 개선 계획 생성")
                await self.improve_episode(episode_num)
        
        logger.info("자동 검토 완료")


async def main():
    """메인 함수"""
    
    # 커맨드라인 인자 처리
    if "--help" in sys.argv:
        print("""
Classic Isekai 웹소설 검토 시스템

사용법:
  python classic_isekai_main.py              # 대화형 모드
  python classic_isekai_main.py --auto       # 자동 검토
  python classic_isekai_main.py --episode N  # N화만 검토
  python classic_isekai_main.py --all        # 전체 검토
  python classic_isekai_main.py --help       # 도움말

기능:
  - 기존 에피소드 품질 검토
  - 세계관/캐릭터 일관성 확인
  - 개선 제안 제공
  - 전체 프로젝트 현황 파악
        """)
        return
    
    # 시스템 생성 및 초기화
    system = ClassicIsekaiSystem()
    await system.initialize()
    
    try:
        if "--auto" in sys.argv:
            # 자동 검토 모드
            await system.run_auto_review()
        
        elif "--episode" in sys.argv:
            # 특정 에피소드 검토
            try:
                idx = sys.argv.index("--episode")
                episode_num = int(sys.argv[idx + 1])
                await system.review_single_episode(episode_num)
            except (IndexError, ValueError):
                logger.error("사용법: --episode N (N은 에피소드 번호)")
        
        elif "--all" in sys.argv:
            # 전체 에피소드 검토
            await system.review_all_episodes()
        
        else:
            # 대화형 모드 (기본)
            await system.run_interactive_mode()
    
    except KeyboardInterrupt:
        logger.info("사용자에 의해 중단됨")
    except Exception as e:
        logger.error(f"실행 오류: {e}")
    
    logger.info("Classic Isekai 검토 시스템 종료")


if __name__ == "__main__":
    # 실행
    asyncio.run(main())