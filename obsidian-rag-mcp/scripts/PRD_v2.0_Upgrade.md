# PRD: Obsidian RAG MCP v2.0 - Upgrade Specification

## 📋 Document Info
- **Project**: Obsidian RAG MCP Server v2.0
- **Version**: 2.0.0
- **Date**: 2024-10-30
- **Type**: Upgrade Specification
- **Current Version**: 1.0.0

---

## 🎯 Executive Summary

### Objective
Upgrade Obsidian RAG MCP server with three critical enhancements:
1. **Unified Indexing System**: Synchronize ChromaDB + Network Metadata + Repomix index
2. **Auto-Update Background Service**: Periodic index updates (every 5 minutes)
3. **Repomix Packing Engine**: Bundle notes into single context for comprehensive LLM analysis

### Strategic Value

| Metric | Current (v1.0) | Target (v2.0) | Impact |
|--------|---------------|---------------|--------|
| Update Workflow | Manual `update_index` call | Auto-sync every 5min | 95% reduction in friction |
| Context Preparation | 5-10 min manual work | < 1 min automated | 90% time savings |
| Data Consistency | ChromaDB only | 3 DBs synchronized | Zero drift |
| Large Project Analysis | Inefficient multi-get | Single packed context | 10x faster |

---

## 🏗️ System Architecture

### Current Architecture (v1.0)

```
Obsidian Vault
    ↓
IncrementalIndexer
    ↓
ChromaDB (vector search only)
    ↓
MCP Tools (7 tools)
```

**Limitations:**
- ❌ Manual update trigger required
- ❌ Network metadata not indexed
- ❌ No whole-project context capability
- ❌ Single database (ChromaDB)

### Target Architecture (v2.0)

```
Obsidian Vault
    ↓
┌─────────────────────────────────────────────┐
│  Background Auto-Update Service (5min)     │
│         ↓                                   │
│  Unified Indexer (Transactional)           │
│         ↓                                   │
│  ┌──────────────┬──────────────┬─────────┐ │
│  │  ChromaDB    │   Network    │ Repomix │ │
│  │  (vectors)   │  (metadata)  │ (index) │ │
│  └──────────────┴──────────────┴─────────┘ │
└─────────────────────────────────────────────┘
    ↓
MCP Tools (12 tools)
  - 7 existing tools
  - 5 new Repomix packing tools
```

---

## 📦 Feature Specifications

## Feature 1: Unified Indexing System

### 1.1 Network Metadata Database

**Purpose**: Extract and index Obsidian-specific metadata (backlinks, tags, relationships)

**Data Structure**: `data/network_metadata.json`

```json
{
  "version": "2.0.0",
  "last_update": "2024-10-30T14:05:00",
  "files": {
    "/path/to/note.md": {
      "title": "AI Strategy 2025",
      "para_folder": "00 Notes",
      "backlinks": ["[[Project A]]", "[[Roadmap 2025]]"],
      "forward_links": ["[[Tech Stack]]", "[[API Docs]]"],
      "tags": ["#ai", "#strategy"],
      "yaml_frontmatter": {
        "status": "in-progress",
        "priority": "high"
      }
    }
  },
  "stats": {
    "total_files": 1234,
    "total_backlinks": 3456,
    "orphaned_notes": 12
  }
}
```

**Implementation**: New `NetworkMetadataStore` class in `src/network_store.py`

**Key Methods**:
- `extract_links(content: str) -> dict`: Parse `[[wiki_links]]`
- `extract_tags(content: str) -> list`: Parse `#tags`
- `update_metadata(doc: dict)`: Store metadata
- `get_backlinks(note_title: str) -> list`: Query reverse links
- `get_network_stats() -> dict`: Aggregate statistics

---

### 1.2 Repomix Index Database

**Purpose**: Store file-level metadata for efficient packing operations

**Data Structure**: `data/repomix_index.json`

