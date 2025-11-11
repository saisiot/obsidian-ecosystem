import asyncio
import sys
from pathlib import Path
from typing import Optional, List
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions
import mcp.server.stdio
import mcp.types as types

# 현재 디렉토리를 sys.path에 추가
sys.path.insert(0, str(Path(__file__).parent))

from config import *
from vector_store import VectorStore
from indexer import UnifiedIndexer
from network_store import NetworkMetadataStore
from repomix_store import RepomixIndexStore
from obsidian_parser import ObsidianParser
from auto_update_service import AutoUpdateService
from context_packer import ContextPacker

# 서버 초기화
server = Server("obsidian-rag")
vector_store = None
indexer = None
parser = ObsidianParser()
auto_update_service = None
context_packer = None

@server.list_tools()
async def handle_list_tools() -> list[types.Tool]:
    """사용 가능한 도구 목록"""
    return [
        types.Tool(
            name="search_notes",
            description="Obsidian 노트를 시맨틱 검색합니다",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "검색 쿼리"},
                    "top_k": {"type": "integer", "description": "결과 개수", "default": 5},
                    "folder": {"type": "string", "description": "PARA 폴더 필터"}
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="get_note",
            description="특정 노트의 전체 내용을 가져옵니다",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string", "description": "노트 제목"}
                },
                "required": ["title"]
            }
        ),
        types.Tool(
            name="find_related",
            description="연관된 노트를 찾습니다",
            inputSchema={
                "type": "object",
                "properties": {
                    "note_path": {"type": "string", "description": "노트 경로"},
                    "top_k": {"type": "integer", "description": "결과 개수", "default": 5}
                },
                "required": ["note_path"]
            }
        ),
        types.Tool(
            name="search_by_tag",
            description="태그로 노트를 검색합니다",
            inputSchema={
                "type": "object",
                "properties": {
                    "tag": {"type": "string", "description": "검색할 태그"}
                },
                "required": ["tag"]
            }
        ),
        types.Tool(
            name="get_backlinks",
            description="특정 노트를 참조하는 모든 노트를 찾습니다",
            inputSchema={
                "type": "object",
                "properties": {
                    "note_title": {"type": "string", "description": "노트 제목"}
                },
                "required": ["note_title"]
            }
        ),
        types.Tool(
            name="get_vault_stats",
            description="볼트 통계를 가져옵니다",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="update_index",
            description="인덱스를 수동으로 업데이트합니다 (자동 업데이트 서비스가 활성화되어 있지만, 필요시 즉시 수동 업데이트 가능)",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        types.Tool(
            name="pack_note_context",
            description="노트와 관련된 모든 컨텍스트를 LLM에 최적화된 형태로 패키징합니다 (백링크, 포워드링크, 시맨틱 유사 노트 포함)",
            inputSchema={
                "type": "object",
                "properties": {
                    "note_title": {"type": "string", "description": "패키징할 노트 제목"},
                    "max_tokens": {"type": "integer", "description": "최대 토큰 수", "default": 100000},
                    "include_backlinks": {"type": "boolean", "description": "백링크 포함", "default": True},
                    "include_forward_links": {"type": "boolean", "description": "포워드링크 포함", "default": True},
                    "include_semantic_related": {"type": "boolean", "description": "시맨틱 유사 노트 포함", "default": True},
                    "max_backlinks": {"type": "integer", "description": "최대 백링크 수", "default": 10},
                    "max_forward_links": {"type": "integer", "description": "최대 포워드링크 수", "default": 10},
                    "max_semantic_related": {"type": "integer", "description": "최대 시맨틱 유사 노트 수", "default": 5}
                },
                "required": ["note_title"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(
    name: str,
    arguments: dict
) -> list[types.TextContent]:
    """도구 실행"""

    if name == "search_notes":
        results = vector_store.search(
            query=arguments["query"],
            top_k=arguments.get("top_k", 5),
            folder=arguments.get("folder")
        )

        response = f"🔍 '{arguments['query']}' 검색 결과:\n\n"
        for i, result in enumerate(results, 1):
            response += f"{i}. **{result['title']}**\n"
            response += f"   📁 {result['metadata']['para_folder']}\n"
            response += f"   📝 {result['content'][:200]}...\n"
            response += f"   🏷️ {result['metadata'].get('tags', '없음')}\n\n"

        return [types.TextContent(type="text", text=response)]

    elif name == "get_note":
        # 노트 찾기 로직
        title = arguments["title"]
        results = vector_store.collection.get(
            where={"title": title}
        )

        if results['ids']:
            # 동일한 경로의 모든 청크를 모아서 전체 내용 재구성
            path = results['metadatas'][0]['path']
            all_chunks = vector_store.collection.get(
                where={"path": path}
            )

            # chunk_index 순서로 정렬
            chunks_with_index = list(zip(
                all_chunks['metadatas'],
                all_chunks['documents']
            ))
            chunks_with_index.sort(key=lambda x: x[0]['chunk_index'])

            full_content = '\n'.join([chunk[1] for chunk in chunks_with_index])
            metadata = chunks_with_index[0][0]

            response = f"📄 **{title}**\n\n"
            response += f"📁 폴더: {metadata['para_folder']}\n"
            response += f"🏷️ 태그: {metadata.get('tags', '없음')}\n"
            response += f"🔗 위키링크: {metadata.get('wiki_links', '없음')}\n\n"
            response += f"**내용:**\n{full_content}"

            return [types.TextContent(type="text", text=response)]
        else:
            return [types.TextContent(type="text", text=f"'{title}' 노트를 찾을 수 없습니다.")]

    elif name == "find_related":
        # 연관 노트 찾기
        note_path = arguments["note_path"]
        # 현재 노트 읽기
        note_file = Path(note_path)
        if note_file.exists():
            doc = parser.parse_file(note_file)
            # 노트 내용으로 유사 검색
            results = vector_store.search(
                query=doc['content'][:500],  # 앞부분만 사용
                top_k=arguments.get("top_k", 5) + 1  # 자기 자신 제외
            )

            # 자기 자신 제외
            results = [r for r in results if r['path'] != note_path][:arguments.get("top_k", 5)]

            response = f"🔗 '{doc['title']}'와 연관된 노트:\n\n"
            for i, result in enumerate(results, 1):
                response += f"{i}. **{result['title']}**\n"
                response += f"   📁 {result['metadata']['para_folder']}\n"
                response += f"   📝 {result['content'][:200]}...\n\n"

            return [types.TextContent(type="text", text=response)]
        else:
            return [types.TextContent(type="text", text=f"'{note_path}' 경로를 찾을 수 없습니다.")]

    elif name == "search_by_tag":
        # 태그 검색
        tag = arguments["tag"]
        results = vector_store.collection.get(
            where_document={"$contains": f"#{tag}"}
        )

        # 중복 제거 (path 기준)
        unique_notes = {}
        for i, metadata in enumerate(results['metadatas']):
            path = metadata['path']
            if path not in unique_notes:
                unique_notes[path] = {
                    'title': metadata['title'],
                    'para_folder': metadata['para_folder'],
                    'tags': metadata.get('tags', '')
                }

        response = f"🏷️ '#{tag}' 태그가 있는 노트 ({len(unique_notes)}개):\n\n"
        for i, (path, note) in enumerate(unique_notes.items(), 1):
            response += f"{i}. **{note['title']}**\n"
            response += f"   📁 {note['para_folder']}\n"
            response += f"   🏷️ {note['tags']}\n\n"

        return [types.TextContent(type="text", text=response)]

    elif name == "get_backlinks":
        # 백링크 찾기
        note_title = arguments["note_title"]

        # 모든 노트에서 위키링크 검색
        results = vector_store.collection.get()

        backlinks = set()
        for metadata in results['metadatas']:
            wiki_links = metadata.get('wiki_links', '').split(',')
            if note_title in wiki_links:
                backlinks.add((metadata['path'], metadata['title'], metadata['para_folder']))

        response = f"⬅️ '{note_title}'를 참조하는 노트 ({len(backlinks)}개):\n\n"
        for i, (path, title, folder) in enumerate(sorted(backlinks), 1):
            response += f"{i}. **{title}**\n"
            response += f"   📁 {folder}\n"
            response += f"   📄 {path}\n\n"

        return [types.TextContent(type="text", text=response)]

    elif name == "get_vault_stats":
        # 통계 생성
        total_notes = len(indexer.metadata['indexed_files'])

        # PARA 폴더별 분포
        para_distribution = {}
        for file_path in indexer.metadata['indexed_files'].keys():
            path = Path(file_path)
            try:
                para_folder = path.relative_to(VAULT_PATH).parts[0]
                para_distribution[para_folder] = para_distribution.get(para_folder, 0) + 1
            except:
                pass

        response = "📊 **Vault 통계**\n\n"
        response += f"📝 전체 노트 수: {total_notes}개\n"
        response += f"⏰ 마지막 업데이트: {indexer.metadata.get('last_update', 'Never')}\n\n"
        response += "**PARA 폴더별 분포:**\n"
        for folder, count in sorted(para_distribution.items()):
            response += f"  - {folder}: {count}개\n"

        return [types.TextContent(type="text", text=response)]

    elif name == "update_index":
        # 인덱스 수동 업데이트
        print("📊 인덱스 업데이트 시작...", file=sys.stderr)
        updates = indexer.check_updates()

        response = "🔄 **인덱스 업데이트**\n\n"
        response += f"📥 새 파일: {len(updates['new'])}개\n"
        response += f"📝 수정된 파일: {len(updates['modified'])}개\n"
        response += f"🗑️ 삭제된 파일: {len(updates['deleted'])}개\n\n"

        if any(updates.values()):
            indexer.update_index()
            response += "✅ 인덱스 업데이트 완료!"
        else:
            response += "✅ 변경사항 없음. 인덱스가 최신 상태입니다."

        print("✅ 인덱스 업데이트 완료", file=sys.stderr)
        return [types.TextContent(type="text", text=response)]

    elif name == "pack_note_context":
        # 노트 컨텍스트 패키징
        note_title = arguments["note_title"]
        max_tokens = arguments.get("max_tokens", 100000)

        print(f"📦 '{note_title}' 컨텍스트 패키징 시작...", file=sys.stderr)

        try:
            # ContextPacker에 max_tokens 설정 적용
            context_packer.smart_packer.max_tokens = max_tokens

            # 노트 패키징
            packed_content = context_packer.pack_note(
                note_title=note_title,
                include_backlinks=arguments.get("include_backlinks", True),
                include_forward_links=arguments.get("include_forward_links", True),
                include_semantic_related=arguments.get("include_semantic_related", True),
                include_tag_related=False,
                max_backlinks=arguments.get("max_backlinks", 10),
                max_forward_links=arguments.get("max_forward_links", 10),
                max_semantic_related=arguments.get("max_semantic_related", 5),
            )

            print("✅ 컨텍스트 패키징 완료", file=sys.stderr)
            return [types.TextContent(type="text", text=packed_content)]

        except Exception as e:
            error_msg = f"❌ 패키징 실패: {str(e)}"
            print(error_msg, file=sys.stderr)
            return [types.TextContent(type="text", text=error_msg)]

    return [types.TextContent(type="text", text="도구 실행 완료")]

async def main():
    """메인 실행"""
    global vector_store, indexer, auto_update_service, context_packer

    print("🚀 Obsidian RAG MCP 서버 시작...", file=sys.stderr)
    print(f"📁 Vault 경로: {VAULT_PATH}", file=sys.stderr)

    # 3개 Store 초기화
    print("🔧 Store 초기화 중...", file=sys.stderr)
    vector_store = VectorStore()
    network_store = NetworkMetadataStore()
    repomix_store = RepomixIndexStore()

    # UnifiedIndexer 초기화 (3개 DB 통합 관리)
    indexer = UnifiedIndexer(vector_store, network_store, repomix_store)

    # 인덱스가 없을 때만 초기 인덱싱
    if not indexer.metadata.get('indexed_files'):
        print("📊 초기 인덱싱 중... (최초 실행시에만)", file=sys.stderr)
        indexer.update_index()
    else:
        print(f"✅ 기존 인덱스 로드 완료 ({len(indexer.metadata['indexed_files'])}개 파일)", file=sys.stderr)

    # ContextPacker 초기화
    print("📦 ContextPacker 초기화 중...", file=sys.stderr)
    context_packer = ContextPacker(vector_store, network_store, repomix_store, max_tokens=100000)

    # Auto-Update Service 시작
    print("🔄 Auto-Update Service 시작 중...", file=sys.stderr)
    auto_update_service = AutoUpdateService(indexer, debounce_seconds=5.0)
    auto_update_service.start()

    print("🎉 MCP 서버 준비 완료!", file=sys.stderr)

    try:
        # MCP 서버 시작
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name="obsidian-rag",
                    server_version="2.0.0",
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={}
                    )
                )
            )
    finally:
        # 서버 종료 시 Auto-Update Service도 중지
        if auto_update_service:
            print("⏹️ Auto-Update Service 중지 중...", file=sys.stderr)
            auto_update_service.stop()

if __name__ == "__main__":
    asyncio.run(main())
