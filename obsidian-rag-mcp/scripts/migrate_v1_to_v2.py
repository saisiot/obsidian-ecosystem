#!/usr/bin/env python3
"""
v1.0 → v2.0 Migration Script

This script migrates the Obsidian RAG MCP from v1.0 to v2.0 by:
1. Backing up existing metadata
2. Upgrading metadata schema
3. Initializing new stores (NetworkMetadata, RepomixIndex)
4. Re-indexing vault to populate new stores (ChromaDB is preserved)
"""

import argparse
import json
import shutil
import sys
import traceback
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from config import METADATA_FILE, PROJECT_ROOT, VAULT_PATH
from indexer import UnifiedIndexer
from network_store import NetworkMetadataStore
from repomix_store import RepomixIndexStore
from vector_store import VectorStore


class Colors:
    """ANSI color codes for terminal output"""

    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def colored(text: str, color: str) -> str:
    """Apply color to text"""
    return f"{color}{text}{Colors.ENDC}"


def print_header(text: str):
    """Print a styled header"""
    print()
    print(colored("╔" + "═" * 58 + "╗", Colors.BOLD))
    print(colored("║" + " " * 58 + "║", Colors.BOLD))
    print(colored("║" + text.center(58) + "║", Colors.BOLD))
    print(colored("║" + " " * 58 + "║", Colors.BOLD))
    print(colored("╚" + "═" * 58 + "╝", Colors.BOLD))


def print_step(step_num: int, title: str):
    """Print a step header"""
    print()
    print(colored(f"\n{title}", Colors.BOLD))
    print(colored("━" * 60, Colors.OKBLUE))


def backup_metadata(dry_run: bool = False, verbose: bool = False) -> Path:
    """v1.0 메타데이터 백업

    Args:
        dry_run: 실제 작업 수행하지 않고 시뮬레이션만
        verbose: 상세 로그 출력

    Returns:
        백업 파일 경로
    """
    print_step(1, "📦 Step 1: v1.0 메타데이터 백업")

    backup_file = METADATA_FILE.with_suffix(".json.v1.backup")

    if verbose:
        print(f"  원본: {METADATA_FILE}")
        print(f"  백업: {backup_file}")

    if METADATA_FILE.exists():
        if not dry_run:
            shutil.copy(METADATA_FILE, backup_file)
        print(colored(f"✅ 백업 완료: {backup_file}", Colors.OKGREEN))
    else:
        print(colored("⚠️ 기존 메타데이터 파일이 없습니다.", Colors.WARNING))

    return backup_file


def upgrade_metadata_schema(
    dry_run: bool = False, verbose: bool = False
) -> dict:
    """메타데이터 스키마 v2.0으로 업그레이드

    Args:
        dry_run: 실제 작업 수행하지 않고 시뮬레이션만
        verbose: 상세 로그 출력

    Returns:
        업그레이드된 메타데이터
    """
    print_step(2, "🔄 Step 2: 메타데이터 스키마 업그레이드")

    if not METADATA_FILE.exists():
        print(
            colored("⚠️ 메타데이터 파일이 없습니다. 새로 생성됩니다.", Colors.WARNING)
        )
        metadata = {"last_update": 0, "indexed_files": {}}
    else:
        with open(METADATA_FILE, "r") as f:
            metadata = json.load(f)

        if verbose:
            print(f"  기존 버전: {metadata.get('version', 'v1.0 (없음)')}")
            print(f"  마지막 업데이트: {metadata.get('last_update', 0)}")
            print(f"  인덱스된 파일 수: {len(metadata.get('indexed_files', {}))}")

    # v2.0 스키마 추가
    metadata["version"] = "2.0.0"
    metadata["databases"] = {
        "chromadb": {"last_update": metadata.get("last_update", 0)},
        "network": {"last_update": None},
        "repomix": {"last_update": None},
    }
    metadata["auto_update"] = {
        "enabled": True,
        "interval": 300,
        "last_run": None,
    }

    if verbose:
        print("\n  업그레이드된 스키마:")
        print(f"    - version: {metadata['version']}")
        print(f"    - databases: {list(metadata['databases'].keys())}")
        print(f"    - auto_update.enabled: {metadata['auto_update']['enabled']}")

    # 저장
    if not dry_run:
        with open(METADATA_FILE, "w") as f:
            json.dump(metadata, f, indent=2)

    print(colored(f"✅ 스키마 업그레이드 완료 (v2.0.0)", Colors.OKGREEN))
    print(f"   - 데이터베이스: ChromaDB, Network, Repomix")
    print(f"   - Auto-update: Enabled (300초 간격)")

    return metadata