```json
{
  "version": "1.0.0",
  "last_update": "2024-10-30T14:05:00",
  "files": {
    "/path/to/note.md": {
      "title": "AI Strategy 2025",
      "para_folder": "00 Notes",
      "relative_path": "00 Notes/Work/AI Strategy 2025.md",
      "timestamps": {
        "created": "2024-10-24T10:30:00",
        "modified": "2024-10-29T14:15:00",
        "indexed": "2024-10-30T14:05:00"
      },
      "size": {
        "bytes": 2048,
        "words": 1250,
        "characters": 8450,
        "lines": 156,
        "estimated_tokens": 1650
      },
      "metadata": {
        "tags": ["#ai", "#strategy"],
        "backlinks": ["Project A", "Roadmap 2025"],
        "forward_links": ["Tech Stack", "API Docs"],
        "backlink_count": 2,
        "forward_link_count": 2
      }
    }
  },
  "stats": {
    "total_files": 1234,
    "total_words": 450000,
    "total_tokens_estimated": 600000,
    "by_folder": {
      "00 Notes": {"files": 456, "words": 180000},
      "01 Reference": {"files": 234, "words": 120000},
      "02 Journals": {"files": 365, "words": 100000},
      "04 Outputs": {"files": 179, "words": 50000}
    },
    "top_tags": {
      "#ai": 45,
      "#strategy": 32,
      "#jpdc": 28
    }
  }
}
```

**Implementation**: New `RepomixIndexStore` class in `src/repomix_store.py`

**Key Methods**:
- `calculate_stats(content: str) -> dict`: Word/character/token counts
- `update_index(doc: dict)`: Store file metadata
- `query_by_timeframe(days: int) -> list`: Filter by mtime
- `query_by_tag(tag: str) -> list`: Filter by tag
- `query_by_backlinks(note_title: str, depth: int) -> list`: Graph traversal

---

### 1.3 Transactional Unified Indexer

**Purpose**: Atomically update all 3 databases or rollback on failure

**Implementation**: Extend `IncrementalIndexer` class in `src/indexer.py`

**New Architecture**:

```python
class UnifiedIndexer(IncrementalIndexer):
    def __init__(self, vector_store, network_store, repomix_store):
        # Initialize all 3 stores
        
    def update_index(self):
        """Transactional update"""
        changes = self.check_updates()
        
        # Phase 1: Prepare updates
        updates = {
            'chroma': [],
            'network': [],
            'repomix': []
        }
        
        for file in changes['new'] + changes['modified']:
            doc = self.parser.parse_file(file)
            updates['chroma'].append(doc)
            updates['network'].append(self.extract_network_metadata(doc))
            updates['repomix'].append(self.extract_repomix_metadata(doc))
        
        # Phase 2: Apply updates (transactional)
        try:
            self.vector_store.batch_update(updates['chroma'])
            self.network_store.batch_update(updates['network'])
            self.repomix_store.batch_update(updates['repomix'])
            self.save_metadata()  # Commit
        except Exception as e:
            self.rollback()  # Rollback on failure
            raise
```

**Rollback Strategy**:
- Store backup snapshots before updates
- On failure: restore from snapshots
- Log transaction failures for debugging

---

## Feature 2: Auto-Update Background Service

### 2.1 Background Scheduler

**Purpose**: Automatically detect and index vault changes every 5 minutes

**Implementation**: Add to `src/mcp_server.py`

```python
import asyncio
from datetime import datetime, timedelta

class AutoUpdateService:
    def __init__(self, indexer, interval=300):
        self.indexer = indexer
        self.interval = interval
        self.running = False
        self.lock = asyncio.Lock()
        self.stats = {
            'total_runs': 0,
            'successful_runs': 0,
            'failed_runs': 0,
            'last_run': None,
            'next_run': None
        }
    
    async def start(self):
        """Start background update task"""
        self.running = True
        asyncio.create_task(self._update_loop())
    
    async def _update_loop(self):
        """Main update loop"""
        while self.running:
            await asyncio.sleep(self.interval)
            
            async with self.lock:  # Prevent concurrent updates
                try:
                    self.stats['total_runs'] += 1
                    self.stats['last_run'] = datetime.now().isoformat()
                    
                    updates = self.indexer.check_updates()
                    total_changes = sum(len(v) for v in updates.values())
                    
                    if total_changes > 0:
                        print(f"[{datetime.now()}] Auto-update: {total_changes} changes detected", 
                              file=sys.stderr)
                        self.indexer.update_index()
                        self.stats['successful_runs'] += 1
                    else:
                        # Quiet mode: no log if no changes
                        pass
                    
                except Exception as e:
                    self.stats['failed_runs'] += 1
                    print(f"[{datetime.now()}] Auto-update failed: {e}", file=sys.stderr)
            
            self.stats['next_run'] = (datetime.now() + timedelta(seconds=self.interval)).isoformat()
    
    async def stop(self):
        """Graceful shutdown"""
        self.running = False
```

