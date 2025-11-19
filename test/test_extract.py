import sys, os, json
from pathlib import Path

# Add project root to PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.core.text_extractor import extract_all_files
from backend.utils.config import PROCESSED_DIR

# ⚠️ Change session ID to your test session folder
session_id = "9d343441-b56b-4e3b-a823-6e66bb775f0a"

print(f"🔥 Running text extractor test for session: {session_id}")

raw_files = extract_all_files(session_id)

print("\n✅ Extracted raw text files:")
for f in raw_files:
    print(" -", f)

meta_file = PROCESSED_DIR / session_id / "file_index.json"

print(f"\n📑 Checking metadata file: {meta_file}")

if meta_file.exists():
    meta_data = json.loads(meta_file.read_text(encoding="utf-8"))
    print("\n📂 File Index Metadata:")
    for entry in meta_data:
        print(entry)
else:
    print("❌ ERROR: file_index.json not found!")

print("\n🎯 Test completed.\n")