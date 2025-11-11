import json
import hashlib
import shutil
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Set
from config import (
    VAULT_PATH,
    METADATA_FILE,
    EXCLUDE_PATTERNS,
    BACKUP_DIR,
    MAX_BACKUPS,
)
from obsidian_parser import ObsidianParser


class IncrementalIndexer:
    """증분 인덱싱 시스템"""

    def __init__(self, vector_store):
        self.vault_path = VAULT_PATH
        self.vector_store = vector_store
        self.parser = ObsidianParser()
        self.metadata = self.load_metadata()
        self.network_store = None  # UnifiedIndexer에서 사용
        self.repomix_store = None  # UnifiedIndexer에서 사용

    def load_metadata(self) -> Dict:
        """메타데이터 로드"""
        if METADATA_FILE.exists():
            with open(METADATA_FILE, "r") as f:
                return json.load(f)
        return {"last_update": 0, "indexed_files": {}}

    def save_metadata(self):
        """메타데이터 저장"""
        METADATA_FILE.parent.mkdir(exist_ok=True)
        with open(METADATA_FILE, "w") as f:
            json.dump(self.metadata, f, indent=2)

    def get_md_files(self) -> Set[Path]:
        """Vault 전체의 모든 .md 파일 수집 (EXCLUDE_PATTERNS 제외)"""
        # vault 전체에서 .md 파일 찾기
        all_md_files = self.vault_path.rglob("*.md")

        # 제외 패턴 필터링
        filtered_files = set()
        for file in all_md_files:
            skip = False
            # 파일의 상대 경로를 문자열로 변환
            relative_path = str(file.relative_to(self.vault_path))

            # 경로의 모든 부분 확인 (폴더 및 파일명)
            path_parts = relative_path.split('/')

            for pattern in EXCLUDE_PATTERNS:
                # ".*" 패턴: 점으로 시작하는 폴더/파일 제외
                if pattern == ".*":
                    # 경로의 어느 부분이든 .으로 시작하면 제외
                    if any(part.startswith('.') for part in path_parts):
                        skip = True
                        break
                else:
                    # 일반 패턴: 경로 어디든 포함되면 제외
                    if pattern in relative_path or pattern in file.name:
                        skip = True
                        break

            if not skip:
                filtered_files.add(file)

        return filtered_files

    def get_file_hash(self, file_path: Path) -> str:
        """파일 해시 생성"""
        stat = file_path.stat()
        return hashlib.md5(f"{stat.st_mtime}_{stat.st_size}".encode()).hexdigest()

    def check_updates(self) -> Dict[str, List[Path]]:
        """변경사항 확인"""
        current_files = self.get_md_files()
        indexed_files = set(Path(p) for p in self.metadata["indexed_files"].keys())

        # 새 파일
        new_files = current_files - indexed_files

        # 삭제된 파일
        deleted_files = indexed_files - current_files

        # 수정된 파일
        modified_files = []
        for file in current_files & indexed_files:
            current_hash = self.get_file_hash(file)
            if self.metadata["indexed_files"][str(file)] != current_hash:
                modified_files.append(file)

        return {
            "new": list(new_files),
            "modified": modified_files,
            "deleted": list(deleted_files),
        }

    def update_index(self):
        """증분 업데이트 실행"""
        changes = self.check_updates()

        total_changes = sum(len(v) for v in changes.values())
        if total_changes == 0:
            print("✅ 인덱스가 최신 상태입니다.")
            return

        print(
            f"📊 변경사항 감지: 새 파일 {len(changes['new'])}, "
            f"수정 {len(changes['modified'])}, 삭제 {len(changes['deleted'])}"
        )

        # 삭제된 파일 처리
        for file in changes["deleted"]:
            self.vector_store.delete_document(str(file))
            del self.metadata["indexed_files"][str(file)]
            print(f"  ❌ 삭제: {file.name}")

        # 수정된 파일 처리
        for file in changes["modified"]:
            doc = self.parser.parse_file(file)
            self.vector_store.update_document(doc)
            self.metadata["indexed_files"][str(file)] = self.get_file_hash(file)
            print(f"  ♻️ 업데이트: {file.name}")

        # 새 파일 처리
        for file in changes["new"]:
            doc = self.parser.parse_file(file)
            self.vector_store.add_document(doc)
            self.metadata["indexed_files"][str(file)] = self.get_file_hash(file)
            print(f"  ➕ 추가: {file.name}")

        # 메타데이터 업데이트
        self.metadata["last_update"] = datetime.now().isoformat()
        self.save_metadata()

        print("✅ 인덱스 업데이트 완료!")


