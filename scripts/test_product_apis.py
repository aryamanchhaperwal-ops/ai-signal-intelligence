import urllib.request
import json
import ssl
import certifi

ctx = ssl.create_default_context(cafile=certifi.where())

# Test 1: Hugging Face Spaces with search queries
queries = ["agent", "chat", "code", "image", "audio", "video", "search", "vision", "automation", "assistant"]
total_hf = 0
for q in queries:
    url = f"https://huggingface.co/api/spaces?search={q}&limit=100&full=false"
    req = urllib.request.Request(url, headers={"User-Agent": "AISignalIntelligence/1.0"})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            print(f"HF Space search '{q}': found {len(data)} spaces")
            total_hf += len(data)
    except Exception as e:
        print(f"Error {q}: {e}")

print(f"Total HF spaces sampled: {total_hf}")
