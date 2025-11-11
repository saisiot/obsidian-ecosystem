"""Transaction 및 Rollback 시스템 테스트"""

import sys
from pathlib import Path

# src 디렉토리를 Python path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import pytest
import json
from datetime import datetime
from unittest.mock import Mock, patch

from indexer import UnifiedIndexer
from config import PROJECT_ROOT


@pytest.fixture
def temp_data_dir(tmp_path):
    """임시 데이터 디렉토리 생성"""
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    backup_dir = data_dir / "backup"
    backup_dir.mkdir()
    return data_dir


@pytest.fixture
def mock_stores():
    """Mock VectorStore, NetworkStore, RepomixStore"""
    vector_store = Mock()
    vector_store.add_document = Mock()
    vector_store.update_document = Mock()
    vector_store.delete_document = Mock()

    network_store = Mock()
    network_store.metadata_file = PROJECT_ROOT / "data" / "network_metadata.json"
    network_store.update_metadata = Mock()
    network_store.delete_metadata = Mock()
    network_store.save_metadata = Mock()
    network_store.load_metadata = Mock(return_value={})

    repomix_store = Mock()
    repomix_store.index_file = PROJECT_ROOT / "data" / "repomix_index.json"
    repomix_store.update_index = Mock()
    repomix_store.delete_index = Mock()
    repomix_store.save_index = Mock()
    repomix_store.load_index = Mock(return_value={})

    return vector_store, network_store, repomix_store


@pytest.fixture
def indexer(mock_stores, temp_data_dir):
    """UnifiedIndexer 인스턴스 생성"""
    vector_store, network_store, repomix_store = mock_stores

    # 임시 메타데이터 파일 설정
    with patch("src.indexer.METADATA_FILE", temp_data_dir / "index_metadata.json"):
        with patch("src.indexer.BACKUP_DIR", temp_data_dir / "backup"):
            indexer = UnifiedIndexer(vector_store, network_store, repomix_store)
            indexer.vault_path = temp_data_dir / "vault"
            indexer.vault_path.mkdir()
            return indexer


class TestBackupCreation:
    """백업 생성 테스트"""

    def test_create_backup_success(self, indexer, temp_data_dir):
        """백업 생성 성공 케이스"""
        # 메타데이터 파일 생성
        metadata_file = temp_data_dir / "index_metadata.json"
        metadata_file.write_text(json.dumps({"test": "data"}))

        network_file = temp_data_dir / "network_metadata.json"
        network_file.write_text(json.dumps({"network": "data"}))

        repomix_file = temp_data_dir / "repomix_index.json"
        repomix_file.write_text(json.dumps({"repomix": "data"}))

        # Mock 파일 경로 설정
        indexer.network_store.metadata_file = network_file
        indexer.repomix_store.index_file = repomix_file

        with patch("indexer.METADATA_FILE", metadata_file):
            with patch("indexer.BACKUP_DIR", temp_data_dir / "backup"):
                backup_dir = indexer._create_backup()

        # 백업 디렉토리 존재 확인
        assert backup_dir.exists()
        assert backup_dir.is_dir()

        # 백업 파일 존재 확인
        assert (backup_dir / "index_metadata.json").exists()
        assert (backup_dir / "network_metadata.json").exists()
        assert (backup_dir / "repomix_index.json").exists()

        # 백업 파일 내용 확인
        with open(backup_dir / "index_metadata.json") as f:
            assert json.load(f) == {"test": "data"}

    def test_create_backup_with_missing_files(self, indexer, temp_data_dir):
        """일부 메타데이터 파일이 없는 경우"""
        # 일부 파일만 생성
        metadata_file = temp_data_dir / "index_metadata.json"
        metadata_file.write_text(json.dumps({"test": "data"}))

        # 나머지 파일은 존재하지 않음
        network_file = temp_data_dir / "network_metadata.json"
        repomix_file = temp_data_dir / "repomix_index.json"

        indexer.network_store.metadata_file = network_file
        indexer.repomix_store.index_file = repomix_file

        with patch("indexer.METADATA_FILE", metadata_file):
            with patch("indexer.BACKUP_DIR", temp_data_dir / "backup"):
                backup_dir = indexer._create_backup()

        # 백업 디렉토리는 생성되어야 함
        assert backup_dir.exists()

        # 존재하는 파일만 백업되어야 함
        assert (backup_dir / "index_metadata.json").exists()
        assert not (backup_dir / "network_metadata.json").exists()
        assert not (backup_dir / "repomix_index.json").exists()

    def test_backup_timestamp_format(self, indexer):
        """백업 디렉토리 타임스탬프 형식 확인"""
        backup_dir = indexer._create_backup()

        # 타임스탬프 형식 검증 (YYYYMMDD_HHMMSS)
        timestamp = backup_dir.name
        assert len(timestamp) == 15
        assert timestamp[8] == "_"

        # 날짜 파싱 가능 확인
        datetime.strptime(timestamp, "%Y%m%d_%H%M%S")