def initialize_new_stores(
    dry_run: bool = False, verbose: bool = False
) -> tuple:
    """새로운 Store 초기화

    Args:
        dry_run: 실제 작업 수행하지 않고 시뮬레이션만
        verbose: 상세 로그 출력

    Returns:
        (vector_store, network_store, repomix_store) 튜플
    """
    print_step(3, "🆕 Step 3: 새로운 데이터베이스 초기화")

    if dry_run:
        print(colored("  [DRY RUN] Store 초기화 시뮬레이션", Colors.OKCYAN))
        return None, None, None

    vector_store = VectorStore()
    network_store = NetworkMetadataStore()
    repomix_store = RepomixIndexStore()

    if verbose:
        print(f"  - VectorStore: {vector_store.collection.name}")
        print(f"  - NetworkMetadataStore: {network_store.metadata_file}")
        print(f"  - RepomixIndexStore: {repomix_store.index_file}")

    print(colored(f"✅ VectorStore 초기화 완료", Colors.OKGREEN))
    print(colored(f"✅ NetworkMetadataStore 초기화 완료", Colors.OKGREEN))
    print(colored(f"✅ RepomixIndexStore 초기화 완료", Colors.OKGREEN))

    return vector_store, network_store, repomix_store


def reindex_vault(
    vector_store,
    network_store,
    repomix_store,
    dry_run: bool = False,
    verbose: bool = False,
) -> bool:
    """Vault 재인덱싱 (Network와 Repomix만)

    Args:
        vector_store: VectorStore 인스턴스
        network_store: NetworkMetadataStore 인스턴스
        repomix_store: RepomixIndexStore 인스턴스
        dry_run: 실제 작업 수행하지 않고 시뮬레이션만
        verbose: 상세 로그 출력

    Returns:
        성공 여부
    """
    print_step(4, "🔍 Step 4: Vault 재인덱싱")
    print("ℹ️  ChromaDB는 보존되며, Network와 Repomix만 생성됩니다.")
    print()

    # Vault 존재 확인
    if not VAULT_PATH.exists():
        print(
            colored(f"❌ Vault 경로가 존재하지 않습니다: {VAULT_PATH}", Colors.FAIL)
        )
        print(colored("⚠️  config.py의 VAULT_PATH를 확인하세요.", Colors.WARNING))
        return False

    # 마크다운 파일 수 확인
    md_files = list(VAULT_PATH.rglob("*.md"))
    print(f"📂 발견된 마크다운 파일: {len(md_files)}개")

    if verbose and len(md_files) > 0:
        print("\n  파일 목록 (최대 10개):")
        for file in md_files[:10]:
            print(f"    - {file.name}")
        if len(md_files) > 10:
            print(f"    ... 그 외 {len(md_files) - 10}개")

    if len(md_files) == 0:
        print(colored("⚠️ 마크다운 파일이 없습니다. 재인덱싱을 건너뜁니다.", Colors.WARNING))
        return True

    if dry_run:
        print(colored("  [DRY RUN] 재인덱싱 시뮬레이션", Colors.OKCYAN))
        print(f"  예상 작업: {len(md_files)}개 파일 인덱싱")
        return True

    # UnifiedIndexer 생성
    indexer = UnifiedIndexer(vector_store, network_store, repomix_store)

    # 재인덱싱 실행
    print("\n⏳ 재인덱싱 시작... (수 분 소요될 수 있습니다)")
    start_time = datetime.now()

    try:
        indexer.update_index()

        elapsed = (datetime.now() - start_time).total_seconds()
        print(
            colored(
                f"\n✅ 재인덱싱 완료! (소요 시간: {elapsed:.1f}초)", Colors.OKGREEN
            )
        )

        # 통계 출력
        print("\n📊 인덱싱 통계:")
        chroma_count = len(vector_store.collection.get()["ids"])
        network_count = len(network_store.metadata["files"])
        repomix_count = len(repomix_store.index["files"])

        print(f"   - ChromaDB: {chroma_count} 청크")
        print(f"   - Network: {network_count} 파일")
        print(f"   - Repomix: {repomix_count} 파일")

        if verbose:
            print("\n  Network 통계:")
            stats = network_store.get_network_stats()
            print(f"    - 총 파일: {stats['total_files']}")
            print(f"    - 총 백링크: {stats['total_backlinks']}")
            print(f"    - 고립된 노트: {stats['orphaned_notes']}")

            print("\n  Repomix 통계:")
            rep_stats = repomix_store.index["stats"]
            print(f"    - 총 단어: {rep_stats['total_words']:,}")
            print(f"    - 예상 토큰: {rep_stats['total_tokens_estimated']:,}")

        return True

    except Exception as e:
        print(colored(f"\n❌ 재인덱싱 실패: {e}", Colors.FAIL))
        if verbose:
            traceback.print_exc()
        return False


