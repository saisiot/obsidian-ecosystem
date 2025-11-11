#!/usr/bin/env python3
"""
Contacts → Obsidian 동기화 (JXA 버전)
JavaScript for Automation을 사용하여 빠르게 연락처 읽기

사용법:
    python sync_jxa.py
"""
import sys
import logging
import subprocess
import json
from pathlib import Path
from src.config import PEOPLE_FOLDER, DB_PATH
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


def read_contacts_via_jxa(limit=None):
    """
    JXA를 통해 연락처 읽기

    Args:
        limit: 읽을 연락처 개수 제한 (None이면 전체)

    Returns:
        연락처 리스트
    """
    logger.info("JXA를 통해 연락처 읽기 중...")

    # JXA 스크립트
    limit_expr = f"Math.min({limit}, people.length)" if limit else "people.length"

    jxa_script = f'''
    const app = Application('Contacts');
    const people = app.people();

    const contacts = [];
    const limit = {limit_expr};

    for (let i = 0; i < limit; i++) {{
        const person = people[i];
        try {{
            const contact = {{
                contact_id: person.id(),
                name: person.name(),
                phone: person.phones.length > 0 ? person.phones[0].value() : null,
                email: person.emails.length > 0 ? person.emails[0].value() : null,
                notes: person.note() || null
            }};
            contacts.push(contact);
        }} catch (e) {{
            // Skip errors
        }}
    }}

    JSON.stringify(contacts);
    '''

    try:
        result = subprocess.run(
            ['osascript', '-l', 'JavaScript', '-e', jxa_script],
            capture_output=True,
            text=True,
            timeout=300  # 5분
        )

        if result.returncode != 0:
            logger.error(f"JXA 실행 실패: {result.stderr}")
            return []

        # JSON 파싱
        contacts = json.loads(result.stdout.strip())

        logger.info(f"✅ {len(contacts)}개의 연락처 읽기 완료")
        return contacts

    except subprocess.TimeoutExpired:
        logger.error("JXA 실행 시간 초과")
        return []
    except json.JSONDecodeError as e:
        logger.error(f"JSON 파싱 실패: {e}")
        logger.debug(f"출력: {result.stdout[:500]}")
        return []
    except Exception as e:
        logger.error(f"연락처 읽기 실패: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return []


def main():
    """메인 동기화 함수"""
    logger.info("=" * 60)
    logger.info("📱 Contacts → Obsidian 동기화 (JXA 버전)")
    logger.info("=" * 60)

    # 0. Vault 디렉토리 확인
    if not PEOPLE_FOLDER.exists():
        logger.error(f"Vault 디렉토리가 존재하지 않습니다: {PEOPLE_FOLDER}")
        return 1

    logger.info(f"Vault 경로: {PEOPLE_FOLDER}")
    logger.info(f"DB 경로: {DB_PATH}")

    # 1. Contacts 읽기 (JXA)
    logger.info("\n[1/5] JXA로 Contacts 읽기...")

    # 전체 연락처 읽기
    contacts = read_contacts_via_jxa(limit=None)

    if len(contacts) == 0:
        logger.warning("⚠️  연락처를 읽을 수 없습니다.")
        return 1

    logger.info(f"\n처음 3개 연락처 미리보기:")
    for contact in contacts[:3]:
        logger.info(f"  - {contact['name']}")
        if contact.get('notes'):
            preview = contact['notes'][:50].replace('\n', ' ')
            logger.info(f"    메모: {preview}...")

    # 2. MemoParser 초기화
    parser = MemoParser()

    # 3. DB 초기화 및 데이터 저장
    logger.info("\n[2/5] SQLite 데이터베이스에 저장 중...")
    interaction_count = 0

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
                    interaction_count += 1

    logger.info(f"✅ {len(contacts)}개 연락처, {interaction_count}개 interaction 저장 완료")

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
    logger.info(f"  - Interaction: {interaction_count}개")
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
