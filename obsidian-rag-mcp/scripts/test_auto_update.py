#!/usr/bin/env python3
"""
Auto-Update Service 테스트 스크립트

AutoUpdateService가 정상적으로 시작/중지되는지 테스트합니다.
"""

import sys
import time
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from vector_store import VectorStore
from network_store import NetworkMetadataStore
from repomix_store import RepomixIndexStore
from indexer import UnifiedIndexer
from auto_update_service import AutoUpdateService


def test_auto_update_service():
    """Auto-Update Service 기본 테스트"""

    print("╔══════════════════════════════════════════════════════════╗")
    print("║                                                          ║")
    print("║         Auto-Update Service 테스트                        ║")
    print("║                                                          ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()

    # Step 1: Store 초기화
    print("📦 Step 1: Store 초기화")
    print("━" * 60)

    try:
        vector_store = VectorStore()
        print("  ✅ VectorStore 초기화 완료")

        network_store = NetworkMetadataStore()
        print("  ✅ NetworkMetadataStore 초기화 완료")

        repomix_store = RepomixIndexStore()
        print("  ✅ RepomixIndexStore 초기화 완료")
        print()
    except Exception as e:
        print(f"  ❌ Store 초기화 실패: {e}")
        return False

    # Step 2: UnifiedIndexer 초기화
    print("📊 Step 2: UnifiedIndexer 초기화")
    print("━" * 60)

    try:
        indexer = UnifiedIndexer(vector_store, network_store, repomix_store)
        indexed_count = len(indexer.metadata.get('indexed_files', {}))
        print(f"  ✅ UnifiedIndexer 초기화 완료 ({indexed_count}개 파일)")
        print()
    except Exception as e:
        print(f"  ❌ UnifiedIndexer 초기화 실패: {e}")
        return False

    # Step 3: AutoUpdateService 시작
    print("🔄 Step 3: AutoUpdateService 시작")
    print("━" * 60)

    try:
        auto_update_service = AutoUpdateService(indexer, debounce_seconds=5.0)
        auto_update_service.start()
        print("  ✅ AutoUpdateService 시작 완료")
        print()
    except Exception as e:
        print(f"  ❌ AutoUpdateService 시작 실패: {e}")
        return False

    # Step 4: 서비스 실행 중 대기
    print("⏳ Step 4: 서비스 실행 중 (10초 대기)...")
    print("━" * 60)
    print("  💡 이 시간 동안 Obsidian에서 파일을 수정하면 자동 업데이트가 감지됩니다.")
    print()

    try:
        for i in range(10, 0, -1):
            print(f"  ⏱️ 남은 시간: {i}초...", end="\r")
            time.sleep(1)
        print("\n")
    except KeyboardInterrupt:
        print("\n  ⚠️ 사용자가 테스트를 중단했습니다.")

    # Step 5: AutoUpdateService 중지
    print("⏹️ Step 5: AutoUpdateService 중지")
    print("━" * 60)

    try:
        auto_update_service.stop()
        print("  ✅ AutoUpdateService 중지 완료")
        print()
    except Exception as e:
        print(f"  ❌ AutoUpdateService 중지 실패: {e}")
        return False

    # 최종 결과
    print("━" * 60)
    print("🎉 Auto-Update Service 테스트 완료!")
    print("━" * 60)
    print()

    return True


if __name__ == "__main__":
    success = test_auto_update_service()
    sys.exit(0 if success else 1)
