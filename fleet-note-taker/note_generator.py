import os
from datetime import datetime
from config import Config

class NoteGenerator:
    def __init__(self):
        pass
    
    def generate_note(self, analysis_result, image_filename, moved_filename=None):
        """분석 결과를 바탕으로 마크다운 노트 생성"""
        try:
            # LLM에서 추출한 날짜 사용
            if analysis_result.get('date'):
                # 메모에서 추출한 날짜를 2025년으로 가정
                extracted_date = analysis_result['date']
                # YYMMDD 형식에서 MM과 DD 추출
                month = extracted_date[2:4]  # 3-4번째 문자 (월)
                day = extracted_date[4:6]    # 5-6번째 문자 (일)
                current_date = f"2025-{month}-{day}"
                current_date_compact = f"2025{extracted_date}"
            else:
                # 날짜 추출 실패 시 현재 날짜 사용
                current_date = datetime.now().strftime('%Y-%m-%d')
                current_date_compact = datetime.now().strftime('%Y%m%d')
            
            # 태그 문자열 생성 (메타데이터용 - 쉼표로 구분, # 제거)
            tags_str = '[' + ', '.join(analysis_result['tags']) + ']'
            
            # 이미지 링크 경로 - 이동된 파일명 사용
            if moved_filename:
                # Config.LINKED_NOTES_DIR의 상대 경로 계산
                linked_dir_name = os.path.basename(Config.LINKED_NOTES_DIR)
                image_link = f"{linked_dir_name}/{moved_filename}"
            else:
                # fallback: 원본 파일명 사용
                linked_dir_name = os.path.basename(Config.LINKED_NOTES_DIR)
                image_link = f"{linked_dir_name}/{image_filename}"
            
            # 템플릿에 데이터 삽입
            note_content = Config.FLEET_TEMPLATE.format(
                title=analysis_result['title'],
                created_date=current_date,
                tags=tags_str,
                notes=analysis_result['notes'],
                image_link=image_link
            )
            
            # 파일명 생성 (LLM에서 추출한 날짜 사용)
            if analysis_result.get('date'):
                filename = f"{analysis_result['date']}_{analysis_result['title']}.md"
            else:
                filename = f"{current_date_compact}_{analysis_result['title']}.md"
            
            filepath = os.path.join(Config.GENERATED_NOTES_DIR, filename)
            
            # 파일 중복 확인 및 처리
            filepath = self._ensure_unique_filename(filepath)
            
            # 파일 저장
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(note_content)
            
            print(f"노트 생성 완료: {os.path.basename(filepath)}")
            return filepath
            
        except Exception as e:
            print(f"노트 생성 중 오류 발생: {e}")
            return None
    
    def generate_note_from_markdown(self, md_result):
        """
        마크다운 처리 결과를 Fleet Note로 생성

        Args:
            md_result: MarkdownProcessor.process_markdown_file()의 반환값
                {
                    'title': 제목,
                    'date': 날짜 (YYYY-MM-DD),
                    'tags': 태그 리스트,
                    'improved_content': 개선된 내용,
                    'suggested_links': 추천 링크 리스트
                }

        Returns:
            str: 생성된 파일 경로 또는 None (실패 시)
        """
        try:
            # 날짜 형식 변환: YYYY-MM-DD -> YYMMDD
            date_obj = datetime.strptime(md_result['date'], '%Y-%m-%d')
            date_compact = date_obj.strftime('%y%m%d')  # YYMMDD

            # 태그 문자열 생성 (메타데이터용)
            if md_result['tags']:
                tags_str = '[' + ', '.join(md_result['tags']) + ']'
            else:
                tags_str = '[]'

            # 추천 링크 문자열 생성
            if md_result['suggested_links']:
                links_str = '\n'.join([f"- [[{link}]]" for link in md_result['suggested_links']])
            else:
                links_str = '-'

            # 템플릿에 데이터 삽입
            note_content = Config.FLEET_TEMPLATE_MD.format(
                title=md_result['title'],
                created_date=md_result['date'],
                tags=tags_str,
                notes=md_result['improved_content'],
                links=links_str
            )

            # 파일명 생성: YYMMDD_타이틀.md
            filename = f"{date_compact}_{md_result['title']}.md"
            filepath = os.path.join(Config.GENERATED_NOTES_DIR, filename)

            # 파일 중복 확인 및 처리
            filepath = self._ensure_unique_filename(filepath)

            # 파일 저장
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(note_content)

            print(f"✅ Fleet Note 생성 완료: {os.path.basename(filepath)}")
            return filepath

        except Exception as e:
            print(f"❌ Fleet Note 생성 중 오류 발생: {e}")
            return None

    def _ensure_unique_filename(self, filepath):
        """중복 파일명 처리"""
        if not os.path.exists(filepath):
            return filepath

        base_path, extension = os.path.splitext(filepath)
        counter = 1

        while os.path.exists(filepath):
            filepath = f"{base_path}_{counter:02d}{extension}"
            counter += 1

        return filepath