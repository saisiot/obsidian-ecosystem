#!/usr/bin/env python3
"""
Fleet Note Generator (Claude Code CLI Edition)
손글씨 메모 이미지를 Obsidian Fleet Note로 변환하는 프로그램
"""

import sys
import os
import argparse
from config import Config
from ocr_processor import OCRProcessor
from md_processor import MarkdownProcessor
from note_generator import NoteGenerator
from file_manager import FileManager

def process_single_file(image_path, ocr_processor, note_generator, file_manager):
    """
    단일 이미지 파일 처리

    Args:
        image_path: 처리할 이미지 파일 경로
        ocr_processor: OCR 프로세서
        note_generator: 노트 생성기
        file_manager: 파일 관리자

    Returns:
        bool: 성공 여부
    """
    filename = os.path.basename(image_path)
    print(f"\n처리 중: {filename}")

    # OCR 및 분석
    print("  - 이미지 분석 중...")
    analysis_result = ocr_processor.extract_text_and_analyze(image_path)

    if not analysis_result:
        print("  ❌ 분석 실패")
        return False

    # 파일 이동
    print("  - 파일 이동 중...")
    moved_filename = file_manager.move_to_linked(image_path)

    if not moved_filename:
        print("  ❌ 파일 이동 실패")
        return False

    # 노트 생성
    print("  - 노트 생성 중...")
    note_path = note_generator.generate_note(analysis_result, filename, moved_filename)

    if not note_path:
        print("  ❌ 노트 생성 실패")
        return False

    print(f"  ✅ 완료: {analysis_result['title']}")
    return True

def process_single_markdown(md_path, md_processor, note_generator, file_manager):
    """
    단일 마크다운 파일 처리

    Args:
        md_path: 처리할 마크다운 파일 경로
        md_processor: 마크다운 프로세서
        note_generator: 노트 생성기
        file_manager: 파일 관리자

    Returns:
        bool: 성공 여부
    """
    filename = os.path.basename(md_path)
    print(f"\n📝 마크다운 처리 중: {filename}")

    # 마크다운 분석 및 개선
    print("  - 내용 분석 및 개선 중...")
    md_result = md_processor.process_markdown_file(md_path)

    if not md_result:
        print("  ❌ 분석 실패")
        return False

    # Fleet Note 생성
    print("  - Fleet Note 생성 중...")
    note_path = note_generator.generate_note_from_markdown(md_result)

    if not note_path:
        print("  ❌ Fleet Note 생성 실패")
        return False

    # 원본 마크다운 삭제
    print("  - 원본 파일 삭제 중...")
    file_manager.delete_markdown_file(md_path)

    print(f"  ✅ 완료: {md_result['title']}")
    return True

def process_batch(ocr_processor, md_processor, note_generator, file_manager):
    """
    폴더 배치 처리 (이미지 + 마크다운)

    Args:
        ocr_processor: OCR 프로세서
        md_processor: 마크다운 프로세서
        note_generator: 노트 생성기
        file_manager: 파일 관리자

    Returns:
        tuple: (성공 개수, 실패 개수)
    """
    # 처리 대기 파일 확인
    all_pending = file_manager.get_all_pending_files()
    pending_images = all_pending['images']
    pending_markdown = all_pending['markdown']
    stats = file_manager.get_stats()

    print(f"처리 대기 이미지: {len(pending_images)}개")
    print(f"처리 대기 마크다운: {len(pending_markdown)}개")
    print(f"처리 완료 이미지: {stats['processed']}개")
    print("-" * 30)

    if not pending_images and not pending_markdown:
        print("처리할 파일이 없습니다.")
        print(f"'{Config.ORIGINAL_NOTES_DIR}' 폴더에 이미지 또는 마크다운 파일을 넣어주세요.")
        print(f"생성된 노트는 '{Config.GENERATED_NOTES_DIR}' 폴더에 저장됩니다.")
        return 0, 0

    # 파일 처리 카운터
    processed_count = 0
    failed_count = 0

    # 1. 이미지 파일 처리
    if pending_images:
        print(f"\n🖼️  이미지 파일 처리 시작 ({len(pending_images)}개)")
        print("-" * 30)

        for i, image_path in enumerate(pending_images, 1):
            filename = os.path.basename(image_path)
            print(f"\n[{i}/{len(pending_images)}] 처리 중: {filename}")

            # OCR 및 분석
            print("  - 이미지 분석 중...")
            analysis_result = ocr_processor.extract_text_and_analyze(image_path)

            if not analysis_result:
                print("  ❌ 분석 실패")
                failed_count += 1
                continue

            # 파일 이동
            print("  - 파일 이동 중...")
            moved_filename = file_manager.move_to_linked(image_path)

            if not moved_filename:
                print("  ❌ 파일 이동 실패")
                failed_count += 1
                continue

            # 노트 생성
            print("  - 노트 생성 중...")
            note_path = note_generator.generate_note(analysis_result, filename, moved_filename)

            if not note_path:
                print("  ❌ 노트 생성 실패")
                failed_count += 1
                continue

            print(f"  ✅ 완료: {analysis_result['title']}")
            processed_count += 1

    # 2. 마크다운 파일 처리
    if pending_markdown:
        print(f"\n📝 마크다운 파일 처리 시작 ({len(pending_markdown)}개)")
        print("-" * 30)

        for i, md_path in enumerate(pending_markdown, 1):
            filename = os.path.basename(md_path)
            print(f"\n[{i}/{len(pending_markdown)}] 처리 중: {filename}")

            # 마크다운 분석 및 개선
            print("  - 내용 분석 및 개선 중...")
            md_result = md_processor.process_markdown_file(md_path)

            if not md_result:
                print("  ❌ 분석 실패")
                failed_count += 1
                continue

            # Fleet Note 생성
            print("  - Fleet Note 생성 중...")
            note_path = note_generator.generate_note_from_markdown(md_result)

            if not note_path:
                print("  ❌ Fleet Note 생성 실패")
                failed_count += 1
                continue

            # 원본 마크다운 삭제
            print("  - 원본 파일 삭제 중...")
            file_manager.delete_markdown_file(md_path)

            print(f"  ✅ 완료: {md_result['title']}")
            processed_count += 1

    return processed_count, failed_count

