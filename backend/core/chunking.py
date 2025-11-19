from pathlib import Path
import json
from langchain_text_splitters import RecursiveCharacterTextSplitter
from backend.utils.config import PROCESSED_DIR, CHUNK_SIZE, CHUNK_OVERLAP
from backend.utils.logger import logger


def chunk_text(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=["\n\n", "\n", " ", ""]
    )
    return splitter.split_text(text)


def chunk_session_documents(session_id: str):
    session_dir = PROCESSED_DIR / session_id
    meta_file = session_dir / "file_index.json"

    if not meta_file.exists():
        raise FileNotFoundError("file_index.json missing")

    meta = json.loads(meta_file.read_text())
    all_chunks = []

    for entry in meta:
        folder = session_dir / entry["doc_folder"]
        cleaned_file = folder / entry["cleaned_file"]

        logger.info(f"✂ Chunking → {cleaned_file.name}")

        text = cleaned_file.read_text(encoding="utf-8")
        chunks = chunk_text(text)

        chunk_root = folder / f"chunks_{entry['doc_folder']}"
        chunk_root.mkdir(exist_ok=True)

        for i, ch in enumerate(chunks, start=1):
            cdir = chunk_root / f"chunk_{i}"
            cdir.mkdir(exist_ok=True)

            (cdir / "text.txt").write_text(ch, encoding="utf-8")

            meta_json = {
                "chunk_id": f"{session_id}_{entry['doc_folder']}_chunk_{i}",
                "session_id": session_id,
                "doc_id": entry.get("doc_id"),
                "source_doc_folder": entry["doc_folder"],
                "original_file_name": entry["original_name"],
                "original_file_path": entry["original_file_path"],
                "chunk_index": i,
                "total_chunks_in_file": len(chunks),
                "file_order": entry["index"],
                "doc_type": entry["file_type"]
            }

            (cdir / "meta.json").write_text(json.dumps(meta_json, indent=2))
            all_chunks.append(meta_json)

    logger.info(f"✅ Total chunks = {len(all_chunks)}")
    return all_chunks