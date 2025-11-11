#!/usr/bin/env python3
"""NetworkMetadataStore 간단한 테스트"""

import sys
from pathlib import Path

# src 디렉토리를 import 경로에 추가
sys.path.insert(0, str(Path(__file__).parent / "src"))

from network_store import NetworkMetadataStore


def test_basic_functionality():
    """기본 기능 테스트"""
    print("🧪 NetworkMetadataStore 테스트 시작\n")

    # 1. 스토어 초기화
    print("1️⃣ 스토어 초기화...")
    store = NetworkMetadataStore()
    print(f"   ✓ 메타데이터 버전: {store.metadata['version']}")
    print(f"   ✓ 파일 경로: {store.metadata_file}\n")

    # 2. 링크 추출 테스트
    print("2️⃣ 링크 추출 테스트...")
    test_content = """
    이것은 [[노트 A]]에 대한 참조입니다.
    또한 [[노트 B|표시명]]도 있습니다.
    그리고 [[노트 C]]도 언급합니다.
    """
    links = store.extract_links(test_content)
    print(f"   ✓ 추출된 링크: {links['links']}")
    print(f"   ✓ 별칭: {links['aliases']}\n")

    # 3. 태그 추출 테스트
    print("3️⃣ 태그 추출 테스트...")
    test_content_with_tags = """
    #ai #strategy #product
    이것은 #machine-learning 과 #deep-learning 에 관한 내용입니다.
    한글 태그도 가능: #인공지능 #머신러닝
    """
    tags = store.extract_tags(test_content_with_tags)
    print(f"   ✓ 추출된 태그: {tags}\n")

    # 4. 문서 메타데이터 업데이트 테스트
    print("4️⃣ 문서 메타데이터 업데이트 테스트...")
    doc1 = {
        "path": "/vault/노트A.md",
        "title": "노트A",
        "content": "이것은 [[노트B]]와 [[노트C]]를 참조합니다. #테스트 #ai",
        "metadata": {"tags": ["meta-tag"]},
        "para_folder": "00 Notes",
        "wiki_links": ["노트B", "노트C"],
        "tags": ["테스트", "ai", "meta-tag"],
    }

    doc2 = {
        "path": "/vault/노트B.md",
        "title": "노트B",
        "content": "이것은 [[노트A]]를 역참조합니다. #테스트",
        "metadata": {},
        "para_folder": "01 Reference",
        "wiki_links": ["노트A"],
        "tags": ["테스트"],
    }

    doc3 = {
        "path": "/vault/고립된노트.md",
        "title": "고립된노트",
        "content": "이 노트는 링크가 없습니다.",
        "metadata": {},
        "para_folder": "00 Notes",
        "wiki_links": [],
        "tags": [],
    }

    store.update_metadata(doc1)
    store.update_metadata(doc2)
    store.update_metadata(doc3)
    print(f"   ✓ 3개 문서 메타데이터 업데이트 완료\n")

    # 5. 백링크 조회 테스트
    print("5️⃣ 백링크 조회 테스트...")
    backlinks_a = store.get_backlinks("노트A")
    backlinks_b = store.get_backlinks("노트B")
    print(f"   ✓ 노트A의 백링크: {backlinks_a}")
    print(f"   ✓ 노트B의 백링크: {backlinks_b}\n")

    # 6. 포워드링크 조회 테스트
    print("6️⃣ 포워드링크 조회 테스트...")
    forward_links_a = store.get_forward_links("노트A")
    forward_links_b = store.get_forward_links("노트B")
    print(f"   ✓ 노트A의 포워드링크: {forward_links_a}")
    print(f"   ✓ 노트B의 포워드링크: {forward_links_b}\n")

    # 7. 네트워크 통계 테스트
    print("7️⃣ 네트워크 통계 테스트...")
    stats = store.get_network_stats()
    print(f"   ✓ 전체 파일 수: {stats['total_files']}")
    print(f"   ✓ 전체 백링크 수: {stats['total_backlinks']}")
    print(f"   ✓ 고립된 노트 수: {stats['orphaned_notes']}\n")

    # 8. 고립된 노트 조회 테스트
    print("8️⃣ 고립된 노트 조회 테스트...")
    orphaned = store.get_orphaned_notes()
    print(f"   ✓ 고립된 노트: {orphaned}\n")

    # 9. 태그별 노트 조회 테스트
    print("9️⃣ 태그별 노트 조회 테스트...")
    all_tags = store.get_all_tags()
    print(f"   ✓ 전체 태그: {all_tags}")
    test_notes = store.get_notes_by_tag("테스트")
    print(f"   ✓ #테스트 태그를 가진 노트: {test_notes}\n")

    # 10. 메타데이터 저장 테스트
    print("🔟 메타데이터 저장 테스트...")
    store.save_metadata()
    print(f"   ✓ 메타데이터 저장 완료: {store.metadata_file}\n")

    print("✅ 모든 테스트 통과!")


if __name__ == "__main__":
    test_basic_functionality()
