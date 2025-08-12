"""
GitHub Actions 사이클 관리자
각 사이클 완료 후 상태를 저장하고 다음 사이클 트리거
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
import asyncio

# 프로젝트 경로 추가
sys.path.append(str(Path(__file__).parent))

from new_agent_system import NewAgentSystem

class GitHubCycleManager:
    """GitHub Actions용 사이클 관리자"""
    
    def __init__(self):
        self.state_file = Path("cycle_state.json")
        self.results_file = Path("cycle_results.json")
        self.state = self.load_state()
    
    def load_state(self) -> Dict[str, Any]:
        """상태 파일 로드"""
        if self.state_file.exists():
            with open(self.state_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'current_cycle': 1,
            'episodes': [1, 2, 3],
            'target_score': 9.0,
            'max_cycles': 10,
            'scores_history': [],
            'start_time': datetime.now().isoformat()
        }
    
    def save_state(self):
        """상태 파일 저장"""
        with open(self.state_file, 'w', encoding='utf-8') as f:
            json.dump(self.state, f, indent=2, ensure_ascii=False)
    
    async def run_single_cycle(self) -> Dict[str, Any]:
        """한 사이클만 실행"""
        print(f"🔄 사이클 #{self.state['current_cycle']} 시작")
        print(f"   대상 에피소드: {self.state['episodes']}")
        print(f"   목표 점수: {self.state['target_score']}")
        
        # 시스템 초기화
        system = NewAgentSystem()
        await system.initialize()
        
        # 각 에피소드 개선
        cycle_results = {
            'cycle_number': self.state['current_cycle'],
            'timestamp': datetime.now().isoformat(),
            'episodes': {},
            'improvements_made': 0,
            'all_reached_target': True
        }
        
        for episode_num in self.state['episodes']:
            print(f"\n📖 에피소드 {episode_num}화 처리 중...")
            
            # 개선 작업 실행
            task = {
                'type': 'improve_episode',
                'episode_number': episode_num,
                'target_score': self.state['target_score']
            }
            
            result = await system.main_coordinator.coordinate_episode_improvement(task)
            
            # 결과 저장
            final_score = result.get('final_score', 0)
            improvements = len(result.get('improvements_made', []))
            
            cycle_results['episodes'][str(episode_num)] = {
                'score': final_score,
                'improvements': improvements,
                'reached_target': final_score >= self.state['target_score']
            }
            
            cycle_results['improvements_made'] += improvements
            
            if final_score < self.state['target_score']:
                cycle_results['all_reached_target'] = False
            
            print(f"   ✅ {episode_num}화 완료: {final_score:.1f}점 (개선: {improvements}개)")
        
        # 평균 점수 계산
        scores = [ep['score'] for ep in cycle_results['episodes'].values()]
        cycle_results['average_score'] = sum(scores) / len(scores) if scores else 0
        
        # 상태 업데이트
        self.state['current_cycle'] += 1
        self.state['last_run'] = datetime.now().isoformat()
        self.state['last_scores'] = {
            ep: data['score'] 
            for ep, data in cycle_results['episodes'].items()
        }
        
        # 점수 히스토리 추가
        if 'scores_history' not in self.state:
            self.state['scores_history'] = []
        
        self.state['scores_history'].append({
            'cycle': cycle_results['cycle_number'],
            'timestamp': cycle_results['timestamp'],
            'average_score': cycle_results['average_score'],
            'scores': self.state['last_scores']
        })
        
        # 파일 저장
        self.save_state()
        with open(self.results_file, 'w', encoding='utf-8') as f:
            json.dump(cycle_results, f, indent=2, ensure_ascii=False)
        
        return cycle_results
    
    def should_continue(self) -> bool:
        """계속 실행 여부 결정"""
        # 최대 사이클 도달
        if self.state['current_cycle'] > self.state['max_cycles']:
            print(f"⚠️ 최대 사이클({self.state['max_cycles']}) 도달")
            return False
        
        # 모든 에피소드가 목표 점수 도달
        if self.state.get('last_scores'):
            all_reached = all(
                score >= self.state['target_score'] 
                for score in self.state['last_scores'].values()
            )
            if all_reached:
                print(f"🎉 모든 에피소드가 목표 점수 도달!")
                return False
        
        return True
    
    def get_progress_report(self) -> str:
        """진행 상황 리포트 생성"""
        report = []
        report.append(f"📊 진행 상황 리포트")
        report.append(f"=" * 50)
        report.append(f"현재 사이클: #{self.state['current_cycle']}")
        report.append(f"목표 점수: {self.state['target_score']}")
        
        if self.state.get('last_scores'):
            report.append(f"\n최근 점수:")
            for ep, score in self.state['last_scores'].items():
                status = "✅" if score >= self.state['target_score'] else "🔄"
                report.append(f"  {status} 에피소드 {ep}화: {score:.1f}점")
        
        if self.state.get('scores_history'):
            report.append(f"\n점수 변화 추이:")
            for history in self.state['scores_history'][-5:]:  # 최근 5개
                report.append(f"  사이클 #{history['cycle']}: 평균 {history['average_score']:.1f}점")
        
        return "\n".join(report)


async def main():
    """메인 실행 함수"""
    # 명령행 인자 처리
    if len(sys.argv) >= 2:
        episodes = [int(x.strip()) for x in sys.argv[1].split(',')]
    else:
        episodes = [1, 2, 3]
    
    if len(sys.argv) >= 3:
        target_score = float(sys.argv[2])
    else:
        target_score = 9.0
    
    if len(sys.argv) >= 4:
        max_cycles = int(sys.argv[3])
    else:
        max_cycles = 10
    
    # 매니저 초기화
    manager = GitHubCycleManager()
    
    # 신규 실행인 경우 상태 초기화
    if len(sys.argv) > 1:
        manager.state['episodes'] = episodes
        manager.state['target_score'] = target_score
        manager.state['max_cycles'] = max_cycles
        manager.save_state()
    
    # 한 사이클 실행
    results = await manager.run_single_cycle()
    
    # 진행 상황 출력
    print("\n" + manager.get_progress_report())
    
    # GitHub Actions 출력 설정
    print(f"\n::set-output name=cycle_complete::{results['all_reached_target']}")
    print(f"::set-output name=average_score::{results['average_score']}")
    print(f"::set-output name=should_continue::{manager.should_continue()}")
    
    return 0 if results['all_reached_target'] else 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)