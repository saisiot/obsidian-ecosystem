"""
마크다운 파일 처리 모듈
YYMMDD 타이틀.md 형식의 메모를 Fleet Note로 변환
"""

import os
import re
from datetime import datetime
from claude_cli_wrapper import ClaudeCliWrapper


class MarkdownProcessor:
    """마크다운 메모를 Fleet Note로 변환하는 프로세서"""

    def __init__(self):
        self.claude_wrapper = ClaudeCliWrapper()

    def parse_filename(self, filename):
        """
        파일명에서 날짜와 제목 추출
        예: '250129 회의 메모.md' -> ('2025-01-29', '회의 메모')
        예: '250129_회의_메모.md' -> ('2025-01-29', '회의 메모')

        Args:
            filename: 파일명 (YYMMDD 타이틀.md 또는 YYMMDD_타이틀.md 형식)

        Returns:
            tuple: (날짜(YYYY-MM-DD), 제목) 또는 (None, None)
        """
        # .md 확장자 제거
        name_without_ext = filename.replace('.md', '')

        # YYMMDD 패턴 매칭 (공백 또는 언더스코어 구분)
        pattern = r'^(\d{6})[\s_]+(.+)$'
        match = re.match(pattern, name_without_ext)

        if not match:
            return None, None

        date_str = match.group(1)  # YYMMDD
        title = match.group(2).strip()

        # 언더스코어를 공백으로 변환
        title = title.replace('_', ' ')

        # YYMMDD -> YYYY-MM-DD 변환
        try:
            year = int('20' + date_str[0:2])
            month = int(date_str[2:4])
            day = int(date_str[4:6])
            date_obj = datetime(year, month, day)
            formatted_date = date_obj.strftime('%Y-%m-%d')
            return formatted_date, title
        except (ValueError, IndexError):
            return None, None

    def extract_tags_from_content(self, content):
        """
        본문에서 해시태그 추출 및 제거

        Args:
            content: 마크다운 본문

        Returns:
            tuple: (태그 리스트, 태그가 제거된 본문)
        """
        # 해시태그 패턴: #태그 (공백이나 줄바꿈 전까지)
        tag_pattern = r'#(\w+)'
        tags = re.findall(tag_pattern, content)

        # 본문에서 해시태그 제거 (중복 공백도 정리)
        content_without_tags = re.sub(tag_pattern, '', content)
        content_without_tags = re.sub(r'\s+', ' ', content_without_tags).strip()

        # 중복 태그 제거
        unique_tags = list(dict.fromkeys(tags))

        return unique_tags, content_without_tags

    def improve_content_with_claude(self, content, title):
        """
        Claude CLI를 사용하여 내용 개선
        - 오타 수정
        - 문장 정리
        - 노트 연결 추천

        Args:
            content: 원본 내용
            title: 제목

        Returns:
            dict: {
                'improved_content': 개선된 내용,
                'suggested_links': 추천 노트 링크 리스트
            }
        """
        prompt = f"""다음 마크다운 메모를 Fleet Note 형식으로 개선해주세요.

제목: {title}
내용:
{content}

작업 내용:
1. 오타 수정 및 문장 다듬기 (한국어 맞춤법)
2. 불렛포인트 형식 정리 (- 또는 * 사용)
3. 관련 있을 것 같은 노트 주제 추천 (Obsidian 내부 링크 형식: [[노트 이름]])

다음 형식으로 응답해주세요:
**개선된 내용:**
[개선된 마크다운 내용]

**추천 연결:**
[추천 노트 링크들, 각 줄에 하나씩. 없으면 "없음"]
"""

        try:
            # Claude CLI 직접 호출 (이미지 없이)
            import subprocess
            result = subprocess.run(
                [
                    'claude',
                    '-p',
                    '--dangerously-skip-permissions',
                    prompt
                ],
                capture_output=True,
                text=True,
                timeout=60
            )

            if result.returncode != 0:
                print(f"  - Claude CLI 실행 실패 (exit code: {result.returncode})")
                return {
                    'improved_content': content,
                    'suggested_links': []
                }

            response = result.stdout.strip()

            if not response:
                # Claude 호출 실패 시 원본 반환
                return {
                    'improved_content': content,
                    'suggested_links': []
                }

            # 응답 파싱
            improved_content = ""
            suggested_links = []

            lines = response.strip().split('\n')
            current_section = None

            for line in lines:
                line_stripped = line.strip()

                if '**개선된 내용:**' in line_stripped or '**개선된 내용**' in line_stripped:
                    current_section = 'content'
                    continue
                elif '**추천 연결:**' in line_stripped or '**추천 연결**' in line_stripped:
                    current_section = 'links'
                    continue

                if current_section == 'content' and line_stripped:
                    improved_content += line + '\n'
                elif current_section == 'links' and line_stripped and line_stripped != '없음':
                    # [[노트 이름]] 형식 추출
                    link_pattern = r'\[\[([^\]]+)\]\]'
                    found_links = re.findall(link_pattern, line_stripped)
                    suggested_links.extend(found_links)

            return {
                'improved_content': improved_content.strip() if improved_content else content,
                'suggested_links': suggested_links
            }

        except Exception as e:
            print(f"⚠️  Claude 개선 실패: {e}")
            return {
                'improved_content': content,
                'suggested_links': []
            }

    def process_markdown_file(self, md_file_path):
        """
        마크다운 파일 전체 처리

        Args:
            md_file_path: 마크다운 파일 경로

        Returns:
            dict: {
                'title': 제목,
                'date': 날짜 (YYYY-MM-DD),
                'tags': 태그 리스트,
                'improved_content': 개선된 내용,
                'suggested_links': 추천 링크 리스트
            } 또는 None (실패 시)
        """
        if not os.path.exists(md_file_path):
            print(f"❌ 파일을 찾을 수 없습니다: {md_file_path}")
            return None

        # 파일명에서 날짜와 제목 추출
        filename = os.path.basename(md_file_path)
        date, title = self.parse_filename(filename)

        if not date or not title:
            print(f"❌ 파일명 형식 오류: {filename} (YYMMDD 타이틀.md 형식이어야 합니다)")
            return None

        # 파일 내용 읽기
        try:
            with open(md_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"❌ 파일 읽기 실패: {e}")
            return None

        # 태그 추출
        tags, content_without_tags = self.extract_tags_from_content(content)

        # Claude로 내용 개선
        print(f"🤖 Claude로 내용 개선 중: {title}")
        improvement_result = self.improve_content_with_claude(content_without_tags, title)

        return {
            'title': title,
            'date': date,
            'tags': tags,
            'improved_content': improvement_result['improved_content'],
            'suggested_links': improvement_result['suggested_links'],
            'original_path': md_file_path
        }
