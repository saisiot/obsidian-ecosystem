#!/usr/bin/env python3
"""
Contacts → Obsidian 동기화 (AppleScript 버전)
권한 문제를 우회하여 실제 연락처로 동기화

사용법:
    python sync_applescript.py
"""
import sys
import logging
import subprocess
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


def read_contacts_via_applescript(limit=None):
    """
    AppleScript를 통해 연락처 읽기

    Args:
        limit: 읽을 연락처 개수 제한 (None이면 전체)

    Returns:
        연락처 리스트
    """
    logger.info("AppleScript를 통해 연락처 읽기 중...")

    # AppleScript 생성
    limit_clause = f"people 1 thru {limit}" if limit else "people"

    applescript = f'''
    tell application "Contacts"
        set peopleList to {limit_clause}
        set output to ""

        repeat with aPerson in peopleList
            try
                set personId to id of aPerson
                set personName to name of aPerson

                -- ID 추가
                set output to output & "CONTACT_START" & "\\n"
                set output to output & "ID:" & personId & "\\n"
                set output to output & "NAME:" & personName & "\\n"

                -- 전화번호
                try
                    set phoneNum to value of phone 1 of aPerson
                    set output to output & "PHONE:" & phoneNum & "\\n"
                on error
                    set output to output & "PHONE:\\n"
                end try

                -- 이메일
                try
                    set emailAddr to value of email 1 of aPerson
                    set output to output & "EMAIL:" & emailAddr & "\\n"
                on error
                    set output to output & "EMAIL:\\n"
                end try

                -- 메모
                try
                    set personNote to note of aPerson
                    if personNote is not missing value then
                        set output to output & "NOTE:" & personNote & "\\n"
                    else
                        set output to output & "NOTE:\\n"
                    end if
                on error
                    set output to output & "NOTE:\\n"
                end try

                set output to output & "CONTACT_END" & "\\n"
            on error errMsg
                -- 에러 무시하고 계속
            end try
        end repeat

        return output
    end tell
    '''

    try:
        result = subprocess.run(
            ['osascript', '-e', applescript],
            capture_output=True,
            text=True,
            timeout=300  # 최대 5분 (416개 연락처 처리 위해)
        )

        if result.returncode != 0:
            logger.error(f"AppleScript 실행 실패: {result.stderr}")
            return []

        # 파싱
        contacts = []
        lines = result.stdout.strip().split('\n')
        current_contact = None
        in_note = False
        note_lines = []

        for line in lines:
            if line.strip() == "CONTACT_START":
                current_contact = {}
                in_note = False
                note_lines = []
            elif line.strip() == "CONTACT_END":
                if current_contact:
                    # NOTE 마무리
                    if note_lines:
                        current_contact['notes'] = '\n'.join(note_lines)
                    contacts.append(current_contact)
                current_contact = None
                in_note = False
                note_lines = []
            elif current_contact is not None:
                if in_note:
                    # NOTE 섹션 내부 - 모든 줄을 노트에 추가
                    note_lines.append(line)
                elif ':' in line:
                    key, value = line.split(':', 1)
                    value = value.strip()

                    if key == "ID":
                        current_contact['contact_id'] = value
                    elif key == "NAME":
                        current_contact['name'] = value
                    elif key == "PHONE":
                        current_contact['phone'] = value if value else None
                    elif key == "EMAIL":
                        current_contact['email'] = value if value else None
                    elif key == "NOTE":
                        in_note = True
                        if value:  # NOTE: 뒤에 내용이 있으면
                            note_lines.append(value)

        logger.info(f"✅ {len(contacts)}개의 연락처 읽기 완료")
        return contacts

    except subprocess.TimeoutExpired:
        logger.error("AppleScript 실행 시간 초과")
        return []
    except Exception as e:
        logger.error(f"연락처 읽기 실패: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return []


def main():
    """메인 동기화 함수"""
    logger.info("=" * 60)
    logger.info("📱 Contacts → Obsidian 동기화 (AppleScript 버전)")
    logger.info("=" * 60)

    # 0. Vault 디렉토리 확인
    if not PEOPLE_FOLDER.exists():
        logger.error(f"Vault 디렉토리가 존재하지 않습니다: {PEOPLE_FOLDER}")
        return 1

    logger.info(f"Vault 경로: {PEOPLE_FOLDER}")
    logger.info(f"DB 경로: {DB_PATH}")

    # 1. Contacts 읽기 (AppleScript)
    logger.info("\n[1/5] AppleScript로 Contacts 읽기...")

    # 연락처 읽기 (50개로 테스트)
    contacts = read_contacts_via_applescript(limit=50)

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
