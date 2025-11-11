"""
샘플 테스트 - pytest 환경 검증용
"""
import pytest


class TestSample:
    """샘플 테스트 클래스"""

    def test_fixture_sample_contacts(self, sample_contacts):
        """sample_contacts 픽스처가 정상 작동하는지 확인"""
        assert isinstance(sample_contacts, list)
        assert len(sample_contacts) > 0
        assert 'contact_id' in sample_contacts[0]

    def test_fixture_temp_vault(self, temp_vault):
        """temp_vault 픽스처가 정상 작동하는지 확인"""
        assert temp_vault.exists()
        assert temp_vault.is_dir()
        assert temp_vault.name == "07 people"

    def test_fixture_temp_db(self, temp_db):
        """temp_db 픽스처가 정상 작동하는지 확인"""
        assert temp_db.name == ".contacts.db"
        assert temp_db.parent.exists()

    def test_fixture_sample_memo_simple(self, sample_memo_simple):
        """sample_memo_simple 픽스처가 정상 작동하는지 확인"""
        assert isinstance(sample_memo_simple, str)
        assert "250115" in sample_memo_simple

    def test_fixture_sample_contact_dict(self, sample_contact_dict):
        """sample_contact_dict 픽스처가 정상 작동하는지 확인"""
        assert sample_contact_dict['contact_id'] == 'ABC-123-DEF-456-789'
        assert sample_contact_dict['name'] == '홍길동'

    def test_fixture_sample_interactions(self, sample_interactions):
        """sample_interactions 픽스처가 정상 작동하는지 확인"""
        assert len(sample_interactions) == 3
        assert 'date' in sample_interactions[0]
        assert 'content' in sample_interactions[0]

    def test_fixture_sample_stats(self, sample_stats):
        """sample_stats 픽스처가 정상 작동하는지 확인"""
        assert 'last_contact' in sample_stats
        assert 'contact_count' in sample_stats
        assert sample_stats['contact_count'] == 3