def verify_migration(verbose: bool = False) -> bool:
    """마이그레이션 검증

    Args:
        verbose: 상세 로그 출력

    Returns:
        검증 성공 여부
    """
    print_step(5, "✅ Step 5: 마이그레이션 검증")

    checks = []

    # 1. 메타데이터 파일 존재 확인
    checks.append(("index_metadata.json", METADATA_FILE.exists()))

    # 2. Network 메타데이터 존재 확인
    network_file = PROJECT_ROOT / "data" / "network_metadata.json"
    checks.append(("network_metadata.json", network_file.exists()))

    # 3. Repomix 인덱스 존재 확인
    repomix_file = PROJECT_ROOT / "data" / "repomix_index.json"
    checks.append(("repomix_index.json", repomix_file.exists()))

    # 4. 백업 존재 확인
    backup_file = METADATA_FILE.with_suffix(".json.v1.backup")
    checks.append(("v1.0 백업", backup_file.exists()))

    # 결과 출력
    all_passed = True
    for name, passed in checks:
        if passed:
            print(colored(f"✅ {name}", Colors.OKGREEN))
        else:
            print(colored(f"❌ {name}", Colors.FAIL))
            all_passed = False

    if verbose and all_passed:
        print("\n  상세 정보:")
        # 메타데이터 버전 확인
        if METADATA_FILE.exists():
            with open(METADATA_FILE, "r") as f:
                metadata = json.load(f)
            print(f"    - 메타데이터 버전: {metadata.get('version', 'N/A')}")
            print(
                f"    - 데이터베이스: {list(metadata.get('databases', {}).keys())}"
            )

    return all_passed


def rollback_migration(verbose: bool = False) -> bool:
    """마이그레이션 롤백

    Args:
        verbose: 상세 로그 출력

    Returns:
        롤백 성공 여부
    """
    print_header("🔙 마이그레이션 롤백")
    print()

    backup_file = METADATA_FILE.with_suffix(".json.v1.backup")

    if not backup_file.exists():
        print(
            colored(f"❌ 백업 파일이 없습니다: {backup_file}", Colors.FAIL)
        )
        return False

    try:
        print(f"⏳ 롤백 중...")

        # 백업 파일 복원
        shutil.copy(backup_file, METADATA_FILE)

        # v2.0 파일 삭제
        network_file = PROJECT_ROOT / "data" / "network_metadata.json"
        repomix_file = PROJECT_ROOT / "data" / "repomix_index.json"

        if network_file.exists():
            network_file.unlink()
            if verbose:
                print(f"  - 삭제: {network_file}")

        if repomix_file.exists():
            repomix_file.unlink()
            if verbose:
                print(f"  - 삭제: {repomix_file}")

        print(colored("\n✅ 롤백 완료!", Colors.OKGREEN))
        print(f"   v1.0 메타데이터로 복원되었습니다.")
        return True

    except Exception as e:
        print(colored(f"\n❌ 롤백 실패: {e}", Colors.FAIL))
        if verbose:
            traceback.print_exc()
        return False


