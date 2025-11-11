#!/usr/bin/env python3
"""
Contacts → Obsidian 동기화 메인 스크립트

사용법:
    python sync.py

동작 순서:
1. macOS Contacts에서 모든 연락처 읽기
2. 각 연락처의 메모 필드에서 interaction 파싱 (YYMMDD 형식)
3. SQLite 데이터베이스에 저장
4. 통계 계산 (contact_count, last_contact, last_6month_contacts)
5. Obsidian 노트 생성/업데이트
"""
import sys
import logging
from pathlib import Path
from src.config import PEOPLE_FOLDER, DB_PATH
from src.contacts_reader import ContactsReader
from src.memo_parser import MemoParser
from src.db_manager import DatabaseManager
from src.stats_calculator import StatsCalculator
from src.obsidian_writer import ObsidianWriter

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(PEOPLE_FOLDER / 'sync.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def main():
    """메인 동기화 함수"""
    logger.info("=" * 60)
    logger.info("Contacts → Obsidian 동기화 시작")
    logger.info("=" * 60)

    # 0. Vault 디렉토리 확인
    if not PEOPLE_FOLDER.exists():
        logger.error(f"Vault 디렉토리가 존재하지 않습니다: {PEOPLE_FOLDER}")
        logger.error("src/config.py에서 PEOPLE_FOLDER 경로를 확인하세요.")
        return 1

    logger.info(f"Vault 경로: {PEOPLE_FOLDER}")
    logger.info(f"DB 경로: {DB_PATH}")

    # 1. Contacts 읽기
    logger.info("\n[1/5] macOS Contacts 읽기...")
    reader = ContactsReader()
    contacts = reader.read_all_contacts()
    logger.info(f"✅ {len(contacts)}개의 연락처 읽기 완료")

    if len(contacts) == 0:
        logger.warning("⚠️  연락처가 없습니다. 동기화를 종료합니다.")
        logger.warning("확인 사항:")
        logger.warning("1. macOS Contacts 앱에 연락처가 있는지 확인")
        logger.warning("2. Python의 Contacts 접근 권한 확인 (시스템 설정 > 개인 정보 보호)")
        return 0

    # 2. MemoParser 초기화
    parser = MemoParser()

    # 3. DB 초기화 및 데이터 저장
    logger.info("\n[2/5] SQLite 데이터베이스에 저장 중...")
    with DatabaseManager(DB_PATH) as db:
        db.create_tables()

        for contact in contacts:
            # 연락처 저장
            db.insert_contact(contact)

            # 메모 파싱
            notes = contact.get('notes', '')
            if notes:
                interactions = parser.parse(notes)

                # Interaction 저장
                for interaction in interactions:
                    db.insert_interaction({
                        'contact_id': contact['contact_id'],
                        'date': interaction['date'],
                        'content': interaction['content']
                    })

    logger.info("✅ 데이터베이스 저장 완료")

    # 4. 통계 계산
    logger.info("\n[3/5] 통계 계산 중...")
    with StatsCalculator(DB_PATH) as calculator:
        all_stats = calculator.calculate_all_stats()

    logger.info(f"✅ {len(all_stats)}개 연락처 통계 계산 완료")

    # 5. Obsidian 노트 생성/업데이트
    logger.info("\n[4/5] Obsidian 노트 생성/업데이트 중...")
    writer = ObsidianWriter(PEOPLE_FOLDER)

    created_count = 0
    updated_count = 0

    for contact in contacts:
        contact_id = contact['contact_id']
        stats = all_stats.get(contact_id, {
            'contact_count': 0,
            'last_contact': None,
            'last_6month_contacts': 0
        })

        # Interaction 조회
        with DatabaseManager(DB_PATH) as db:
            interactions = db.get_interactions(contact_id)

        # 노트 생성/업데이트
        existing_note = writer.find_note_by_contact_id(contact_id)
        if existing_note:
            updated_count += 1
        else:
            created_count += 1

        writer.write_note(contact, interactions, stats)

    logger.info(f"✅ 노트 생성 {created_count}개, 업데이트 {updated_count}개")

    # 6. 완료 메시지
    logger.info("\n[5/5] 동기화 완료!")
    logger.info("=" * 60)
    logger.info(f"📊 통계")
    logger.info(f"  - 총 연락처: {len(contacts)}개")
    logger.info(f"  - 새로 생성: {created_count}개")
    logger.info(f"  - 업데이트: {updated_count}개")
    logger.info("=" * 60)

    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        logger.info("\n\n동기화가 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ 오류 발생: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)
