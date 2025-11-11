#!/usr/bin/env python3
"""
데이터베이스 재빌드 스크립트

ChromaDB는 유지하고, Network와 Repomix 데이터베이스를 처음부터 다시 빌드합니다.
"""

import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

import json
from datetime import datetime

from config import METADATA_FILE, VAULT_PATH
from indexer import UnifiedIndexer
from network_store import NetworkMetadataStore
from repomix_store import RepomixIndexStore
from vector_store import VectorStore


def rebuild_databases():
    """데이터베이스 재빌드"""

    print("╔══════════════════════════════════════════════════════════╗")
    print("║                                                          ║")
    print("║         Obsidian RAG MCP Database Rebuild                ║")
    print("║                                                          ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()

    # Step 1: 기존 Network와 Repomix 데이터베이스 백업
    print("📦 Step 1: 기존 데이터베이스 백업")
    print("━" * 60)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = PROJECT_ROOT / "data" / "backup" / f"rebuild_{timestamp}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    network_file = PROJECT_ROOT / "data" / "network_metadata.json"
    repomix_file = PROJECT_ROOT / "data" / "repomix_index.json"

    if network_file.exists():
        import shutil

        shutil.copy(network_file, backup_dir / "network_metadata.json")
        print(f"  ✅ Network 백업: {backup_dir}/network_metadata.json")

    if repomix_file.exists():
        import shutil

        shutil.copy(repomix_file, backup_dir / "repomix_index.json")
        print(f"  ✅ Repomix 백업: {backup_dir}/repomix_index.json")

    print()

    # Step 2: Network와 Repomix 데이터베이스 초기화
    print("🔄 Step 2: 데이터베이스 초기화")
    print("━" * 60)

    # Network Metadata 초기화
    network_store = NetworkMetadataStore(metadata_file=network_file)
    print("  ✅ NetworkMetadataStore 초기화")

    # Repomix Index 초기화
    repomix_store = RepomixIndexStore(index_file=repomix_file)
    print("  ✅ RepomixIndexStore 초기화")

    # VectorStore는 기존 것 사용
    vector_store = VectorStore()
    print("  ✅ VectorStore 연결 (기존 ChromaDB 사용)")

    print()

    # Step 3: 전체 Vault 재인덱싱
    print("📂 Step 3: Vault 전체 재인덱싱")
    print("━" * 60)

    # 마크다운 파일 목록
    md_files = list(VAULT_PATH.rglob("*.md"))
    print(f"  📂 발견된 마크다운 파일: {len(md_files)}개")
    print()

    # UnifiedIndexer 생성
    indexer = UnifiedIndexer(
        vector_store=vector_store,
        network_store=network_store,
        repomix_store=repomix_store,
    )

    # index_metadata.json에서 indexed_files 읽기
    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        metadata = json.load(f)
        indexed_files = metadata.get("indexed_files", {})

    print(f"  📊 Index metadata: {len(indexed_files)}개 파일 기록")
    print("  ⏳ 재인덱싱 시작... (수 분 소요될 수 있습니다)")
    print()

    # 각 파일을 순회하며 Network와 Repomix에 추가
    from obsidian_parser import ObsidianParser

    parser = ObsidianParser()

    success_count = 0
    error_count = 0

    for i, md_file in enumerate(md_files, 1):
        file_path = str(md_file)

        # indexed_files에 있는 파일만 처리
        if file_path not in indexed_files:
            continue

        try:
            # 파일 파싱
            doc = parser.parse_file(md_file)
            if not doc:
                continue

            # Network Metadata 업데이트
            network_store.update_metadata(doc)

            # Repomix Index 업데이트
            repomix_store.update_index(doc, md_file)

            success_count += 1

            # 진행 상황 출력 (매 100개마다)
            if i % 100 == 0:
                print(f"  ➕ 진행 중: {i}/{len(md_files)} ({success_count} 성공)")

        except Exception as e:
            error_count += 1
            if error_count <= 10:  # 처음 10개 에러만 출력
                print(f"  ⚠️  에러: {md_file.name} - {e}")

    print()
    print(f"  ✅ 재인덱싱 완료!")
    print(f"     - 성공: {success_count}개")
    print(f"     - 에러: {error_count}개")
    print()

    # Network와 Repomix 저장
    network_store.save_metadata()
    repomix_store.save_index()

    print("  💾 메타데이터 저장 완료")
    print()

    # Step 4: 검증
    print("✅ Step 4: 재빌드 검증")
    print("━" * 60)

    # 파일 존재 확인
    assert network_file.exists(), "network_metadata.json이 생성되지 않았습니다"
    assert repomix_file.exists(), "repomix_index.json이 생성되지 않았습니다"

    # 파일 크기 확인
    network_size = network_file.stat().st_size
    repomix_size = repomix_file.stat().st_size

    print(f"  ✅ network_metadata.json: {network_size:,} bytes")
    print(f"  ✅ repomix_index.json: {repomix_size:,} bytes")
    print()

    # 통계 출력
    network_count = len(network_store.metadata["files"])
    repomix_count = len(repomix_store.index["files"])

    print("  📊 재빌드 통계:")
    print(f"     - Network: {network_count}개 파일")
    print(f"     - Repomix: {repomix_count}개 파일")
    print()

    print("━" * 60)
    print("🎉 데이터베이스 재빌드 완료!")
    print("━" * 60)
    print()


if __name__ == "__main__":
    rebuild_databases()
