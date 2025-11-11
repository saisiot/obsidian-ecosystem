#!/usr/bin/env python3
"""
Demo: 모의 데이터로 동기화 시연

실제 macOS Contacts 대신 샘플 데이터를 사용하여
전체 동기화 워크플로우를 시연합니다.
"""
import sys
import logging
from pathlib import Path
from datetime import date
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
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def main():
    """데모 동기화 함수"""
    logger.info("=" * 60)
    logger.info("📱 Contacts → Obsidian 동기화 데모 (모의 데이터)")
    logger.info("=" * 60)

    # 모의 연락처 데이터
    demo_contacts = [
        {
            'contact_id': 'DEMO-001-HONG',
            'name': '홍길동',
            'phone': '010-1234-5678',
            'email': 'hong@example.com',
            'notes': '''251110 점심 미팅. 새 프로젝트 논의.
251105 전화 통화. 일정 조율.
251101 이메일 답장.
241220 연말 인사.'''
        },
        {
            'contact_id': 'DEMO-002-KIM',
            'name': '김철수',
            'phone': '010-9876-5432',
            'email': 'kim@example.com',
            'notes': '''251108 커피 미팅. AI 도입 방안 논의.
251020 컨퍼런스에서 만남.'''
        },
        {
            'contact_id': 'DEMO-003-PARK',
            'name': '박영희',
            'phone': '010-5555-6666',
            'email': 'park@example.com',
            'notes': '''251109 저녁 식사.
250815 여름 휴가 후 연락.'''
        },
        {
            'contact_id': 'DEMO-004-JOHN',
            'name': 'John Smith',
            'phone': '+1-234-567-8900',
            'email': 'john@example.com',
            'notes': '''251107 Video call about project.
251015 Email exchange.'''
        },
        {
            'contact_id': 'DEMO-005-EMPTY',
            'name': '이순신',
            'phone': '010-7777-8888',
            'email': 'lee@example.com',
            'notes': ''  # 메모 없음
        }
    ]

    logger.info(f"\n📊 모의 연락처: {len(demo_contacts)}개")
    for contact in demo_contacts:
        logger.info(f"  - {contact['name']}")

    # 1. MemoParser 초기화
    parser = MemoParser()

    # 2. DB 초기화 및 데이터 저장
    logger.info("\n[1/4] 데이터베이스에 저장 중...")
    with DatabaseManager(DB_PATH) as db:
        db.create_tables()

        for contact in demo_contacts:
            # 연락처 저장
            db.insert_contact(contact)

            # 메모 파싱
            notes = contact.get('notes', '')
            if notes:
                interactions = parser.parse(notes)
                logger.info(f"  {contact['name']}: {len(interactions)}개 interaction")

                # Interaction 저장
                for interaction in interactions:
                    db.insert_interaction({
                        'contact_id': contact['contact_id'],
                        'date': interaction['date'],
                        'content': interaction['content']
                    })
            else:
                logger.info(f"  {contact['name']}: 메모 없음")

    logger.info("✅ 데이터베이스 저장 완료")

    # 3. 통계 계산
    logger.info("\n[2/4] 통계 계산 중...")
    with StatsCalculator(DB_PATH) as calculator:
        all_stats = calculator.calculate_all_stats()

    logger.info(f"✅ {len(all_stats)}개 연락처 통계 계산 완료")

    # 통계 미리보기
    logger.info("\n📈 통계 미리보기:")
    for contact in demo_contacts[:3]:  # 처음 3명만
        contact_id = contact['contact_id']
        stats = all_stats[contact_id]
        logger.info(f"  {contact['name']}:")
        logger.info(f"    - 총 연락 횟수: {stats['contact_count']}회")
        logger.info(f"    - 최근 연락: {stats['last_contact']}")
        logger.info(f"    - 최근 6개월: {stats['last_6month_contacts']}회")

    # 4. Obsidian 노트 생성/업데이트
    logger.info("\n[3/4] Obsidian 노트 생성 중...")
    writer = ObsidianWriter(PEOPLE_FOLDER)

    created_count = 0

    for contact in demo_contacts:
        contact_id = contact['contact_id']
        stats = all_stats.get(contact_id, {
            'contact_count': 0,
            'last_contact': None,
            'last_6month_contacts': 0
        })

        # Interaction 조회
        with DatabaseManager(DB_PATH) as db:
            interactions = db.get_interactions(contact_id)

        # 노트 생성
        writer.write_note(contact, interactions, stats)
        created_count += 1

    logger.info(f"✅ {created_count}개 노트 생성 완료")

    # 5. 생성된 노트 미리보기
    logger.info("\n[4/4] 생성된 노트 확인...")
    logger.info(f"\n📝 노트 파일 목록 ({PEOPLE_FOLDER}):")
    for note_path in sorted(PEOPLE_FOLDER.glob("*.md")):
        logger.info(f"  - {note_path.name}")

    # 홍길동 노트 미리보기
    hong_note = PEOPLE_FOLDER / "홍길동.md"
    if hong_note.exists():
        logger.info("\n📄 홍길동.md 내용 미리보기:")
        logger.info("-" * 60)
        content = hong_note.read_text(encoding='utf-8')
        # 처음 30줄만 출력
        lines = content.split('\n')[:30]
        for line in lines:
            logger.info(line)
        if len(content.split('\n')) > 30:
            logger.info("...")
        logger.info("-" * 60)

    # 6. 완료
    logger.info("\n" + "=" * 60)
    logger.info("✅ 동기화 데모 완료!")
    logger.info("=" * 60)
    logger.info(f"📊 최종 통계:")
    logger.info(f"  - 총 연락처: {len(demo_contacts)}개")
    logger.info(f"  - 노트 생성: {created_count}개")
    logger.info(f"  - 저장 위치: {PEOPLE_FOLDER}")
    logger.info(f"  - 데이터베이스: {DB_PATH}")
    logger.info("=" * 60)

    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        logger.info("\n\n데모가 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"\n❌ 오류 발생: {e}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)
