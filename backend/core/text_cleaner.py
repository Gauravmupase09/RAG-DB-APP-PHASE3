import re, json
from pathlib import Path
from backend.utils.logger import logger
from backend.utils.config import PROCESSED_DIR


def clean_text(text: str) -> str:
    text = text.replace("-\n", "")
    text = re.sub(r'\n\s*\n+', '\n\n', text)
    text = re.sub(r' +', ' ', text)
    text = re.sub(r'[^\x00-\x7F]+', ' ', text)
    text = re.sub(r'([.!?])\1+', r'\1', text)
    return text.strip()


def clean_all_raw_files(session_id: str) -> list:
    session_dir = PROCESSED_DIR / session_id
    meta_file = session_dir / "file_index.json"

    if not meta_file.exists():
        raise FileNotFoundError("file_index.json missing")

    meta = json.loads(meta_file.read_text())
    cleaned_paths = []

    for entry in meta:
        folder = session_dir / entry["doc_folder"]
        raw_file = folder / entry["stored_raw_file"]

        logger.info(f"🧹 Cleaning → {raw_file.name}")

        text = raw_file.read_text(encoding="utf-8")
        cleaned_text = clean_text(text)

        clean_file_name = raw_file.name.replace("raw_", "clean_")
        clean_file = folder / clean_file_name

        clean_file.write_text(cleaned_text, encoding="utf-8")
        cleaned_paths.append(str(clean_file))

        entry["cleaned_file"] = clean_file_name

        logger.info(f"✅ Saved cleaned → {clean_file}")

    (session_dir / "file_index.json").write_text(json.dumps(meta, indent=2), encoding="utf-8")
    return cleaned_paths