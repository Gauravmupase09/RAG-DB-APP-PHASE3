# import sys, os
# from pathlib import Path

# # Add project root to PYTHONPATH
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# from backend.core.text_cleaner import clean_text, save_clean_text
# from backend.utils.config import PROCESSED_DIR

# # Use the real uploaded session_id
# session_id = "28735376-65a1-4808-82a6-556e58df9f06"

# raw_file_path = PROCESSED_DIR / session_id / "raw_text.txt"

# if not raw_file_path.exists():
#     print(f"❌ raw_text.txt not found at: {raw_file_path}")
#     sys.exit(1)

# print(f"📄 Reading raw text from: {raw_file_path}")

# with open(raw_file_path, "r", encoding="utf-8") as f:
#     raw_text = f.read()

# cleaned = clean_text(raw_text)

# # Save cleaned output
# cleaned_path = save_clean_text(cleaned, session_id)

# print("\n✅ Cleaned text saved at:")
# print(cleaned_path)

# import sys, os
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# from backend.core.text_cleaner import clean_all_raw_files

# session_id = "28735376-65a1-4808-82a6-556e58df9f06"

# cleaned_files = clean_all_raw_files(session_id)

# print("\nCleaned files generated:")
# for f in cleaned_files:
#     print(f)

# import os, sys, json
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# from backend.core.text_cleaner import clean_all_raw_files
# from backend.utils.config import PROCESSED_DIR

# session_id = "28735376-65a1-4808-82a6-556e58df9f06"

# print(f"🔥 Running multi-file cleaner for session: {session_id}\n")

# cleaned_files = clean_all_raw_files(session_id)

# print("\n✅ Cleaned Files:")
# for f in cleaned_files:
#     print(" -", f)

# # Validate metadata index
# index_path = PROCESSED_DIR / session_id / "clean_index.json"
# print(f"\n📑 Checking metadata file: {index_path}")

# with open(index_path, "r", encoding="utf-8") as f:
#     meta = json.load(f)

# print("\n📂 Clean Index Metadata:")
# print(meta)

# print("\n🎯 Test completed.")


# import os, sys, json
# from pathlib import Path

# # Add project root to PYTHONPATH
# sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# from backend.core.text_cleaner import clean_all_raw_files
# from backend.utils.config import PROCESSED_DIR

# # ⚠️ Change if testing a different session
# session_id = "28735376-65a1-4808-82a6-556e58df9f06"

# print(f"🔥 Running multi-file cleaner for session: {session_id}\n")

# cleaned_files = clean_all_raw_files(session_id)

# print("\n✅ Cleaned Files:")
# for f in cleaned_files:
#     print(" -", f)

# print("\n🎯 Test completed.\n")

import os, sys, json
from pathlib import Path

# Add project root to PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.core.text_cleaner import clean_all_raw_files
from backend.utils.config import PROCESSED_DIR

# ⚠️ Use the new session ID
session_id = "9d343441-b56b-4e3b-a823-6e66bb775f0a"

print(f"🔥 Running text cleaner test for session: {session_id}\n")

cleaned_files = clean_all_raw_files(session_id)

print("\n✅ Cleaned Files:")
for f in cleaned_files:
    print(" -", f)

# ✅ Verify file_index.json got updated
meta_file = PROCESSED_DIR / session_id / "file_index.json"

if meta_file.exists():
    meta_data = json.loads(meta_file.read_text(encoding="utf-8"))
    print("\n📑 Updated file_index.json entries:")
    for entry in meta_data:
        print(entry)
else:
    print("❌ ERROR: file_index.json not found!")

print("\n🎯 Text cleaning test completed.\n")