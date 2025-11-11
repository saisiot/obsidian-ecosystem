import chromadb
from chromadb.utils import embedding_functions
from typing import List, Dict, Optional
from config import CHROMA_PATH, EMBEDDING_MODEL, COLLECTION_NAME, CHUNK_SIZE


class VectorStore:
    """ChromaDB 벡터 스토어 관리"""

    def __init__(self):
        self.client = chromadb.PersistentClient(path=str(CHROMA_PATH))
        self.embedding_function = (
            embedding_functions.SentenceTransformerEmbeddingFunction(
                model_name=EMBEDDING_MODEL
            )
        )
        self.collection = self.get_or_create_collection()

    def get_or_create_collection(self):
        """컬렉션 생성 또는 가져오기"""
        try:
            return self.client.get_collection(
                name=COLLECTION_NAME, embedding_function=self.embedding_function
            )
        except Exception:
            return self.client.create_collection(
                name=COLLECTION_NAME,
                embedding_function=self.embedding_function,
                metadata={"hnsw:space": "cosine"},
            )

    def chunk_text(self, text: str) -> List[str]:
        """텍스트 청킹"""
        chunks = []
        lines = text.split("\n")
        current_chunk = []
        current_size = 0

        for line in lines:
            line_size = len(line)
            if current_size + line_size > CHUNK_SIZE and current_chunk:
                chunks.append("\n".join(current_chunk))
                current_chunk = [line]
                current_size = line_size
            else:
                current_chunk.append(line)
                current_size += line_size

        if current_chunk:
            chunks.append("\n".join(current_chunk))

        return chunks

    def add_document(self, doc: Dict):
        """문서 추가"""
        chunks = self.chunk_text(doc["content"])

        for i, chunk in enumerate(chunks):
            chunk_id = f"{doc['path']}_{i}"
            metadata = {
                "path": doc["path"],
                "title": doc["title"],
                "chunk_index": i,
                "para_folder": doc["para_folder"],
                "tags": ",".join(doc["tags"]),
                "wiki_links": ",".join(doc["wiki_links"]),
                "modified_time": doc["modified_time"],
            }

            self.collection.add(ids=[chunk_id], documents=[chunk], metadatas=[metadata])

    def update_document(self, doc: Dict):
        """문서 업데이트"""
        # 기존 청크 삭제
        self.delete_document(doc["path"])
        # 새로 추가
        self.add_document(doc)

    def delete_document(self, path: str):
        """문서 삭제"""
        results = self.collection.get(where={"path": path})
        if results["ids"]:
            self.collection.delete(ids=results["ids"])

    def search(
        self,
        query: str,
        top_k: int = 5,
        folder: Optional[str] = None,
        tags: Optional[List[str]] = None,
    ) -> List[Dict]:
        """시맨틱 검색"""
        where_clause = {}
        if folder:
            where_clause["para_folder"] = folder

        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where_clause if where_clause else None,
        )

        # 결과 포맷팅
        formatted_results = []
        for i in range(len(results["ids"][0])):
            formatted_results.append(
                {
                    "path": results["metadatas"][0][i]["path"],
                    "title": results["metadatas"][0][i]["title"],
                    "content": results["documents"][0][i],
                    "score": results["distances"][0][i],
                    "metadata": results["metadatas"][0][i],
                }
            )

        return formatted_results