def main():
    """메인 실행 함수"""
    # 명령줄 인자 파싱
    parser = argparse.ArgumentParser(
        description='손글씨 메모 이미지를 Obsidian Fleet Note로 변환',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--file', '-f',
        type=str,
        help='단일 이미지 파일 경로 (지정하지 않으면 배치 모드)'
    )

    parser.add_argument(
        '--batch', '-b',
        action='store_true',
        help='배치 모드 (original_notes 폴더의 모든 이미지 처리)'
    )

    args = parser.parse_args()

    print("=" * 50)
    print("Fleet Note Generator (Claude Code CLI Edition)")
    print("=" * 50)

    try:
        # 설정 검증 및 디렉토리 생성
        Config.validate_config()
        Config.create_directories()

        # 폴더 정보 출력
        Config.print_directory_info()

        # 컴포넌트 초기화
        ocr_processor = OCRProcessor()
        md_processor = MarkdownProcessor()
        note_generator = NoteGenerator()
        file_manager = FileManager()

        # 단일 파일 모드
        if args.file:
            if not os.path.exists(args.file):
                print(f"오류: 파일을 찾을 수 없습니다: {args.file}")
                return 1

            # 파일 형식 확인 (이미지 or 마크다운)
            file_ext = args.file.lower().split('.')[-1]

            if file_ext in Config.SUPPORTED_MARKDOWN_FORMATS:
                # 마크다운 파일 처리
                success = process_single_markdown(args.file, md_processor, note_generator, file_manager)
            elif file_ext in Config.SUPPORTED_IMAGE_FORMATS:
                # 이미지 파일 처리
                success = process_single_file(args.file, ocr_processor, note_generator, file_manager)
            else:
                print(f"❌ 지원하지 않는 파일 형식입니다: {file_ext}")
                print(f"지원 형식: 이미지({', '.join(Config.SUPPORTED_IMAGE_FORMATS)}), 마크다운({', '.join(Config.SUPPORTED_MARKDOWN_FORMATS)})")
                return 1

            print("\n" + "=" * 50)
            if success:
                print("처리 완료!")
            else:
                print("처리 실패!")
            print("=" * 50)

            return 0 if success else 1

        # 배치 모드
        else:
            processed_count, failed_count = process_batch(ocr_processor, md_processor, note_generator, file_manager)

            # 결과 요약
            print("\n" + "=" * 50)
            print("처리 완료!")
            print(f"성공: {processed_count}개")
            print(f"실패: {failed_count}개")
            print("=" * 50)

            return 0 if failed_count == 0 else 1

    except ValueError as e:
        print(f"설정 오류: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n\n처리가 중단되었습니다.")
        return 1
    except Exception as e:
        print(f"예상치 못한 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
