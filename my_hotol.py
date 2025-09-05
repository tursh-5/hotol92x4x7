import gzip, lzma, urllib.request, xml.etree.ElementTree as ET

# Replace these with your actual EPG URLs
urls = [
    "https://github.com/ferteque/Curated-M3U-Repository/raw/refs/heads/main/epg2.xml.gz",
    "https://github.com/ferteque/Curated-M3U-Repository/raw/refs/heads/main/epg11.xml.gz"
]

def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as r:
        data = r.read()
        if data[:2] == b"\x1f\x8b":  # gzip
            data = gzip.decompress(data)
        elif data[:6] == b"\xfd7zXZ\x00":  # xz
            data = lzma.decompress(data)
        return data

def parse(data):
    return ET.fromstring(data)

def merge(tv1, tv2):
    ids = {ch.get("id") for ch in tv1.findall("channel")}
    for ch in tv2.findall("channel"):
        if ch.get("id") not in ids:
            tv1.append(ch)
            ids.add(ch.get("id"))

    keys = {(p.get("channel"), p.get("start"), p.get("stop")) for p in tv1.findall("programme")}
    for p in tv2.findall("programme"):
        k = (p.get("channel"), p.get("start"), p.get("stop"))
        if k not in keys:
            tv1.append(p)
            keys.add(k)
    return tv1

trees = [parse(fetch(u)) for u in urls]
merged = merge(trees[0], trees[1])
ET.ElementTree(merged).write("epg.xml", encoding="utf-8", xml_declaration=True)