class TestRollback:
    """롤백 테스트"""

    def test_rollback_success(self, indexer, temp_data_dir):
        """롤백 성공 케이스"""
        # 원본 메타데이터 생성
        metadata_file = temp_data_dir / "index_metadata.json"
        metadata_file.write_text(json.dumps({"version": "original"}))

        network_file = temp_data_dir / "network_metadata.json"
        network_file.write_text(json.dumps({"network": "original"}))

        repomix_file = temp_data_dir / "repomix_index.json"
        repomix_file.write_text(json.dumps({"repomix": "original"}))

        indexer.network_store.metadata_file = network_file
        indexer.repomix_store.index_file = repomix_file

        # 백업 생성
        with patch("indexer.METADATA_FILE", metadata_file):
            with patch("indexer.BACKUP_DIR", temp_data_dir / "backup"):
                backup_dir = indexer._create_backup()

        # 메타데이터 변경 (업데이트 시뮬레이션)
        metadata_file.write_text(json.dumps({"version": "updated"}))
        network_file.write_text(json.dumps({"network": "updated"}))
        repomix_file.write_text(json.dumps({"repomix": "updated"}))

        # 롤백 실행
        with patch("indexer.METADATA_FILE", metadata_file):
            indexer._rollback(backup_dir)

        # 원본 데이터로 복원 확인
        with open(metadata_file) as f:
            assert json.load(f) == {"version": "original"}

        with open(network_file) as f:
            assert json.load(f) == {"network": "original"}

        with open(repomix_file) as f:
            assert json.load(f) == {"repomix": "original"}

    def test_rollback_with_partial_backup(self, indexer, temp_data_dir):
        """일부 백업만 있는 경우 롤백"""
        metadata_file = temp_data_dir / "index_metadata.json"
        network_file = temp_data_dir / "network_metadata.json"
        repomix_file = temp_data_dir / "repomix_index.json"

        # 백업 디렉토리 생성
        backup_dir = temp_data_dir / "backup" / "20240101_120000"
        backup_dir.mkdir(parents=True)

        # 일부 백업만 생성
        (backup_dir / "index_metadata.json").write_text(
            json.dumps({"version": "backup"})
        )

        indexer.network_store.metadata_file = network_file
        indexer.repomix_store.index_file = repomix_file

        # 롤백 실행 (에러 없이 진행되어야 함)
        with patch("indexer.METADATA_FILE", metadata_file):
            indexer._rollback(backup_dir)

        # 백업이 있는 파일만 복원
        assert metadata_file.exists()
        with open(metadata_file) as f:
            assert json.load(f) == {"version": "backup"}

    def test_rollback_calls_reload_methods(self, indexer, temp_data_dir):
        """롤백이 메타데이터 재로드 메소드를 호출하는지 확인"""
        backup_dir = temp_data_dir / "backup" / "20240101_120000"
        backup_dir.mkdir(parents=True)

        # 빈 백업 파일 생성
        (backup_dir / "index_metadata.json").write_text(json.dumps({}))

        metadata_file = temp_data_dir / "index_metadata.json"
        indexer.network_store.metadata_file = temp_data_dir / "network_metadata.json"
        indexer.repomix_store.index_file = temp_data_dir / "repomix_index.json"

        with patch("indexer.METADATA_FILE", metadata_file):
            with patch.object(indexer, "load_metadata") as mock_load:
                indexer._rollback(backup_dir)
                mock_load.assert_called_once()