**Integration**:

```python
async def main():
    # ... existing initialization ...
    
    # Start auto-update service
    auto_update = AutoUpdateService(indexer, interval=AUTO_UPDATE_INTERVAL)
    await auto_update.start()
    
    # ... MCP server run ...
```

---

### 2.2 Configuration

**Add to `src/config.py`**:

```python
# Auto-update settings
AUTO_UPDATE_ENABLED = True
AUTO_UPDATE_INTERVAL = 300  # seconds (5 minutes)
AUTO_UPDATE_QUIET = True    # No log if no changes
AUTO_UPDATE_MAX_RETRIES = 3
```

**Validation**:
- `INTERVAL` must be between 60 and 3600 seconds
- Default to 300 if invalid value provided

---

### 2.3 Concurrency Control

**Lock Mechanism**:
- Single `asyncio.Lock` prevents:
  - Auto-update vs manual `update_index` collision
  - Multiple auto-updates running simultaneously
  
**Search During Update**:
- Reads are not blocked (ChromaDB handles this)
- Only writes are serialized

---

## Feature 3: Repomix Packing Engine

### 3.1 Note Selection Engine

**Purpose**: Filter and select notes based on various criteria

**Implementation**: New `NoteSelector` class in `src/repomix_selector.py`

```python
class NoteSelector:
    def __init__(self, repomix_store, network_store):
        self.repomix_store = repomix_store
        self.network_store = network_store
    
    def select_by_timeframe(self, days: int, folder: str = None, max_notes: int = 50) -> list:
        """Select notes modified in last N days"""
        cutoff = datetime.now() - timedelta(days=days)
        notes = [
            note for note in self.repomix_store.files.values()
            if datetime.fromisoformat(note['timestamps']['modified']) > cutoff
        ]
        
        if folder:
            notes = [n for n in notes if n['para_folder'] == folder]
        
        # Sort by modified time (newest first)
        notes.sort(key=lambda x: x['timestamps']['modified'], reverse=True)
        return notes[:max_notes]
    
    def select_by_paths(self, note_paths: list) -> list:
        """Select specific notes by paths"""
        return [
            self.repomix_store.files[str(path)]
            for path in note_paths
            if str(path) in self.repomix_store.files
        ]
    
    def select_by_tag(self, tag: str, max_notes: int = 50) -> list:
        """Select notes with specific tag"""
        notes = [
            note for note in self.repomix_store.files.values()
            if tag in note['metadata']['tags']
        ]
        return notes[:max_notes]
    
    def select_by_backlinks(self, note_title: str, depth: int = 1, max_notes: int = 50) -> list:
        """Select notes linked to target note (up to N hops)"""
        visited = set()
        current_level = {note_title}
        
        for _ in range(depth):
            next_level = set()
            for title in current_level:
                backlinks = self.network_store.get_backlinks(title)
                forward_links = self.network_store.get_forward_links(title)
                next_level.update(backlinks + forward_links)
            visited.update(current_level)
            current_level = next_level - visited
        
        notes = [
            self.repomix_store.get_by_title(title)
            for title in visited
            if title != note_title  # Exclude center note
        ]
        return notes[:max_notes]
```

---

### 3.2 Packing Formatter

**Purpose**: Format selected notes into structured text

**Implementation**: New `PackFormatter` class in `src/repomix_formatter.py`

