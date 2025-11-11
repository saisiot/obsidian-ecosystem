#!/usr/bin/env python3
"""
실제 Contacts 데이터 읽기 테스트 스크립트
macOS Contacts 앱에서 실제 연락처를 읽어옵니다.
"""
import logging
from src.contacts_reader import ContactsReader

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    print("=" * 60)
    print("Contacts 데이터 읽기 테스트")
    print("=" * 60)

    # ContactsReader 초기화
    reader = ContactsReader()

    # 모든 연락처 읽기
    contacts = reader.read_all_contacts()

    print(f"\n✅ 총 {len(contacts)}개의 연락처를 찾았습니다.\n")

    # 처음 5개만 출력
    for i, contact in enumerate(contacts[:5], 1):
        print(f"[{i}] {contact['name']}")
        print(f"    ID: {contact['contact_id']}")
        if contact['phone']:
            print(f"    전화: {contact['phone']}")
        if contact['email']:
            print(f"    이메일: {contact['email']}")
        if contact['notes']:
            notes_preview = contact['notes'][:50] + "..." if len(contact['notes']) > 50 else contact['notes']
            print(f"    메모: {notes_preview}")
        print()

    # 한글 이름 통계
    korean_contacts = [
        c for c in contacts
        if any('\uac00' <= ch <= '\ud7a3' for ch in c.get('name', ''))
    ]
    print(f"📊 통계:")
    print(f"   - 전체 연락처: {len(contacts)}개")
    print(f"   - 한글 이름: {len(korean_contacts)}개")
    print(f"   - 영문 이름: {len(contacts) - len(korean_contacts)}개")

    # 메모가 있는 연락처
    with_notes = [c for c in contacts if c['notes']]
    print(f"   - 메모 있음: {len(with_notes)}개")

if __name__ == '__main__':
    main()
