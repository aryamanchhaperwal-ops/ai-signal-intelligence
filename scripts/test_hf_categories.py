import urllib.request
import json
import ssl
import certifi

ctx = ssl.create_default_context(cafile=certifi.where())

categories = [
    "agent", "chat", "code", "image", "audio", "video", "search", "vision", 
    "automation", "assistant", "diffusion", "rag", "summarization", "translation", 
    "voice", "transcription", "multimodal", "robotics", "generation", "nlp",
    "embedding", "classification", "detector", "workflow", "reasoning"
]

all_spaces = {}
for cat in categories:
    url = f"https://huggingface.co/api/spaces?search={cat}&limit=100&full=false"
    req = urllib.request.Request(url, headers={"User-Agent": "AISignalIntelligence/1.0"})
    try:
        with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            for s in data:
                space_id = s.get("id")
                if space_id and space_id not in all_spaces:
                    all_spaces[space_id] = s
            print(f"Category '{cat}': total unique spaces so far: {len(all_spaces)}")
            if len(all_spaces) >= 1200:
                break
    except Exception as e:
        print(f"Error '{cat}': {e}")

print(f"Final unique spaces count: {len(all_spaces)}")