```python
class PackFormatter:
    def format_pack(self, notes: list, source_description: str) -> str:
        """Generate formatted pack"""
        output = []
        
        # Header
        output.append(self._format_header(notes, source_description))
        
        # Notes
        for i, note in enumerate(notes, 1):
            output.append(self._format_note(note, i, len(notes)))
        
        # Footer
        output.append(self._format_footer(notes))
        
        return '\n'.join(output)
    
    def _format_header(self, notes: list, source: str) -> str:
        total_words = sum(n['size']['words'] for n in notes)
        total_tokens = sum(n['size']['estimated_tokens'] for n in notes)
        
        return f"""{'='*80}
OBSIDIAN CONTEXT PACK
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Source: {source}
Total Notes: {len(notes)}
Total Words: {total_words:,}
Estimated Tokens: ~{total_tokens:,}
{'='*80}
"""
    
    def _format_note(self, note: dict, index: int, total: int) -> str:
        path = note['relative_path']
        title = note['title']
        folder = note['para_folder']
        tags = ', '.join(note['metadata']['tags'])
        backlinks = note['metadata']['backlinks']
        forward_links = note['metadata']['forward_links']
        
        # Read actual content
        full_path = VAULT_PATH / path
        content = full_path.read_text(encoding='utf-8')
        
        return f"""{'-'*80}
[{index}/{total}] {title}
{'-'*80}
Path: {path}
Folder: {folder}
Tags: {tags}
Created: {note['timestamps']['created']}
Modified: {note['timestamps']['modified']}
Word Count: {note['size']['words']}

Backlinks ({len(backlinks)}):
{self._format_links(backlinks, '←')}

Forward Links ({len(forward_links)}):
{self._format_links(forward_links, '→')}

{'─'*80}

{content}

"""
    
    def _format_links(self, links: list, arrow: str) -> str:
        if not links:
            return "  (none)"
        return '\n'.join(f"  {arrow} [[{link}]]" for link in links)
    
    def _format_footer(self, notes: list) -> str:
        total_words = sum(n['size']['words'] for n in notes)
        total_chars = sum(n['size']['characters'] for n in notes)
        total_tokens = sum(n['size']['estimated_tokens'] for n in notes)
        
        # Folder distribution
        folders = {}
        for note in notes:
            folder = note['para_folder']
            folders[folder] = folders.get(folder, 0) + 1
        
        # Tag distribution
        tags = {}
        for note in notes:
            for tag in note['metadata']['tags']:
                tags[tag] = tags.get(tag, 0) + 1
        top_tags = sorted(tags.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return f"""{'='*80}
SUMMARY
Total Notes: {len(notes)}
Total Words: {total_words:,}
Total Characters: {total_chars:,}
Estimated Tokens: ~{total_tokens:,} (GPT-4 basis)

Notes by Folder:
{chr(10).join(f'  - {k}: {v}' for k, v in sorted(folders.items()))}

Top Tags:
{chr(10).join(f'  - {tag}: {count}' for tag, count in top_tags)}
{'='*80}
"""
```

---

### 3.3 Size Limit Manager

**Purpose**: Prevent oversized packs that exceed LLM context limits

**Limits**:
| Constraint | Limit | Action on Exceed |
|------------|-------|------------------|
| Max notes | 50 | Error + suggest filtering |
| Max characters | 200,000 | Warning + auto-trim oldest |
| Max estimated tokens | 50,000 | Warning + continue |
| Single note size | 20,000 chars | Truncate or summarize |

**Implementation**:

```python
class SizeLimitManager:
    MAX_NOTES = 50
    MAX_CHARS = 200_000
    MAX_TOKENS = 50_000
    MAX_NOTE_CHARS = 20_000
    
    def validate_pack(self, notes: list) -> dict:
        """Validate pack size"""
        if len(notes) > self.MAX_NOTES:
            raise ValueError(f"Too many notes ({len(notes)}). Max: {self.MAX_NOTES}")
        
        total_chars = sum(n['size']['characters'] for n in notes)
        total_tokens = sum(n['size']['estimated_tokens'] for n in notes)
        
        warnings = []
        
        if total_chars > self.MAX_CHARS:
            warnings.append(f"Pack size ({total_chars:,} chars) exceeds recommended limit")
        
        if total_tokens > self.MAX_TOKENS:
            warnings.append(f"Estimated tokens ({total_tokens:,}) may exceed LLM context limit")
        
        return {
            'valid': len(notes) <= self.MAX_NOTES,
            'warnings': warnings,
            'total_chars': total_chars,
            'total_tokens': total_tokens
        }
```

