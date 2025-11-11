#!/usr/bin/env python3
"""
Context Packer 테스트 스크립트

ContextPacker가 정상적으로 작동하는지 테스트합니다.
"""

import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from vector_store import VectorStore
from network_store import NetworkMetadataStore
from repomix_store import RepomixIndexStore
from context_packer import ContextPacker


def test_context_packer():
    """Context Packer 기본 테스트"""

    print("╔══════════════════════════════════════════════════════════╗")
    print("║                                                          ║")
    print("║         Context Packer 테스트                            ║")
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

    # Step 2: ContextPacker 초기화
    print("📊 Step 2: ContextPacker 초기화")
    print("━" * 60)

    try:
        context_packer = ContextPacker(
            vector_store, network_store, repomix_store, max_tokens=10000
        )
        print("  ✅ ContextPacker 초기화 완료")
        print()
    except Exception as e:
        print(f"  ❌ ContextPacker 초기화 실패: {e}")
        return False

    # Step 3: 테스트용 노트 찾기
    print("🔍 Step 3: 테스트용 노트 찾기")
    print("━" * 60)

    # network_store에서 첫 번째 노트 제목 가져오기
    try:
        if not network_store.metadata.get("files"):
            print("  ⚠️ 인덱싱된 노트가 없습니다.")
            return False

        # 첫 번째 파일 선택
        first_file = next(iter(network_store.metadata["files"].values()))
        test_note_title = first_file["title"]
        print(f"  📄 테스트 노트: '{test_note_title}'")
        print()
    except Exception as e:
        print(f"  ❌ 테스트 노트 선택 실패: {e}")
        return False

    # Step 4: 컨텍스트 패키징
    print("📦 Step 4: 컨텍스트 패키징")
    print("━" * 60)

    try:
        packed_content = context_packer.pack_note(
            note_title=test_note_title,
            include_backlinks=True,
            include_forward_links=True,
            include_semantic_related=True,
            max_backlinks=5,
            max_forward_links=5,
            max_semantic_related=3,
        )

        print("  ✅ 컨텍스트 패키징 완료")
        print(f"  📏 결과 길이: {len(packed_content):,} 문자")
        print()

        # 결과 미리보기 (처음 500자)
        print("📄 Step 5: 결과 미리보기")
        print("━" * 60)
        print(packed_content[:500])
        print("\n... (생략)\n")

    except Exception as e:
        print(f"  ❌ 컨텍스트 패키징 실패: {e}")
        import traceback
        traceback.print_exc()
        return False

    # 최종 결과
    print("━" * 60)
    print("🎉 Context Packer 테스트 완료!")
    print("━" * 60)
    print()

    return True


if __name__ == "__main__":
    success = test_context_packer()
    sys.exit(0 if success else 1)