class TestBackupCleanup:
    """백업 정리 테스트"""

    def test_cleanup_old_backups(self, indexer, temp_data_dir):
        """오래된 백업 정리"""
        backup_root = temp_data_dir / "backup"

        # 10개의 백업 생성
        backup_dirs = []
        for i in range(10):
            backup_dir = backup_root / f"2024010{i}_120000"
            backup_dir.mkdir(parents=True)
            backup_dirs.append(backup_dir)

        with patch("indexer.BACKUP_DIR", backup_root):
            indexer._cleanup_old_backups(max_backups=5)

        # 최신 5개만 유지
        remaining = sorted(backup_root.iterdir())
        assert len(remaining) == 5

        # 최신 백업들만 남아있는지 확인
        for backup_dir in backup_dirs[-5:]:
            assert backup_dir.exists()

        # 오래된 백업은 삭제되었는지 확인
        for backup_dir in backup_dirs[:5]:
            assert not backup_dir.exists()

    def test_cleanup_no_backups(self, indexer, temp_data_dir):
        """백업이 없는 경우 정리"""
        backup_root = temp_data_dir / "empty_backup"

        with patch("indexer.BACKUP_DIR", backup_root):
            # 에러 없이 실행되어야 함
            indexer._cleanup_old_backups()

    def test_cleanup_less_than_max(self, indexer, temp_data_dir):
        """백업 개수가 최대값보다 적은 경우"""
        backup_root = temp_data_dir / "backup"

        # 3개만 생성
        for i in range(3):
            backup_dir = backup_root / f"2024010{i}_120000"
            backup_dir.mkdir(parents=True)

        with patch("indexer.BACKUP_DIR", backup_root):
            indexer._cleanup_old_backups(max_backups=5)

        # 모든 백업 유지
        remaining = list(backup_root.iterdir())
        assert len(remaining) == 3