---

### 3.4 MCP Tools

**Add 5 new tools to `src/mcp_server.py`**:

#### Tool 1: pack_notes_by_timeframe

```python
types.Tool(
    name="pack_notes_by_timeframe",
    description="최근 N일 내 수정된 노트를 하나의 컨텍스트로 패킹",
    inputSchema={
        "type": "object",
        "properties": {
            "days": {
                "type": "integer",
                "description": "최근 며칠 (예: 7, 30, 90)"
            },
            "folder": {
                "type": "string",
                "description": "PARA 폴더 필터 (선택)"
            },
            "max_notes": {
                "type": "integer",
                "description": "최대 노트 개수",
                "default": 50
            },
            "include_metadata": {
                "type": "boolean",
                "description": "메타데이터 포함 여부",
                "default": True
            }
        },
        "required": ["days"]
    }
)
```

#### Tool 2: pack_notes_by_paths

```python
types.Tool(
    name="pack_notes_by_paths",
    description="지정된 경로의 노트들을 패킹",
    inputSchema={
        "type": "object",
        "properties": {
            "note_paths": {
                "type": "array",
                "items": {"type": "string"},
                "description": "노트 경로 배열"
            },
            "include_metadata": {
                "type": "boolean",
                "description": "메타데이터 포함 여부",
                "default": True
            }
        },
        "required": ["note_paths"]
    }
)
```

#### Tool 3: pack_search_results

```python
types.Tool(
    name="pack_search_results",
    description="검색 결과를 자동으로 패킹 (search + pack 통합)",
    inputSchema={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "검색 쿼리"
            },
            "top_k": {
                "type": "integer",
                "description": "결과 개수",
                "default": 10
            },
            "folder": {
                "type": "string",
                "description": "PARA 폴더 필터 (선택)"
            }
        },
        "required": ["query"]
    }
)
```

#### Tool 4: pack_by_tag

```python
types.Tool(
    name="pack_by_tag",
    description="특정 태그의 모든 노트를 패킹",
    inputSchema={
        "type": "object",
        "properties": {
            "tag": {
                "type": "string",
                "description": "태그명 (# 없이, 예: 'ai')"
            },
            "max_notes": {
                "type": "integer",
                "description": "최대 노트 개수",
                "default": 50
            }
        },
        "required": ["tag"]
    }
)
```

#### Tool 5: pack_by_backlinks

```python
types.Tool(
    name="pack_by_backlinks",
    description="특정 노트와 연결된 모든 노트를 패킹 (네트워크 기반)",
    inputSchema={
        "type": "object",
        "properties": {
            "note_title": {
                "type": "string",
                "description": "중심 노트 제목"
            },
            "depth": {
                "type": "integer",
                "description": "링크 깊이 (1=직접 연결만, 2=2단계 링크)",
                "default": 1
            },
            "max_notes": {
                "type": "integer",
                "description": "최대 노트 개수",
                "default": 50
            }
        },
        "required": ["note_title"]
    }
)
```

---

## 🗺️ Implementation Roadmap

### Phase 1: Foundation (Days 1-5)

**Week 1: Core Infrastructure**

| Day | Tasks | Deliverables |
|-----|-------|--------------|
| 1 | Network Metadata Store | `src/network_store.py` |
| 2 | Repomix Index Store | `src/repomix_store.py` |
| 3 | Unified Indexer | Extended `src/indexer.py` |
| 4 | Transaction & Rollback | Backup/restore logic |
| 5 | Integration Testing | Unit tests for all 3 DBs |

**Success Criteria**:
- ✅ All 3 DBs update atomically
- ✅ Rollback works on any failure
- ✅ Metadata is consistent across DBs

---

### Phase 2: Automation (Days 6-8)

**Week 2: Auto-Update Service**

| Day | Tasks | Deliverables |
|-----|-------|--------------|
| 6 | Background Scheduler | `AutoUpdateService` class |
| 7 | Concurrency Control | Lock mechanism + testing |
| 8 | Configuration & Logging | Config validation + stderr logs |

