import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.core.model_manager import get_embedding_model

print("🔥 Testing model loading...\n")

model = get_embedding_model()

print(f"✅ Model loaded: {model.__class__.__name__}")
print(f"📦 Model name: {model}")