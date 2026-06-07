import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime

FEEDS = {
    "cnn": "https://podcasts.files.bbci.co.uk/p02nq0gn.rss",
    "voa": "https://learningenglish.voanews.com/podcast/?zoneId=1689"
}

def fetch_feed(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return r.read()

def parse_feed(xml_bytes):
    ns = {"itunes": "http://www.itunes.com/dtds/podcast-1.0.dtd"}
    root = ET.fromstring(xml_bytes)
    items = root.findall(".//item")
    episodes = []
    for item in items[:12]:
        title = item.findtext("title", "").strip()
        enclosure = item.find("enclosure")
        audio_url = enclosure.get("url", "") if enclosure is not None else ""
        pub_date = item.findtext("pubDate", "").strip()
        desc = item.findtext("description", "").strip()
        if "<" in desc:
            import re
            desc = re.sub(r"<[^>]+>", "", desc).strip()
        episodes.append({
            "title": title,
            "audioUrl": audio_url,
            "pubDate": pub_date,
            "desc": desc
        })
    return episodes

result = {}
for key, url in FEEDS.items():
    try:
        xml_bytes = fetch_feed(url)
        result[key] = parse_feed(xml_bytes)
        print(f"[OK] {key}: {len(result[key])} episodes")
    except Exception as e:
        print(f"[ERROR] {key}: {e}")
        result[key] = []

result["updated"] = datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")

with open("feeds.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("feeds.json written.")