**Success Criteria**:
- ✅ Auto-update runs every 5 minutes
- ✅ No duplicate updates (lock works)
- ✅ Graceful shutdown on server stop

---

### Phase 3: Repomix Engine (Days 9-13)

**Week 2-3: Packing System**

| Day | Tasks | Deliverables |
|-----|-------|--------------|
| 9 | Note Selector Engine | `src/repomix_selector.py` |
| 10 | Pack Formatter | `src/repomix_formatter.py` |
| 11 | Size Limit Manager | Validation + auto-trim |
| 12 | MCP Tools (5 tools) | Tool handlers in `mcp_server.py` |
| 13 | Integration Testing | E2E packing scenarios |

**Success Criteria**:
- ✅ All 5 packing tools work
- ✅ Pack output is well-formatted
- ✅ Size limits enforced

---

### Phase 4: Testing & Optimization (Days 14-17)

**Week 3: Quality Assurance**

| Day | Tasks | Deliverables |
|-----|-------|--------------|
| 14 | Unit Tests | Test coverage > 80% |
| 15 | Performance Tests | <10s for 100 files update |
| 16 | Load Tests | 1000+ notes, memory < 600MB |
| 17 | Bug Fixes | Address all critical issues |

**Success Criteria**:
- ✅ All tests pass
- ✅ Performance targets met
- ✅ No memory leaks

---

### Phase 5: Documentation & Deployment (Days 18-20)

**Week 3: Finalization**

| Day | Tasks | Deliverables |
|-----|-------|--------------|
| 18 | README Update | New features documented |
| 19 | Migration Script | `scripts/migrate_v1_to_v2.py` |
| 20 | Release | Version 2.0.0 tagged |

**Success Criteria**:
- ✅ Documentation complete
- ✅ Migration script tested
- ✅ v2.0.0 released

---

## 📊 Success Metrics

### Functional Requirements

| Requirement | Criteria | Status |
|-------------|----------|--------|
| Unified Indexing | 3 DBs always synchronized | ☐ |
| Auto-Update | Runs every 5 min without manual trigger | ☐ |
| Repomix Packing | 5 tools work correctly | ☐ |
| Data Consistency | Zero drift between DBs | ☐ |

### Performance Requirements

| Metric | Target | Current |
|--------|--------|---------|
| 100-file update time | < 10 seconds | TBD |
| 50-note packing time | < 5 seconds | TBD |
| Memory usage | < 600 MB | TBD |
| Server startup time | < 5 seconds | ~3s ✅ |

### User Experience

| Before (v1.0) | After (v2.0) |
|---------------|--------------|
| Manual `update_index` every time | Auto-sync every 5 min |
| 4-hour avg delay for new notes | < 5 min delay |
| 10 min to prepare project context | < 1 min automated |
| ChromaDB-only search | 3-DB unified search + packing |

---

## 🚨 Risk Assessment

### Technical Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Transaction rollback fails | High | Low | Extensive testing + backup snapshots |
| Auto-update causes race condition | Medium | Medium | `asyncio.Lock` + concurrent testing |
| Large pack exceeds memory | High | Low | Size validation + streaming |
| Background task crashes server | High | Low | Try/except + error logging |

### Operational Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| User disables auto-update | Low | Low | Config flag `AUTO_UPDATE_ENABLED` |
| Pack size too large for LLM | Medium | Medium | Size warnings + auto-filtering |
| Migration from v1.0 fails | High | Medium | Migration script + rollback plan |

---

## 🔄 Migration Plan

### Backward Compatibility

**v1.0 → v2.0 Migration**:

1. **Metadata Upgrade**:
   - Preserve existing `index_metadata.json`
   - Add new fields: `databases`, `auto_update`
   - Create `network_metadata.json` and `repomix_index.json`

2. **Initial Population**:
   - Run full re-index on first v2.0 startup
   - Populate all 3 DBs from existing vault
   - Preserve ChromaDB collection (no data loss)

