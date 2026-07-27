import logging
from pathlib import Path

import chromadb
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

CHROMA_PATH = Path(__file__).resolve().parent.parent.parent / "chroma_db"
COLLECTION_NAME = "meeting_notes"
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
NOTES_DIR = Path(__file__).resolve().parent.parent.parent / "data" / "meeting_notes"


class IngestService:
    """
    Indexes meeting note markdown files into ChromaDB for semantic search.
    """

    def __init__(self) -> None:
        self._model: SentenceTransformer | None = None

    def _get_model(self) -> SentenceTransformer:
        if self._model is None:
            logger.info(f"Loading embedding model: {EMBEDDING_MODEL}")
            self._model = SentenceTransformer(EMBEDDING_MODEL)
        return self._model

    def _embed(self, texts: list[str]) -> list[list[float]]:
        return self._get_model().encode(texts).tolist()

    def _chunk_file(self, content: str) -> list[str]:
        md_splitter = MarkdownHeaderTextSplitter(
            headers_to_split_on=[("#", "h1"), ("##", "h2")],
        )
        char_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)

        chunks: list[str] = []
        for split in md_splitter.split_text(content):
            text = split.page_content if hasattr(split, "page_content") else str(split)
            if len(text) > 500:
                chunks.extend(char_splitter.split_text(text))
            elif text.strip():
                chunks.append(text)

        return chunks

    def ingest(self) -> dict[str, int]:
        md_files = sorted(NOTES_DIR.glob("*.md"))
        logger.info(f"Found {len(md_files)} markdown files in {NOTES_DIR}")

        chroma_client = chromadb.PersistentClient(path=str(CHROMA_PATH))
        try:
            chroma_client.delete_collection(COLLECTION_NAME)
            logger.info(f"Removed existing collection: {COLLECTION_NAME}")
        except Exception:
            pass

        collection = chroma_client.create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": "cosine"},
        )

        ids: list[str] = []
        documents: list[str] = []
        metadatas: list[dict] = []

        for md_file in md_files:
            content = md_file.read_text(encoding="utf-8")
            client_name = md_file.stem
            file_chunks = self._chunk_file(content)
            logger.info(f"Chunked {md_file.name}: {len(file_chunks)} chunks")

            for chunk_id, chunk_text in enumerate(file_chunks):
                ids.append(f"{md_file.name}_{chunk_id}")
                documents.append(chunk_text)
                metadatas.append(
                    {
                        "client": client_name,
                        "filename": md_file.name,
                        "source": "meeting_notes",
                        "chunk_id": str(chunk_id),
                    }
                )

        if documents:
            embeddings = self._embed(documents)
            collection.add(
                ids=ids,
                documents=documents,
                embeddings=embeddings,
                metadatas=metadatas,
            )
            logger.info(f"Indexed {len(documents)} chunks into ChromaDB")

        return {
            "indexed_documents": len(md_files),
            "indexed_chunks": len(documents),
        }
