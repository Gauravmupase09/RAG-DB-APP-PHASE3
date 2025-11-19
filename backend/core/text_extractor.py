import pdfplumber
from docx import Document
from pathlib import Path
from datetime import datetime
import json
import re
import uuid

from backend.utils.config import PROCESSED_DIR, UPLOAD_DIR
from backend.utils.logger import logger


def clean_filename(name: str) -> str:
    return re.sub(r'[^a-zA-Z0-9_\-]', '_', name)


def extract_text_from_pdf(file_path: str) -> str:
    text = ""
    try:
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                words = page.extract_words()
                page_text = " ".join([w["text"] for w in words]) if words else (page.extract_text() or "")
                page_text = page_text.replace("-\n", "")
                page_text = " ".join(page_text.split())
                text += page_text + "\n\n"
        return text
    except Exception as e:
        logger.error(f"PDF extraction failed for {file_path}: {e}")
        raise


def extract_text_from_docx(file_path: str) -> str:
    text = ""
    try:
        doc = Document(file_path)
        for para in doc.paragraphs:
            text += para.text + "\n"
        return text
    except Exception as e:
        logger.error(f"DOCX extraction failed for {file_path}: {e}")
        raise


def extract_single_file(file_path: Path) -> str:
    ext = file_path.suffix.lower()
    if ext == ".pdf": return extract_text_from_pdf(file_path)
    if ext in [".docx", ".doc"]: return extract_text_from_docx(file_path)
    if ext == ".txt": return file_path.read_text(encoding="utf-8")
    raise ValueError(f"Unsupported file type: {ext}")


def extract_all_files(session_id: str) -> list:
    upload_dir = UPLOAD_DIR / session_id
    processed_dir = PROCESSED_DIR / session_id

    processed_dir.mkdir(parents=True, exist_ok=True)

    uploaded_files = list(upload_dir.iterdir())
    if not uploaded_files:
        logger.error(f"No uploaded files for session {session_id}")
        return []

    # ✅ Load upload metadata (if available)
    upload_meta_file = processed_dir / "upload_metadata.json"
    upload_meta = []
    if upload_meta_file.exists():
        upload_meta = json.loads(upload_meta_file.read_text(encoding="utf-8"))

    raw_paths = []
    meta = []

    for idx, file in enumerate(uploaded_files, start=1):
        safe_name = clean_filename(file.stem)
        doc_dir = processed_dir / safe_name
        doc_dir.mkdir(parents=True, exist_ok=True)

        logger.info(f"📄 Extracting: {file.name}")

        text = extract_single_file(file)
        raw_file_name = f"raw_{idx}_{safe_name}.txt"
        raw_path = doc_dir / raw_file_name

        raw_path.write_text(text, encoding="utf-8")
        raw_paths.append(str(raw_path))

        # ✅ Find upload time if available
        upload_time = None
        if upload_meta:
            entry = next((x for x in upload_meta if x["file_name"] == file.name), None)
            if entry:
                upload_time = entry["uploaded_at"]

        # ✅ Build metadata entry
        meta.append({
            "index": idx,
            "doc_id": str(uuid.uuid4()),
            "original_name": file.name,
            "stored_raw_file": raw_file_name,
            "doc_folder": safe_name,
            "file_type": file.suffix.lower(),
            "original_file_path": str(file),
            "uploaded_at": upload_time or datetime.now().isoformat(),
            "processed": False
        })

        logger.info(f"✅ Saved raw → {raw_path}")

    meta_file = processed_dir / "file_index.json"
    meta_file.write_text(json.dumps(meta, indent=2), encoding="utf-8")

    logger.info(f"📁 Saved file_index.json")
    return raw_paths