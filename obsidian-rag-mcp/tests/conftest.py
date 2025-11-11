"""Pytest fixtures for integration tests

통합 테스트를 위한 공통 fixture 및 helper 함수를 제공합니다.
"""

import shutil
import sys
from pathlib import Path

import pytest

# 프로젝트 루트를 sys.path에 추가
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from config import VAULT_PATH  # noqa: E402
from indexer import UnifiedIndexer  # noqa: E402
from network_store import NetworkMetadataStore  # noqa: E402
from repomix_store import RepomixIndexStore  # noqa: E402
from vector_store import VectorStore  # noqa: E402


@pytest.fixture(scope="function")
def temp_vault(tmp_path):
    """임시 Vault 디렉토리 생성

    실제 Vault를 건드리지 않고 테스트용 파일을 생성합니다.

    Yields:
        Path: 임시 Vault 경로
    """
    vault_path = tmp_path / "test_vault"
    vault_path.mkdir(parents=True, exist_ok=True)

    # PARA 폴더 구조 생성
    (vault_path / "00 Notes").mkdir(exist_ok=True)
    (vault_path / "01 Reference").mkdir(exist_ok=True)
    (vault_path / "02 Journals").mkdir(exist_ok=True)
    (vault_path / "04 Outputs").mkdir(exist_ok=True)

    yield vault_path

    # Cleanup
    if vault_path.exists():
        shutil.rmtree(vault_path)


@pytest.fixture(scope="function")
def temp_data_dir(tmp_path):
    """임시 데이터 디렉토리 생성

    ChromaDB, 메타데이터, 백업 파일을 저장할 임시 디렉토리를 생성합니다.

    Yields:
        dict: {"root": Path, "chroma": Path, "metadata": Path, "backup": Path}
    """
    data_dir = tmp_path / "test_data"
    data_dir.mkdir(parents=True, exist_ok=True)

    chroma_dir = data_dir / "chroma_db"
    chroma_dir.mkdir(exist_ok=True)

    backup_dir = data_dir / "backup"
    backup_dir.mkdir(exist_ok=True)

    yield {
        "root": data_dir,
        "chroma": chroma_dir,
        "metadata": data_dir / "index_metadata.json",
        "network_metadata": data_dir / "network_metadata.json",
        "repomix_index": data_dir / "repomix_index.json",
        "backup": backup_dir,
    }

    # Cleanup
    if data_dir.exists():
        shutil.rmtree(data_dir)


@pytest.fixture(scope="function")
def sample_notes(temp_vault):
    """샘플 노트 파일 생성

    다양한 링크, 태그, 구조를 가진 테스트용 노트를 생성합니다.

    Args:
        temp_vault: 임시 Vault 경로

    Returns:
        list[Path]: 생성된 노트 파일 경로 리스트
    """
    notes = []

    # Note 1: 기본 노트 (forward links, tags)
    note1 = temp_vault / "00 Notes" / "Note A.md"
    note1.write_text(
        """---
tags: [python, testing]
---
# Note A

This is a test note that links to [[Note B]] and [[Note C]].

It also has inline tags: #important #draft
"""
    )
    notes.append(note1)

    # Note 2: 백링크 대상
    note2 = temp_vault / "00 Notes" / "Note B.md"
    note2.write_text(
        """---
tags: [research]
---
# Note B

This note is referenced by Note A.

Links to [[Note C]].

#project #active
"""
    )
    notes.append(note2)

    # Note 3: 다중 백링크 대상
    note3 = temp_vault / "01 Reference" / "Note C.md"
    note3.write_text(
        """# Note C

Referenced by both Note A and Note B.

No forward links, only backlinks.

#reference #core
"""
    )
    notes.append(note3)

    # Note 4: 고립된 노트 (no links)
    note4 = temp_vault / "02 Journals" / "Orphaned Note.md"
    note4.write_text(
        """# Orphaned Note

This note has no links at all.

#lonely
"""
    )
    notes.append(note4)

    # Note 5: 긴 컨텐츠 (청킹 테스트)
    note5 = temp_vault / "04 Outputs" / "Long Document.md"
    long_content = "# Long Document\n\n" + "\n\n".join(
        [f"## Section {i}\n\nContent for section {i}. " * 20 for i in range(1, 11)]
    )
    note5.write_text(long_content)
    notes.append(note5)

    return notes


