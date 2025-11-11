"""
Auto-Update Service

파일 시스템 변경을 감지하고 자동으로 인덱스를 업데이트하는 서비스
"""

import sys
import threading
import time
from collections import defaultdict
from pathlib import Path
from queue import Queue
from typing import Optional, Set

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from config import EXCLUDE_PATTERNS, VAULT_PATH


class FileWatcher(FileSystemEventHandler):
    """파일 시스템 변경 감지자

    watchdog를 사용하여 vault 폴더의 .md 파일 변경사항을 감지합니다.
    """

    def __init__(self, update_queue: "UpdateQueue"):
        """
        Args:
            update_queue: 변경사항을 전달할 UpdateQueue 인스턴스
        """
        self.update_queue = update_queue
        self.exclude_patterns = EXCLUDE_PATTERNS

    def _should_process(self, path: str) -> bool:
        """파일을 처리해야 하는지 확인

        Args:
            path: 파일 경로

        Returns:
            처리 여부
        """
        # .md 파일만 처리
        if not path.endswith(".md"):
            return False

        # 제외 패턴 확인
        for pattern in self.exclude_patterns:
            if pattern in path:
                return False

        return True

    def on_created(self, event: FileSystemEvent):
        """파일 생성 이벤트"""
        if not event.is_directory and self._should_process(event.src_path):
            self.update_queue.add_change("created", event.src_path)

    def on_modified(self, event: FileSystemEvent):
        """파일 수정 이벤트"""
        if not event.is_directory and self._should_process(event.src_path):
            self.update_queue.add_change("modified", event.src_path)

    def on_deleted(self, event: FileSystemEvent):
        """파일 삭제 이벤트"""
        if not event.is_directory and self._should_process(event.src_path):
            self.update_queue.add_change("deleted", event.src_path)

    def on_moved(self, event: FileSystemEvent):
        """파일 이동 이벤트"""
        # 이동은 삭제 + 생성으로 처리
        if not event.is_directory:
            if self._should_process(event.src_path):
                self.update_queue.add_change("deleted", event.src_path)
            if hasattr(event, 'dest_path') and self._should_process(event.dest_path):
                self.update_queue.add_change("created", event.dest_path)


class UpdateQueue:
    """변경사항 큐 및 배치 처리

    파일 변경사항을 큐에 모아서 일정 시간 후 배치로 처리합니다.
    """

    def __init__(self, indexer, debounce_seconds: float = 5.0):
        """
        Args:
            indexer: UnifiedIndexer 인스턴스
            debounce_seconds: 마지막 변경 후 대기 시간 (초)
        """
        self.indexer = indexer
        self.debounce_seconds = debounce_seconds

        # 변경사항 저장 (경로별로 최신 이벤트만 유지)
        self.pending_changes: dict[str, str] = {}  # {path: event_type}
        self.lock = threading.Lock()

        # 배치 처리 스레드
        self.processing_thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.change_event = threading.Event()

        # 실행 중 플래그
        self.running = False

    def add_change(self, event_type: str, path: str):
        """변경사항 추가

        Args:
            event_type: 이벤트 타입 (created, modified, deleted)
            path: 파일 경로
        """
        with self.lock:
            # 중복 제거: created와 modified는 모두 modified로 통합
            if event_type in ("created", "modified"):
                self.pending_changes[path] = "modified"
            else:
                self.pending_changes[path] = event_type

        # 변경사항이 추가되었음을 알림
        self.change_event.set()

    def start(self):
        """배치 처리 스레드 시작"""
        if self.running:
            return

        self.running = True
        self.stop_event.clear()

        self.processing_thread = threading.Thread(target=self._process_loop, daemon=True)
        self.processing_thread.start()

        print("🔄 Auto-Update Service 시작됨", file=sys.stderr)

    def stop(self):
        """배치 처리 스레드 중지"""
        if not self.running:
            return

        self.running = False
        self.stop_event.set()
        self.change_event.set()  # 대기 중인 스레드를 깨움

        if self.processing_thread:
            self.processing_thread.join(timeout=10)

        print("⏹️ Auto-Update Service 중지됨", file=sys.stderr)

    def _process_loop(self):
        """배치 처리 루프 (백그라운드 스레드에서 실행)"""
        while not self.stop_event.is_set():
            # 변경사항이 추가될 때까지 대기
            self.change_event.wait(timeout=1.0)

            if self.stop_event.is_set():
                break

            # debounce: 추가 변경사항이 없을 때까지 대기
            last_change_time = time.time()
            while time.time() - last_change_time < self.debounce_seconds:
                if self.stop_event.is_set():
                    return

                # 새로운 변경사항이 있는지 확인
                self.change_event.clear()
                if self.change_event.wait(timeout=0.5):
                    last_change_time = time.time()

            # 배치 처리 실행
            self._process_batch()

    def _process_batch(self):
        """현재 큐의 변경사항을 배치로 처리"""
        # 큐 복사 및 초기화
        with self.lock:
            if not self.pending_changes:
                return

            changes_to_process = self.pending_changes.copy()
            self.pending_changes.clear()

        try:
            print(f"\n🔄 자동 업데이트 시작: {len(changes_to_process)}개 파일", file=sys.stderr)

            # UnifiedIndexer의 update_index()는 check_updates()를 호출하므로
            # 파일 시스템을 직접 스캔합니다.
            # 우리는 그냥 update_index()를 호출하면 됩니다.
            self.indexer.update_index()

            print("✅ 자동 업데이트 완료\n", file=sys.stderr)

        except Exception as e:
            print(f"❌ 자동 업데이트 실패: {e}", file=sys.stderr)


class AutoUpdateService:
    """Auto-Update Service 메인 클래스

    FileWatcher와 UpdateQueue를 통합하여 자동 업데이트 서비스를 제공합니다.
    """

    def __init__(self, indexer, vault_path: Path = VAULT_PATH, debounce_seconds: float = 5.0):
        """
        Args:
            indexer: UnifiedIndexer 인스턴스
            vault_path: 감시할 vault 경로
            debounce_seconds: 변경 후 대기 시간 (초)
        """
        self.vault_path = vault_path
        self.indexer = indexer

        # 컴포넌트 생성
        self.update_queue = UpdateQueue(indexer, debounce_seconds)
        self.file_watcher = FileWatcher(self.update_queue)
        self.observer: Optional[Observer] = None

        # 실행 상태
        self.running = False

    def start(self):
        """서비스 시작"""
        if self.running:
            print("⚠️ Auto-Update Service가 이미 실행 중입니다", file=sys.stderr)
            return

        # UpdateQueue 시작
        self.update_queue.start()

        # FileWatcher (Observer) 시작
        self.observer = Observer()
        self.observer.schedule(self.file_watcher, str(self.vault_path), recursive=True)
        self.observer.start()

        self.running = True
        print(f"👁️ Vault 감시 시작: {self.vault_path}", file=sys.stderr)

    def stop(self):
        """서비스 중지"""
        if not self.running:
            return

        # Observer 중지
        if self.observer:
            self.observer.stop()
            self.observer.join(timeout=10)

        # UpdateQueue 중지
        self.update_queue.stop()

        self.running = False
        print("✅ Auto-Update Service 완전히 중지됨", file=sys.stderr)

    def __enter__(self):
        """컨텍스트 매니저 진입"""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료"""
        self.stop()
