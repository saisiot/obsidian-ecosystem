#!/usr/bin/env python3
"""
JXA (JavaScript for Automation) 속도 테스트
"""
import subprocess
import time
import json

print("=" * 60)
print("JXA vs AppleScript 속도 비교")
print("=" * 60)

# JXA 스크립트 (50개 연락처)
jxa_script = '''
const app = Application('Contacts');
const people = app.people();

const contacts = [];
const limit = Math.min(50, people.length);

for (let i = 0; i < limit; i++) {
    const person = people[i];
    try {
        const contact = {
            id: person.id(),
            name: person.name(),
            phone: person.phones.length > 0 ? person.phones[0].value() : null,
            email: person.emails.length > 0 ? person.emails[0].value() : null,
            note: person.note() || null
        };
        contacts.push(contact);
    } catch (e) {
        // Skip errors
    }
}

JSON.stringify(contacts);
'''

print("\n[1] JXA 테스트...")
start_time = time.time()

result = subprocess.run(
    ['osascript', '-l', 'JavaScript', '-e', jxa_script],
    capture_output=True,
    text=True,
    timeout=60
)

jxa_time = time.time() - start_time

if result.returncode == 0:
    contacts = json.loads(result.stdout.strip())
    print(f"✅ 성공: {len(contacts)}개 연락처")
    print(f"   소요 시간: {jxa_time:.2f}초")
    print(f"   초당 처리: {len(contacts)/jxa_time:.1f}개/초")

    # 처음 2개 미리보기
    print(f"\n   처음 2개:")
    for contact in contacts[:2]:
        print(f"   - {contact['name']}")
        if contact['note']:
            preview = contact['note'][:40].replace('\n', ' ')
            print(f"     메모: {preview}...")
else:
    print(f"❌ 실패: {result.stderr}")

print("\n" + "=" * 60)
print(f"💡 예상 전체 처리 시간 (416개):")
if result.returncode == 0 and len(contacts) > 0:
    total_time = (416 / len(contacts)) * jxa_time
    print(f"   약 {total_time:.1f}초 = {total_time/60:.1f}분")
print("=" * 60)
