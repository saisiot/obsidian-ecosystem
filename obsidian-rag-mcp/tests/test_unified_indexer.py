"""UnifiedIndexer 테스트"""

import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

# 프로젝트 루트를 sys.path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from indexer import UnifiedIndexer


def test_unified_indexer_initialization():
    """UnifiedIndexer 초기화 테스트"""
    # Mock stores
    vector_store = MagicMock()
    network_store = MagicMock()
    repomix_store = MagicMock()

    # UnifiedIndexer 생성
    indexer = UnifiedIndexer(vector_store, network_store, repomix_store)

    # 검증
    assert indexer.vector_store == vector_store
    assert indexer.network_store == network_store
    assert indexer.repomix_store == repomix_store
    print("✅ UnifiedIndexer 초기화 테스트 통과")


def test_unified_indexer_update_no_changes():
    """변경사항이 없을 때 update_index() 테스트"""
    # Mock stores
    vector_store = MagicMock()
    network_store = MagicMock()
    repomix_store = MagicMock()

    # UnifiedIndexer 생성
    indexer = UnifiedIndexer(vector_store, network_store, repomix_store)

    # check_updates() mock - 변경사항 없음
    with patch.object(indexer, "check_updates") as mock_check:
        mock_check.return_value = {"new": [], "modified": [], "deleted": []}

        # update_index() 실행
        indexer.update_index()

        # 검증: 아무 store도 업데이트되지 않음
        vector_store.add_document.assert_not_called()
        vector_store.update_document.assert_not_called()
        vector_store.delete_document.assert_not_called()
        network_store.update_metadata.assert_not_called()
        repomix_store.update_index.assert_not_called()

    print("✅ 변경사항 없음 테스트 통과")


def test_unified_indexer_update_with_new_file():
    """새 파일 추가 시 update_index() 테스트"""
    # Temporary directory for test
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Mock stores
        vector_store = MagicMock()
        network_store = MagicMock()
        repomix_store = MagicMock()

        # Mock 파일 경로 설정 (실제 Path 객체)
        network_store.metadata_file = tmpdir / "network_metadata.json"
        repomix_store.index_file = tmpdir / "repomix_index.json"

        # UnifiedIndexer 생성
        indexer = UnifiedIndexer(vector_store, network_store, repomix_store)

        # 테스트 파일 생성
        test_file = tmpdir / "test_note.md"
        test_file.write_text(
            """---
tags: [test, demo]
---
# Test Note

This is a [[linked note]] with #tag
"""
        )

        # Mock parser
        mock_doc = {
            "path": str(test_file),
            "title": "test_note",
            "content": "This is a [[linked note]] with #tag",
            "metadata": {"tags": ["test", "demo"]},
            "wiki_links": ["linked note"],
            "tags": ["test", "demo", "tag"],
            "para_folder": "Projects",
            "modified_time": 1234567890,
        }

        # Mock methods
        with patch.object(indexer, "check_updates") as mock_check, patch.object(
            indexer.parser, "parse_file"
        ) as mock_parse, patch.object(indexer, "get_file_hash") as mock_hash, patch(
            "indexer.METADATA_FILE", tmpdir / "index_metadata.json"
        ), patch(
            "indexer.BACKUP_DIR", tmpdir / "backup"
        ):

            mock_check.return_value = {
                "new": [test_file],
                "modified": [],
                "deleted": [],
            }
            mock_parse.return_value = mock_doc
            mock_hash.return_value = "abcd1234"

            # Mock metadata file operations
            indexer.metadata = {"indexed_files": {}}
            with patch.object(indexer, "save_metadata"):
                # update_index() 실행
                indexer.update_index()

            # 검증: 모든 store가 업데이트됨
            vector_store.add_document.assert_called_once()
            network_store.update_metadata.assert_called_once()
            repomix_store.update_index.assert_called_once()
            network_store.save_metadata.assert_called_once()
            repomix_store.save_index.assert_called_once()

            # 네트워크 메타데이터 검증
            network_call = network_store.update_metadata.call_args[0][0]
            assert network_call["title"] == "test_note"
            assert network_call["forward_links"] == ["linked note"]
            assert "test" in network_call["tags"]

    print("✅ 새 파일 추가 테스트 통과")


def test_unified_indexer_update_with_deletion():
    """파일 삭제 시 update_index() 테스트"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Mock stores
        vector_store = MagicMock()
        network_store = MagicMock()
        repomix_store = MagicMock()

        # Mock 파일 경로 설정 (실제 Path 객체)
        network_store.metadata_file = tmpdir / "network_metadata.json"
        repomix_store.index_file = tmpdir / "repomix_index.json"

        # UnifiedIndexer 생성
        indexer = UnifiedIndexer(vector_store, network_store, repomix_store)

        # 삭제된 파일 경로
        deleted_file = Path("/tmp/deleted_note.md")

        # Mock methods
        with patch.object(indexer, "check_updates") as mock_check, patch(
            "indexer.METADATA_FILE", tmpdir / "index_metadata.json"
        ), patch("indexer.BACKUP_DIR", tmpdir / "backup"):
            mock_check.return_value = {
                "new": [],
                "modified": [],
                "deleted": [deleted_file],
            }

            # Mock metadata
            indexer.metadata = {"indexed_files": {str(deleted_file): "hash123"}}
            with patch.object(indexer, "save_metadata"):
                # update_index() 실행
                indexer.update_index()

            # 검증: 모든 store에서 삭제됨
            vector_store.delete_document.assert_called_once_with(str(deleted_file))
            network_store.delete_metadata.assert_called_once_with(str(deleted_file))
            repomix_store.delete_index.assert_called_once_with(str(deleted_file))

        print("✅ 파일 삭제 테스트 통과")


def test_unified_indexer_backward_compatibility():
    """IncrementalIndexer와의 하위 호환성 테스트"""
    from indexer import IncrementalIndexer

    # Mock store
    vector_store = MagicMock()

    # IncrementalIndexer는 여전히 작동해야 함
    base_indexer = IncrementalIndexer(vector_store)
    assert base_indexer.vector_store == vector_store
    assert hasattr(base_indexer, "check_updates")
    assert hasattr(base_indexer, "update_index")

    print("✅ 하위 호환성 테스트 통과")


if __name__ == "__main__":
    print("🧪 UnifiedIndexer 테스트 시작\n")

    test_unified_indexer_initialization()
    test_unified_indexer_update_no_changes()
    test_unified_indexer_update_with_new_file()
    test_unified_indexer_update_with_deletion()
    test_unified_indexer_backward_compatibility()

    print("\n✅ 모든 테스트 통과!")