3. **Rollback Plan**:
   - Keep v1.0 codebase in `backup/` folder
   - Metadata is backward-compatible (v2.0 adds fields, doesn't remove)
   - Can revert to v1.0 if issues occur

**Migration Script**: `scripts/migrate_v1_to_v2.py`

```python
def migrate():
    """Migrate v1.0 metadata to v2.0"""
    # 1. Backup existing metadata
    shutil.copy(METADATA_FILE, f"{METADATA_FILE}.v1.backup")
    
    # 2. Upgrade metadata schema
    metadata = load_metadata()
    metadata['version'] = '2.0.0'
    metadata['databases'] = {
        'chromadb': {'last_update': metadata['last_update']},
        'network': {'last_update': None},
        'repomix': {'last_update': None}
    }
    metadata['auto_update'] = {
        'enabled': True,
        'interval': 300,
        'last_run': None
    }
    save_metadata(metadata)
    
    # 3. Initialize new stores
    network_store = NetworkMetadataStore()
    repomix_store = RepomixIndexStore()
    
    # 4. Full re-index to populate new stores
    indexer = UnifiedIndexer(vector_store, network_store, repomix_store)
    indexer.full_reindex()
    
    print("✅ Migration complete!")
```

---

## 📚 Appendix

### A. File Structure (v2.0)

```
obsidian-rag-mcp/
├── src/
│   ├── config.py                  # [UPDATED] Add auto-update configs
│   ├── obsidian_parser.py         # [NO CHANGE]
│   ├── vector_store.py            # [NO CHANGE]
│   ├── indexer.py                 # [UPDATED] → UnifiedIndexer
│   ├── network_store.py           # [NEW] Network metadata DB
│   ├── repomix_store.py           # [NEW] Repomix index DB
│   ├── repomix_selector.py        # [NEW] Note selection engine
│   ├── repomix_formatter.py       # [NEW] Pack formatting
│   └── mcp_server.py              # [UPDATED] +5 tools, auto-update
├── data/
│   ├── chroma_db/                 # [NO CHANGE] ChromaDB storage
│   ├── index_metadata.json        # [UPDATED] v2.0 schema
│   ├── network_metadata.json      # [NEW]
│   └── repomix_index.json         # [NEW]
├── scripts/
│   └── migrate_v1_to_v2.py        # [NEW] Migration script
├── tests/                         # [NEW]
│   ├── test_unified_indexer.py
│   ├── test_auto_update.py
│   └── test_repomix_packing.py
├── requirements.txt               # [UPDATED] Add new dependencies
├── mcp.json                       # [NO CHANGE]
└── README.md                      # [UPDATED] Document new features
```

---

### B. Dependencies

**New dependencies to add to `requirements.txt`**:

```
tiktoken>=0.5.0  # For token estimation (Repomix)
```

**Existing dependencies**:
```
chromadb>=0.4.0
sentence-transformers>=2.2.0
mcp>=0.1.0
python-frontmatter>=1.0.0
pyyaml>=6.0
```

---

### C. Glossary

| Term | Definition |
|------|------------|
| **Unified Indexing** | Atomic update of 3 DBs (ChromaDB + Network + Repomix) |
| **Network Metadata** | Obsidian-specific data (backlinks, tags, relationships) |
| **Repomix Index** | File-level metadata for packing (size, stats, links) |
| **Packing** | Bundling multiple notes into single formatted text |
| **PARA Folders** | Projects, Areas, Resources, Archives (Obsidian organization) |
| **Auto-Update** | Background service that syncs vault changes every 5 min |

---

### D. Change Log

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2024-10-13 | Initial release (ChromaDB only) |
| 2.0.0 | 2024-10-30 | Unified indexing + Auto-update + Repomix packing |

---

## ✅ Approval Checklist

**Before implementation:**
- [ ] PRD reviewed by stakeholder (타래)
- [ ] Architecture approved
- [ ] Timeline feasible (20 days)
- [ ] Resources allocated

**Before deployment:**
- [ ] All tests pass (>80% coverage)
- [ ] Performance benchmarks met
- [ ] Migration script tested
- [ ] Documentation complete
- [ ] Rollback plan validated

---

**Document Status**: ✅ Ready for Implementation

**Next Steps**: 
1. Review and approve this PRD
2. Create GitHub issues for each phase
3. Start Phase 1 (Foundation)

---

*End of PRD v2.0*
