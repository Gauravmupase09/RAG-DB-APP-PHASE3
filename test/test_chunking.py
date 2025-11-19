# import sys, os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# from backend.core.chunking import chunk_session_documents

# session_id = "28735376-65a1-4808-82a6-556e58df9f06"

# chunks = chunk_session_documents(session_id)

# print(f"Chunks created: {len(chunks)}")
# print(chunks[0])

# import os, sys, json
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# from backend.core.chunking import chunk_session_documents
# from backend.utils.config import PROCESSED_DIR

# session_id = "28735376-65a1-4808-82a6-556e58df9f06"

# print(f"🔥 Running multi-file chunk test for session: {session_id}\n")

# chunks = chunk_session_documents(session_id)

# print(f"\n✅ Total chunks generated: {len(chunks)}")

# # Show first 2 metadata for sanity
# print("\n📌 Sample chunk metadata:")
# print(json.dumps(chunks[:2], indent=2))

# # Show folder structure
# chunks_root = PROCESSED_DIR / session_id
# print("\n📂 Directory tree:")
# for root, dirs, files in os.walk(chunks_root):
#     level = root.replace(str(chunks_root), '').count(os.sep)
#     indent = ' ' * 2 * level
#     print(f"{indent}{os.path.basename(root)}/")
#     subindent = ' ' * 2 * (level + 1)
#     for f in files:
#         print(f"{subindent}{f}")


# import os, sys, json
# from pathlib import Path

# # Add root to Python path
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# from backend.core.chunking import chunk_session_documents
# from backend.utils.config import PROCESSED_DIR

# # Change per test
# session_id = "28735376-65a1-4808-82a6-556e58df9f06"

# print(f"🔥 Running multi-file chunk test for session: {session_id}\n")

# chunks = chunk_session_documents(session_id)

# print(f"\n✅ Total chunks generated: {len(chunks)}")

# # Print first 2 for sanity check
# print("\n📌 Sample chunk metadata:")
# print(json.dumps(chunks[:2], indent=2))

# # Verify chunk folders exist
# session_dir = PROCESSED_DIR / session_id
# chunk_dirs = [d for d in session_dir.glob("chunks_*") if d.is_dir()]

# print(f"\n📁 Files chunked: {len(chunk_dirs)}")
# for d in chunk_dirs:
#     print(f" - {d.name}")

# # Display directory tree under session folder
# print("\n📂 Directory tree:")
# for root, dirs, files in os.walk(session_dir):
#     # only show chunk-related folders
#     if "chunks_" not in root and not any("chunks_" in d for d in dirs):
#         continue

#     level = root.replace(str(session_dir), "").count(os.sep)
#     indent = " " * 2 * level
#     print(f"{indent}{os.path.basename(root)}/")

#     subindent = " " * 2 * (level + 1)
#     for f in files:
#         print(f"{subindent}{f}")

# # Validate 1 folder has expected files
# sample_folder = None
# for d in chunk_dirs:
#     chunk_sub = list(d.glob("chunk_1"))
#     if chunk_sub:
#         sample_folder = chunk_sub[0]
#         break

# if sample_folder:
#     print(f"\n🔍 Checking sample chunk at: {sample_folder}")
#     expected = {"text.txt", "meta.json"}
#     present = {f.name for f in sample_folder.iterdir() if f.is_file()}
#     missing = expected - present

#     if missing:
#         print(f"❌ Missing files inside first chunk: {missing}")
#     else:
#         print("✅ meta.json and text.txt found in sample chunk")

# print("\n🎯 Chunk test completed\n")


# import os, sys, json
# from pathlib import Path

# # Add project root
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# from backend.core.chunking import chunk_session_documents
# from backend.utils.config import PROCESSED_DIR

# session_id = "28735376-65a1-4808-82a6-556e58df9f06"

# print(f"🔥 Running multi-file chunk test for session: {session_id}\n")

# chunks = chunk_session_documents(session_id)

# print(f"\n✅ Total chunks generated: {len(chunks)}")

# # Print first 2 chunk metadata entries
# print("\n📌 Sample chunk metadata:")
# print(json.dumps(chunks[:2], indent=2))

# session_dir = PROCESSED_DIR / session_id

# # ✅ Find doc folders
# doc_folders = [d for d in session_dir.iterdir() if d.is_dir() and not d.name.endswith(".json")]

# chunk_folders = []
# for doc in doc_folders:
#     doc_chunks = [c for c in doc.glob("chunks_*") if c.is_dir()]
#     chunk_folders.extend(doc_chunks)

# print(f"\n📁 Files chunked: {len(chunk_folders)}")
# for d in chunk_folders:
#     print(f" - {d.name} (inside {d.parent.name})")

# # ✅ Display tree of chunks only
# print("\n📂 Directory tree (chunk folders only):")
# for root, dirs, files in os.walk(session_dir):
#     if not any("chunks_" in p for p in root.split(os.sep)):
#         continue

#     level = root.replace(str(session_dir), "").count(os.sep)
#     indent = " " * 2 * level
#     print(f"{indent}{os.path.basename(root)}/")

#     subindent = " " * 2 * (level + 1)
#     for f in files:
#         print(f"{subindent}{f}")

# # ✅ Validate sample folder contains text + meta
# sample_chunk = None
# for folder in chunk_folders:
#     chunk1 = folder / "chunk_1"
#     if chunk1.exists():
#         sample_chunk = chunk1
#         break

# if sample_chunk:
#     print(f"\n🔍 Checking sample chunk at: {sample_chunk}")
#     expected_files = {"text.txt", "meta.json"}
#     actual_files = {f.name for f in sample_chunk.iterdir() if f.is_file()}

#     missing = expected_files - actual_files
#     if missing:
#         print(f"❌ Missing files: {missing}")
#     else:
#         print("✅ meta.json & text.txt present!")

# print("\n🎯 Chunk test completed\n")

import os, sys, json
from pathlib import Path

# Add project root
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.core.chunking import chunk_session_documents
from backend.utils.config import PROCESSED_DIR

# ⚠️ Use your active session ID
session_id = "9d343441-b56b-4e3b-a823-6e66bb775f0a"

print(f"🧩 Running document chunking test for session: {session_id}\n")

chunks = chunk_session_documents(session_id)

print(f"\n✅ Total chunks generated: {len(chunks)}")

# Print first few metadata entries
print("\n📌 Sample chunk metadata:")
print(json.dumps(chunks[:2], indent=2))

session_dir = PROCESSED_DIR / session_id

# ✅ Find chunk folders
chunk_folders = []
for doc_folder in session_dir.iterdir():
    if doc_folder.is_dir():
        for cf in doc_folder.glob("chunks_*"):
            if cf.is_dir():
                chunk_folders.append(cf)

print(f"\n📁 Total chunk folders: {len(chunk_folders)}")
for cf in chunk_folders:
    print(f" - {cf.name} (in {cf.parent.name})")

# ✅ Validate chunk subfolder contents
sample_chunk_folder = None
for cf in chunk_folders:
    first_chunk = cf / "chunk_1"
    if first_chunk.exists():
        sample_chunk_folder = first_chunk
        break

if sample_chunk_folder:
    print(f"\n🔍 Checking sample chunk folder: {sample_chunk_folder}")
    expected_files = {"text.txt", "meta.json"}
    found_files = {f.name for f in sample_chunk_folder.iterdir() if f.is_file()}
    missing = expected_files - found_files
    if missing:
        print(f"❌ Missing: {missing}")
    else:
        print("✅ Both text.txt and meta.json found!")

print("\n🎯 Chunking test completed.\n")