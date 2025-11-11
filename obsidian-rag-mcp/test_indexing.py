#!/usr/bin/env python
"""인덱싱 테스트 스크립트"""

import sys
from pathlib import Path

# 현재 디렉토리를 sys.path에 추가
sys.path.insert(0, str(Path(__file__).parent / "src"))

from vector_store import VectorStore
from indexer import IncrementalIndexer


def main():
    print("🚀 Obsidian RAG 인덱싱 테스트 시작...")

    # 벡터 스토어 초기화
    print("📦 벡터 스토어 초기화 중...")
    vector_store = VectorStore()

    # 인덱서 초기화
    print("🔧 인덱서 초기화 중...")
    indexer = IncrementalIndexer(vector_store)

    # 인덱싱 실행
    print("📊 인덱싱 시작...")
    indexer.update_index()

    print("\n✅ 테스트 완료!")
    print(f"📝 인덱싱된 파일 수: {len(indexer.metadata['indexed_files'])}")
    print(f"⏰ 마지막 업데이트: {indexer.metadata.get('last_update', 'Never')}")


if __name__ == "__main__":
    main()
