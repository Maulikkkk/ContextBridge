import logging
import traceback

from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

from embeddings import embed_texts, get_embedding_model_error, is_embedding_model_ready, recreate_collection
from paths import NOTES_DIR, ensure_runtime_dirs

logger = logging.getLogger(__name__)


class IngestService:
    """
    Indexes meeting note markdown files into ChromaDB for semantic search.
    """

    def _validate_data_paths(self) -> None:
        if not NOTES_DIR.exists():
            raise FileNotFoundError(f"Meeting notes directory not found: {NOTES_DIR}")
        md_files = list(NOTES_DIR.glob("*.md"))
        if not md_files:
            raise FileNotFoundError(f"No markdown files found in {NOTES_DIR}")

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
        if not is_embedding_model_ready():
            error = get_embedding_model_error() or "Embedding model was not loaded at startup"
            raise RuntimeError(f"Cannot ingest: {error}")

        ensure_runtime_dirs()
        self._validate_data_paths()

        md_files = sorted(NOTES_DIR.glob("*.md"))
        logger.info("Found %d markdown files in %s", len(md_files), NOTES_DIR)

        try:
            collection = recreate_collection()
        except Exception as exc:
            logger.error("ChromaDB collection setup failed: %s\n%s", exc, traceback.format_exc())
            raise RuntimeError(f"ChromaDB collection setup failed: {exc}") from exc

        ids: list[str] = []
        documents: list[str] = []
        metadatas: list[dict] = []

        for md_file in md_files:
            try:
                content = md_file.read_text(encoding="utf-8")
            except OSError as exc:
                raise PermissionError(f"Cannot read {md_file}: {exc}") from exc

            client_name = md_file.stem
            file_chunks = self._chunk_file(content)
            logger.info("Chunked %s: %d chunks", md_file.name, len(file_chunks))

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
            try:
                embeddings = embed_texts(documents)
            except Exception as exc:
                logger.error("Embedding generation failed: %s\n%s", exc, traceback.format_exc())
                raise RuntimeError(f"Failed to generate embeddings: {exc}") from exc

            try:
                collection.add(
                    ids=ids,
                    documents=documents,
                    embeddings=embeddings,
                    metadatas=metadatas,
                )
            except Exception as exc:
                logger.error("ChromaDB add failed: %s\n%s", exc, traceback.format_exc())
                raise RuntimeError(f"ChromaDB indexing failed: {exc}") from exc
            logger.info("Indexed %d chunks into ChromaDB", len(documents))

        return {
            "indexed_documents": len(md_files),
            "indexed_chunks": len(documents),
        }