@pytest.fixture(scope="function")
def test_stores(temp_data_dir, monkeypatch):
    """테스트용 3개 Store 인스턴스 생성

    ChromaDB, NetworkMetadataStore, RepomixIndexStore를 임시 디렉토리에 생성합니다.

    Args:
        temp_data_dir: 임시 데이터 디렉토리
        monkeypatch: pytest monkeypatch fixture

    Yields:
        dict: {"vector": VectorStore, "network": NetworkMetadataStore, "repomix": RepomixIndexStore}
    """
    # config.py의 경로를 임시 디렉토리로 패치
    monkeypatch.setattr("config.CHROMA_PATH", temp_data_dir["chroma"])
    monkeypatch.setattr("config.METADATA_FILE", temp_data_dir["metadata"])
    monkeypatch.setattr("config.BACKUP_DIR", temp_data_dir["backup"])
    monkeypatch.setattr("vector_store.CHROMA_PATH", temp_data_dir["chroma"])

    # 실제 store 인스턴스 생성
    vector_store = VectorStore()

    network_store = NetworkMetadataStore(
        metadata_file=temp_data_dir["network_metadata"]
    )

    repomix_store = RepomixIndexStore(index_file=temp_data_dir["repomix_index"])

    yield {
        "vector": vector_store,
        "network": network_store,
        "repomix": repomix_store,
    }

    # Cleanup: ChromaDB 컬렉션 삭제
    try:
        # 컬렉션 완전 삭제
        from config import COLLECTION_NAME

        try:
            vector_store.client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass
    except Exception:
        pass


@pytest.fixture(scope="function")
def unified_indexer(test_stores, temp_vault, temp_data_dir, monkeypatch):
    """UnifiedIndexer 인스턴스 생성

    테스트용 stores와 temp_vault를 사용하는 UnifiedIndexer를 생성합니다.

    Args:
        test_stores: 테스트용 stores
        temp_vault: 임시 Vault 경로
        temp_data_dir: 임시 데이터 디렉토리
        monkeypatch: pytest monkeypatch fixture

    Yields:
        UnifiedIndexer: 테스트용 UnifiedIndexer 인스턴스
    """
    # config.py의 VAULT_PATH를 임시 Vault로 패치
    monkeypatch.setattr("config.VAULT_PATH", temp_vault)
    monkeypatch.setattr("indexer.VAULT_PATH", temp_vault)
    monkeypatch.setattr("obsidian_parser.VAULT_PATH", temp_vault)
    monkeypatch.setattr("repomix_store.VAULT_PATH", temp_vault)

    # indexer.py의 BACKUP_DIR도 패치
    monkeypatch.setattr("indexer.BACKUP_DIR", temp_data_dir["backup"])
    monkeypatch.setattr("indexer.METADATA_FILE", temp_data_dir["metadata"])

    # UnifiedIndexer 생성
    indexer = UnifiedIndexer(
        vector_store=test_stores["vector"],
        network_store=test_stores["network"],
        repomix_store=test_stores["repomix"],
    )

    # vault_path 오버라이드
    indexer.vault_path = temp_vault

    # metadata 초기화 (indexed_files 키 추가)
    indexer.metadata = {"last_update": 0, "indexed_files": {}}

    yield indexer


