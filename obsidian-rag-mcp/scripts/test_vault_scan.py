#!/usr/bin/env python3
"""
Vault 전체 스캔 테스트

변경된 설정으로 얼마나 많은 .md 파일이 발견되는지 확인합니다.
"""

import sys
from pathlib import Path
from collections import defaultdict

# 프로젝트 루트를 sys.path에 추가
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "src"))

from config import VAULT_PATH, EXCLUDE_PATTERNS
from indexer import IncrementalIndexer


def test_vault_scan():
    """Vault 전체 스캔 테스트"""

    print("╔══════════════════════════════════════════════════════════╗")
    print("║                                                          ║")
    print("║         Vault 전체 스캔 테스트                            ║")
    print("║                                                          ║")
    print("╚══════════════════════════════════════════════════════════╝")
    print()

    print(f"📁 Vault 경로: {VAULT_PATH}")
    print(f"🚫 제외 패턴: {', '.join(EXCLUDE_PATTERNS)}")
    print()

    # Step 1: Vault 전체의 .md 파일 수 확인
    print("📊 Step 1: Vault 전체 .md 파일 스캔")
    print("━" * 60)

    all_md_files = list(VAULT_PATH.rglob("*.md"))
    print(f"  📄 전체 .md 파일: {len(all_md_files):,}개")
    print()

    # Step 2: IncrementalIndexer로 필터링된 파일 확인
    print("🔍 Step 2: 제외 패턴 적용 후 파일 수")
    print("━" * 60)

    # Mock vector_store (None으로 전달)
    class MockVectorStore:
        pass

    indexer = IncrementalIndexer(MockVectorStore())
    filtered_files = indexer.get_md_files()

    print(f"  ✅ 인덱싱 대상 파일: {len(filtered_files):,}개")
    print(f"  🚫 제외된 파일: {len(all_md_files) - len(filtered_files):,}개")
    print()

    # Step 3: 폴더별 분포 확인
    print("📂 Step 3: 폴더별 파일 분포")
    print("━" * 60)

    folder_distribution = defaultdict(int)
    for file in filtered_files:
        try:
            relative_path = file.relative_to(VAULT_PATH)
            # 최상위 폴더 추출
            if len(relative_path.parts) > 1:
                top_folder = relative_path.parts[0]
            else:
                top_folder = "(root)"
            folder_distribution[top_folder] += 1
        except ValueError:
            pass

    # 파일 수로 정렬
    sorted_folders = sorted(folder_distribution.items(), key=lambda x: x[1], reverse=True)

    total_shown = 0
    for folder, count in sorted_folders:
        print(f"  📁 {folder:30s}: {count:4d}개")
        total_shown += count

    print(f"  {'─' * 35}{'─' * 10}")
    print(f"  {'총합':30s}: {total_shown:4d}개")
    print()

    # Step 4: 새로 추가된 폴더 확인
    print("🆕 Step 4: 이전에 인덱싱되지 않았던 폴더")
    print("━" * 60)

    previous_folders = {"00 Notes", "01 Reference", "02 Journals", "04 Outputs"}
    new_folders = set(folder_distribution.keys()) - previous_folders - {"(root)"}

    if new_folders:
        for folder in sorted(new_folders):
            count = folder_distribution[folder]
            print(f"  ✨ {folder:30s}: {count:4d}개")
    else:
        print("  (없음)")
    print()

    # 최종 결과
    print("━" * 60)
    print("🎉 Vault 스캔 완료!")
    print("━" * 60)
    print()

    return True


if __name__ == "__main__":
    success = test_vault_scan()
    sys.exit(0 if success else 1)
