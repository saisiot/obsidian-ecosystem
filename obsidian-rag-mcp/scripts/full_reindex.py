#!/usr/bin/env python3
"""
전체 vault 재인덱싱 스크립트

UnifiedIndexer.update_index()를 호출하여 새로운 파일들을 인덱싱합니다.
"""

import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from indexer import UnifiedIndexer
from network_store import NetworkMetadataStore
from repomix_store import RepomixIndexStore
from vector_store import VectorStore


def full_reindex():
    """전체 vault 증분 인덱싱"""

    print("╔══════════════════════════════════════════════════════════╗")
    print("║                                                          ║")
    print("║         Obsidian Vault 전체 재인덱싱                      ║")
    print("║                                                          ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()

    # Store 초기화
    print("🔄 Store 초기화 중...")
    network_store = NetworkMetadataStore()
    repomix_store = RepomixIndexStore()
    vector_store = VectorStore()

    # UnifiedIndexer 생성
    indexer = UnifiedIndexer(
        vector_store=vector_store,
        network_store=network_store,
        repomix_store=repomix_store,
    )

    print("✅ Store 초기화 완료")
    print()

    # 증분 업데이트 실행 (새 파일, 수정된 파일, 삭제된 파일 모두 처리)
    print("📊 변경사항 확인 및 인덱싱 시작...")
    print()
    indexer.update_index()

    print()
    print("━" * 60)
    print("🎉 전체 vault 재인덱싱 완료!")
    print("━" * 60)


if __name__ == "__main__":
    full_reindex()