@pytest.fixture(scope="function")
def real_vault_files():
    """실제 Vault의 마크다운 파일 리스트

    VAULT_PATH에 실제 파일이 있는 경우에만 사용합니다.
    파일이 없으면 테스트를 스킵합니다.

    Returns:
        list[Path]: 실제 Vault의 .md 파일 리스트
    """
    if not VAULT_PATH.exists():
        pytest.skip("실제 Vault가 존재하지 않습니다")

    md_files = list(VAULT_PATH.rglob("*.md"))

    if len(md_files) == 0:
        pytest.skip("실제 Vault에 마크다운 파일이 없습니다")

    return md_files


@pytest.fixture(scope="function")
def performance_sample_vault(temp_vault):
    """성능 테스트용 대량 샘플 노트 생성

    100개의 노트를 생성하여 성능 테스트에 사용합니다.

    Args:
        temp_vault: 임시 Vault 경로

    Returns:
        list[Path]: 생성된 100개 노트 파일 경로 리스트
    """
    notes = []

    for i in range(100):
        # 폴더를 순환하며 분산 배치
        folders = ["00 Notes", "01 Reference", "02 Journals", "04 Outputs"]
        folder = folders[i % len(folders)]

        note_path = temp_vault / folder / f"Note_{i:03d}.md"

        # 다양한 링크 패턴 생성
        links = []
        if i > 0:
            links.append(f"[[Note_{i-1:03d}]]")
        if i < 99:
            links.append(f"[[Note_{i+1:03d}]]")

        content = f"""---
tags: [tag{i % 10}, batch]
---
# Note {i:03d}

This is test note number {i}.

Links: {' '.join(links)}

Content: {"Sample content. " * 10}

#test #performance
"""
        note_path.write_text(content)
        notes.append(note_path)

    return notes


# Helper functions


def count_documents_in_chroma(vector_store: VectorStore) -> int:
    """ChromaDB의 문서 수 조회

    Args:
        vector_store: VectorStore 인스턴스

    Returns:
        int: 저장된 문서(청크) 수
    """
    result = vector_store.collection.get()
    return len(result["ids"])


def get_unique_files_in_chroma(vector_store: VectorStore) -> set:
    """ChromaDB에 저장된 고유 파일 경로 집합

    Args:
        vector_store: VectorStore 인스턴스

    Returns:
        set: 고유 파일 경로 집합
    """
    result = vector_store.collection.get()
    paths = {metadata["path"] for metadata in result["metadatas"]}
    return paths


def verify_three_db_sync(
    vector_store: VectorStore,
    network_store: NetworkMetadataStore,
    repomix_store: RepomixIndexStore,
) -> bool:
    """3개 DB의 동기화 상태 검증

    Args:
        vector_store: VectorStore 인스턴스
        network_store: NetworkMetadataStore 인스턴스
        repomix_store: RepomixIndexStore 인스턴스

    Returns:
        bool: 동기화 상태 (True: 동기화됨, False: 불일치)
    """
    chroma_files = get_unique_files_in_chroma(vector_store)
    network_files = set(network_store.metadata["files"].keys())
    repomix_files = set(repomix_store.index["files"].keys())

    return chroma_files == network_files == repomix_files


def print_db_stats(
    vector_store: VectorStore,
    network_store: NetworkMetadataStore,
    repomix_store: RepomixIndexStore,
):
    """3개 DB 통계 출력 (디버깅용)

    Args:
        vector_store: VectorStore 인스턴스
        network_store: NetworkMetadataStore 인스턴스
        repomix_store: RepomixIndexStore 인스턴스
    """
    chroma_count = count_documents_in_chroma(vector_store)
    chroma_files = len(get_unique_files_in_chroma(vector_store))
    network_count = len(network_store.metadata["files"])
    repomix_count = len(repomix_store.index["files"])

    print("\n📊 DB 통계:")
    print(f"  - ChromaDB: {chroma_count}개 청크, {chroma_files}개 파일")
    print(f"  - NetworkMetadata: {network_count}개 파일")
    print(f"  - RepomixIndex: {repomix_count}개 파일")
