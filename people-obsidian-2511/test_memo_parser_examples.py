#!/usr/bin/env python3
"""
MemoParser 사용 예제 및 테스트
"""
from src.memo_parser import MemoParser
from datetime import date


def main():
    print("=" * 60)
    print("MemoParser 사용 예제")
    print("=" * 60)

    parser = MemoParser()

    # 예제 1: YYMMDD 형식
    print("\n[예제 1] YYMMDD 형식")
    memo1 = "250115 점심 미팅. 새 프로젝트 논의"
    interactions1 = parser.parse(memo1)
    for i in interactions1:
        print(f"  날짜: {i['date']} | 내용: {i['content']}")

    # 예제 2: 여러 엔트리
    print("\n[예제 2] 여러 엔트리")
    memo2 = """250115 점심 미팅
250110 전화 통화
241220 연말 인사"""
    interactions2 = parser.parse(memo2)
    for i in interactions2:
        print(f"  날짜: {i['date']} | 내용: {i['content']}")

    # 예제 3: 줄바꿈이 포함된 내용
    print("\n[예제 3] 줄바꿈이 포함된 내용")
    memo3 = """251110 생일날만남
같이 카페에가서 커피 한잔하고 선물받음
정말 즐거운 시간이었음

251101 전화로 연락함"""
    interactions3 = parser.parse(memo3)
    for i in interactions3:
        print(f"  날짜: {i['date']}")
        print(f"  내용:\n{i['content']}")
        print()

    # 예제 4: 자연어 날짜
    print("\n[예제 4] 자연어 날짜")
    memo4 = """오늘 커피 미팅
어제 전화함
250115 점심 약속"""
    interactions4 = parser.parse(memo4)
    for i in interactions4:
        print(f"  날짜: {i['date']} | 내용: {i['content']}")

    # 예제 5: 실제 사용 시나리오 (PRD 예시)
    print("\n[예제 5] 실제 사용 시나리오")
    real_memo = """250115 점심 미팅. 새 프로젝트 논의. AI 도입 방안에 대해 이야기 나눔.
250110 전화 통화. 다음 주 일정 조율.
241220 연말 인사. 내년에도 잘 부탁한다고.
241110 서울 AI 컨퍼런스에서 만남. 명함 교환."""
    real_interactions = parser.parse(real_memo)

    print(f"\n  총 {len(real_interactions)}개의 interaction 파싱됨:")
    for idx, i in enumerate(real_interactions, 1):
        print(f"\n  [{idx}] {i['date']}")
        print(f"      {i['content']}")

    print("\n" + "=" * 60)
    print("✅ 모든 예제 실행 완료")
    print("=" * 60)


if __name__ == '__main__':
    main()