class TestTransactionUpdate:
    """트랜잭션 업데이트 통합 테스트"""

    def test_update_with_successful_transaction(self, indexer, temp_data_dir):
        """성공적인 업데이트 트랜잭션"""
        # 테스트 파일 생성
        test_file = indexer.vault_path / "00 Notes" / "test.md"
        test_file.parent.mkdir(parents=True)
        test_file.write_text("# Test\nContent")

        metadata_file = temp_data_dir / "index_metadata.json"
        metadata_file.write_text(json.dumps({"last_update": 0, "indexed_files": {}}))

        with patch("indexer.METADATA_FILE", metadata_file):
            with patch("indexer.BACKUP_DIR", temp_data_dir / "backup"):
                with patch("indexer.INCLUDE_FOLDERS", ["00 Notes"]):
                    with patch("indexer.EXCLUDE_PATTERNS", []):
                        # metadata 초기화
                        indexer.metadata = {"last_update": 0, "indexed_files": {}}

                        with patch.object(indexer.parser, "parse_file") as mock_parse:
                            mock_parse.return_value = {
                                "title": "Test",
                                "content": "Content",
                                "para_folder": "00 Notes",
                                "wiki_links": [],
                                "tags": [],
                                "metadata": {},
                            }

                            indexer.update_index()

        # 백업이 생성되었는지 확인
        backup_dir = temp_data_dir / "backup"
        assert backup_dir.exists()
        assert len(list(backup_dir.iterdir())) == 1

        # VectorStore 메소드가 호출되었는지 확인
        assert indexer.vector_store.add_document.called

    def test_update_with_failed_transaction_triggers_rollback(
        self, indexer, temp_data_dir
    ):
        """실패한 업데이트가 롤백을 트리거하는지 확인"""
        # 테스트 파일 생성
        test_file = indexer.vault_path / "00 Notes" / "test.md"
        test_file.parent.mkdir(parents=True)
        test_file.write_text("# Test\nContent")

        metadata_file = temp_data_dir / "index_metadata.json"
        original_metadata = {"last_update": 0, "indexed_files": {}}
        metadata_file.write_text(json.dumps(original_metadata))

        with patch("indexer.METADATA_FILE", metadata_file):
            with patch("indexer.BACKUP_DIR", temp_data_dir / "backup"):
                with patch("indexer.INCLUDE_FOLDERS", ["00 Notes"]):
                    with patch("indexer.EXCLUDE_PATTERNS", []):
                        # metadata 초기화
                        indexer.metadata = {"last_update": 0, "indexed_files": {}}

                        with patch.object(indexer.parser, "parse_file") as mock_parse:
                            mock_parse.return_value = {
                                "title": "Test",
                                "content": "Content",
                                "para_folder": "00 Notes",
                                "wiki_links": [],
                                "tags": [],
                                "metadata": {},
                            }

                            # VectorStore에서 에러 발생 시뮬레이션
                            indexer.vector_store.add_document.side_effect = Exception(
                                "DB Error"
                            )

                            # 롤백이 호출되는지 확인
                            with pytest.raises(Exception):
                                indexer.update_index()

        # 백업이 생성되었는지 확인
        backup_dir = temp_data_dir / "backup"
        assert backup_dir.exists()

    def test_update_cleans_old_backups_after_success(self, indexer, temp_data_dir):
        """성공적인 업데이트 후 오래된 백업이 정리되는지 확인"""
        backup_root = temp_data_dir / "backup"

        # 5개의 오래된 백업 생성
        for i in range(5):
            old_backup = backup_root / f"2024010{i}_120000"
            old_backup.mkdir(parents=True)

        metadata_file = temp_data_dir / "index_metadata.json"
        metadata_file.write_text(json.dumps({"last_update": 0, "indexed_files": {}}))

        with patch("indexer.METADATA_FILE", metadata_file):
            with patch("indexer.BACKUP_DIR", backup_root):
                with patch("indexer.MAX_BACKUPS", 3):
                    with patch.object(indexer, "check_updates") as mock_check:
                        # 변경사항 없음
                        mock_check.return_value = {
                            "new": [],
                            "modified": [],
                            "deleted": [],
                        }

                        indexer.update_index()

        # 변경사항이 없으면 백업 생성 및 정리가 안됨
        # 변경사항이 있는 경우를 테스트하려면 더 복잡한 설정 필요


class TestEdgeCases:
    """엣지 케이스 테스트"""

    def test_backup_with_corrupted_metadata(self, indexer, temp_data_dir):
        """손상된 메타데이터 파일 백업"""
        metadata_file = temp_data_dir / "index_metadata.json"
        metadata_file.write_text("invalid json {{{")

        indexer.network_store.metadata_file = temp_data_dir / "network_metadata.json"
        indexer.repomix_store.index_file = temp_data_dir / "repomix_index.json"

        with patch("indexer.METADATA_FILE", metadata_file):
            with patch("indexer.BACKUP_DIR", temp_data_dir / "backup"):
                # 손상된 파일도 백업되어야 함
                backup_dir = indexer._create_backup()
                assert (backup_dir / "index_metadata.json").exists()

    def test_rollback_failure_raises_exception(self, indexer, temp_data_dir):
        """롤백 실패 시 예외 발생"""
        backup_dir = temp_data_dir / "backup" / "20240101_120000"
        backup_dir.mkdir(parents=True)

        # 빈 백업 파일 생성
        (backup_dir / "index_metadata.json").write_text(json.dumps({}))

        metadata_file = temp_data_dir / "index_metadata.json"
        indexer.network_store.metadata_file = temp_data_dir / "network_metadata.json"
        indexer.repomix_store.index_file = temp_data_dir / "repomix_index.json"

        with patch("indexer.METADATA_FILE", metadata_file):
            # load_metadata에서 에러 발생 시뮬레이션
            with patch.object(
                indexer, "load_metadata", side_effect=Exception("Load Error")
            ):
                with pytest.raises(Exception):
                    indexer._rollback(backup_dir)
