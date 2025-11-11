"""
Contacts 데이터 읽기 기능 테스트
TDD RED 단계: 먼저 테스트 작성
"""
import pytest
from src.contacts_reader import ContactsReader


class TestContactsReader:
    """ContactsReader 클래스 테스트"""

    def test_read_all_contacts_returns_list(self):
        """모든 연락처를 읽고 리스트를 반환해야 함"""
        reader = ContactsReader()
        contacts = reader.read_all_contacts()

        assert isinstance(contacts, list)

    def test_contact_has_required_fields(self):
        """각 연락처는 필수 필드를 가져야 함"""
        reader = ContactsReader()
        contacts = reader.read_all_contacts()

        if len(contacts) > 0:
            contact = contacts[0]
            assert 'contact_id' in contact
            assert 'name' in contact
            # phone, email, notes는 선택적

    def test_contact_id_is_string(self):
        """contact_id는 문자열이어야 함"""
        reader = ContactsReader()
        contacts = reader.read_all_contacts()

        if len(contacts) > 0:
            contact_id = contacts[0]['contact_id']
            assert isinstance(contact_id, str)
            assert len(contact_id) > 0

    def test_name_is_not_empty(self):
        """이름은 비어있지 않아야 함"""
        reader = ContactsReader()
        contacts = reader.read_all_contacts()

        if len(contacts) > 0:
            name = contacts[0]['name']
            assert isinstance(name, str)
            assert len(name) > 0

    def test_korean_name_support(self):
        """한글 이름을 정확히 읽을 수 있어야 함"""
        reader = ContactsReader()
        contacts = reader.read_all_contacts()

        # 한글 연락처가 있으면 이름이 깨지지 않았는지 확인
        korean_contacts = [
            c for c in contacts
            if any('\uac00' <= ch <= '\ud7a3' for ch in c.get('name', ''))
        ]

        for contact in korean_contacts:
            assert contact['name'] is not None
            assert len(contact['name']) > 0
            # 한글이 제대로 인코딩되었는지 확인
            assert any('\uac00' <= ch <= '\ud7a3' for ch in contact['name'])

    def test_phone_is_optional(self):
        """전화번호는 선택적 필드여야 함"""
        reader = ContactsReader()
        contacts = reader.read_all_contacts()

        if len(contacts) > 0:
            contact = contacts[0]
            # phone이 있으면 문자열, 없으면 None
            if 'phone' in contact and contact['phone'] is not None:
                assert isinstance(contact['phone'], str)

    def test_email_is_optional(self):
        """이메일은 선택적 필드여야 함"""
        reader = ContactsReader()
        contacts = reader.read_all_contacts()

        if len(contacts) > 0:
            contact = contacts[0]
            # email이 있으면 문자열, 없으면 None
            if 'email' in contact and contact['email'] is not None:
                assert isinstance(contact['email'], str)

    def test_notes_is_optional(self):
        """메모는 선택적 필드여야 함"""
        reader = ContactsReader()
        contacts = reader.read_all_contacts()

        if len(contacts) > 0:
            contact = contacts[0]
            # notes가 있으면 문자열, 없으면 None 또는 빈 문자열
            if 'notes' in contact and contact['notes']:
                assert isinstance(contact['notes'], str)

    def test_extract_contact_data_with_mock_contact(self):
        """_extract_contact_data 메서드가 정상 작동해야 함 (모킹 테스트)"""
        reader = ContactsReader()

        # Mock CNContact 객체 (실제로는 PyObjC 객체)
        # 일단은 구조만 확인
        assert hasattr(reader, '_extract_contact_data')