def main():
    """메인 마이그레이션 프로세스"""
    parser = argparse.ArgumentParser(
        description="Obsidian RAG MCP v1.0 → v2.0 마이그레이션 스크립트"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="실제 작업을 수행하지 않고 시뮬레이션만 실행",
    )
    parser.add_argument(
        "--rollback",
        action="store_true",
        help="마이그레이션 롤백 (v1.0으로 복원)",
    )
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="상세 로그 출력"
    )

    args = parser.parse_args()

    # 롤백 모드
    if args.rollback:
        success = rollback_migration(verbose=args.verbose)
        return 0 if success else 1

    # 일반 마이그레이션 모드
    print_header("Obsidian RAG MCP v1.0 → v2.0 Migration")

    if args.dry_run:
        print(
            colored(
                "\n⚠️  DRY RUN 모드: 실제 작업은 수행되지 않습니다.", Colors.WARNING
            )
        )

    try:
        # Step 1: 백업
        backup_file = backup_metadata(dry_run=args.dry_run, verbose=args.verbose)

        # Step 2: 스키마 업그레이드
        metadata = upgrade_metadata_schema(
            dry_run=args.dry_run, verbose=args.verbose
        )

        # Step 3: 새 Store 초기화
        vector_store, network_store, repomix_store = initialize_new_stores(
            dry_run=args.dry_run, verbose=args.verbose
        )

        # Step 4: 재인덱싱
        if not args.dry_run:
            success = reindex_vault(
                vector_store,
                network_store,
                repomix_store,
                dry_run=args.dry_run,
                verbose=args.verbose,
            )

            if not success:
                print(colored("\n❌ 마이그레이션 실패!", Colors.FAIL))
                print(colored(f"💡 롤백 방법: python {__file__} --rollback", Colors.OKCYAN))
                return 1

        # Step 5: 검증
        if not args.dry_run:
            if not verify_migration(verbose=args.verbose):
                print(
                    colored(
                        "\n⚠️ 검증 실패. 일부 파일이 누락되었습니다.", Colors.WARNING
                    )
                )
                return 1

        # 성공!
        print("\n" + colored("━" * 60, Colors.OKBLUE))
        print(colored("🎉 마이그레이션 완료!", Colors.OKGREEN + Colors.BOLD))
        print(colored("━" * 60, Colors.OKBLUE))

        if not args.dry_run:
            print("\n✅ v2.0 기능:")
            print("   - 3개 데이터베이스 통합 (ChromaDB, Network, Repomix)")
            print("   - 트랜잭션 & 롤백 시스템")
            print("   - 백링크 네트워크 추적")
            print("   - 파일 통계 및 토큰 추정")
            print("\n📝 다음 단계:")
            print("   - python src/mcp_server.py 로 서버 시작")
            print("   - Auto-update 서비스 활성화 (Phase 2)")
            print("   - Repomix 패킹 도구 사용 (Phase 3)")
        else:
            print(
                "\n💡 실제 마이그레이션을 수행하려면 --dry-run 플래그 없이 실행하세요."
            )

        print()

        return 0

    except Exception as e:
        print(colored(f"\n❌ 예상치 못한 오류: {e}", Colors.FAIL))
        if args.verbose:
            traceback.print_exc()
        print(colored(f"\n💡 롤백 방법: python {__file__} --rollback", Colors.OKCYAN))
        return 1


if __name__ == "__main__":
    sys.exit(main())