class UnifiedIndexer(IncrementalIndexer):
    """통합 인덱서: ChromaDB, NetworkMetadataStore, RepomixIndexStore를 동시에 업데이트"""

    def __init__(self, vector_store, network_store, repomix_store):
        """
        Args:
            vector_store: ChromaDB VectorStore 인스턴스
            network_store: NetworkMetadataStore 인스턴스
            repomix_store: RepomixIndexStore 인스턴스
        """
        super().__init__(vector_store)
        self.network_store = network_store
        self.repomix_store = repomix_store

    def _create_backup(self) -> Path:
        """업데이트 전 백업 스냅샷 생성

        Returns:
            backup_dir: 백업 디렉토리 경로
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = BACKUP_DIR / timestamp
        backup_dir.mkdir(parents=True, exist_ok=True)

        # 3개 메타데이터 파일 백업
        if METADATA_FILE.exists():
            shutil.copy(METADATA_FILE, backup_dir / "index_metadata.json")

        if self.network_store.metadata_file.exists():
            shutil.copy(
                self.network_store.metadata_file, backup_dir / "network_metadata.json"
            )

        if self.repomix_store.index_file.exists():
            shutil.copy(
                self.repomix_store.index_file, backup_dir / "repomix_index.json"
            )

        print(f"📦 백업 생성: {backup_dir.name}")
        return backup_dir

    def _rollback(self, backup_dir: Path):
        """백업에서 복원

        Args:
            backup_dir: 복원할 백업 디렉토리
        """
        try:
            print(f"🔄 롤백 시작: {backup_dir.name}")

            # 메타데이터 파일 복원
            if (backup_dir / "index_metadata.json").exists():
                shutil.copy(backup_dir / "index_metadata.json", METADATA_FILE)

            if (backup_dir / "network_metadata.json").exists():
                shutil.copy(
                    backup_dir / "network_metadata.json",
                    self.network_store.metadata_file,
                )

            if (backup_dir / "repomix_index.json").exists():
                shutil.copy(
                    backup_dir / "repomix_index.json", self.repomix_store.index_file
                )

            # 메타데이터 재로드
            self.metadata = self.load_metadata()
            self.network_store.metadata = self.network_store.load_metadata()
            self.repomix_store.index = self.repomix_store.load_index()

            print("✅ 롤백 완료")

        except Exception as e:
            print(f"❌ 롤백 실패: {e}")
            raise

    def _cleanup_old_backups(self, max_backups: int = MAX_BACKUPS):
        """오래된 백업 정리

        Args:
            max_backups: 유지할 최대 백업 개수
        """
        if not BACKUP_DIR.exists():
            return

        backups = sorted(BACKUP_DIR.iterdir(), reverse=True)

        # 최신 N개만 유지
        for old_backup in backups[max_backups:]:
            if old_backup.is_dir():
                shutil.rmtree(old_backup)
                print(f"🗑️ 오래된 백업 삭제: {old_backup.name}")

    def update_index(self):
        """3개 DB 통합 업데이트 (트랜잭션 지원)"""
        changes = self.check_updates()

        if not changes["new"] and not changes["modified"] and not changes["deleted"]:
            print("✅ 인덱스가 최신 상태입니다.")
            return

        print(
            f"📊 변경사항 감지: 새 파일 {len(changes['new'])}, "
            f"수정 {len(changes['modified'])}, 삭제 {len(changes['deleted'])}"
        )

        # 백업 생성
        backup_dir = self._create_backup()

        try:
            # Phase 1: Prepare updates for all 3 DBs
            updates = {"chroma": [], "network": [], "repomix": []}

            for file in changes["new"] + changes["modified"]:
                doc = self.parser.parse_file(file)

                # ChromaDB: full document
                updates["chroma"].append({"file": file, "doc": doc})

                # Network: extract links and tags
                updates["network"].append(
                    {
                        "path": str(file),
                        "title": doc["title"],
                        "para_folder": doc["para_folder"],
                        "forward_links": doc["wiki_links"],
                        "tags": doc["tags"],
                        "metadata": doc.get("metadata", {}),
                        "content": doc["content"],
                    }
                )

                # Repomix: extract file stats
                updates["repomix"].append(
                    {
                        "doc": doc,
                        "file": file,
                    }
                )

            # Phase 2: Apply updates to all 3 DBs
            # Update ChromaDB (기존 로직 재사용)
            for file in changes["deleted"]:
                self.vector_store.delete_document(str(file))
                del self.metadata["indexed_files"][str(file)]
                print(f"  ❌ 삭제: {file.name}")

            # 수정된 파일과 새 파일 처리
            for i, file in enumerate(changes["modified"] + changes["new"]):
                chroma_data = updates["chroma"][i]
                doc = chroma_data["doc"]

                if file in changes["modified"]:
                    self.vector_store.update_document(doc)
                    print(f"  ♻️ 업데이트: {file.name}")
                else:
                    self.vector_store.add_document(doc)
                    print(f"  ➕ 추가: {file.name}")

                self.metadata["indexed_files"][str(file)] = self.get_file_hash(file)

            # Update NetworkMetadataStore
            print("  🔗 네트워크 메타데이터 업데이트 중...")
            for network_doc in updates["network"]:
                self.network_store.update_metadata(network_doc)

            for file in changes["deleted"]:
                self.network_store.delete_metadata(str(file))

            # Update RepomixIndexStore
            print("  📦 Repomix 인덱스 업데이트 중...")
            for repomix_data in updates["repomix"]:
                doc = repomix_data["doc"]
                file = repomix_data["file"]
                self.repomix_store.update_index(doc, file)

            for file in changes["deleted"]:
                self.repomix_store.delete_index(str(file))

            # Save all metadata
            self.metadata["last_update"] = datetime.now().isoformat()
            self.save_metadata()
            self.network_store.save_metadata()
            self.repomix_store.save_index()

            print("✅ 통합 인덱스 업데이트 완료!")
            print(
                f"  - ChromaDB: {len(changes['new']) + len(changes['modified'])} 문서 업데이트"
            )
            print(f"  - Network: {len(updates['network'])} 메타데이터 업데이트")
            print(f"  - Repomix: {len(updates['repomix'])} 인덱스 업데이트")

            # 오래된 백업 정리
            self._cleanup_old_backups()

        except Exception as e:
            print(f"❌ 업데이트 실패: {e}")
            print("🔄 롤백 시도 중...")
            self._rollback(backup_dir)
            raise
