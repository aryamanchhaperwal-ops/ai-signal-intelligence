import urllib.request
import json
import ssl
import certifi

ctx = ssl.create_default_context(cafile=certifi.where())
url = "https://huggingface.co/api/spaces?search=agent&limit=5&full=true"
req = urllib.request.Request(url, headers={"User-Agent": "AISignalIntelligence/1.0"})
with urllib.request.urlopen(req, context=ctx, timeout=10) as resp:
    data = json.loads(resp.read().decode("utf-8"))
    for item in data:
        print("="*60)
        print("ID:", item.get("id"))
        print("Author:", item.get("author"))
        card = item.get("cardData") or {}
        print("Title:", card.get("title"))
        print("Emoji:", card.get("emoji"))
        print("SDK:", item.get("sdk"))
        print("Tags:", item.get("tags"))
        print("Likes:", item.get("likes"))
