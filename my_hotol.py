import gzip, lzma, urllib.request, xml.etree.ElementTree as ET

urls = [
    "https://github.com/ferteque/Curated-M3U-Repository/raw/refs/heads/main/epg2.xml.gz",
    "https://github.com/ferteque/Curated-M3U-Repository/raw/refs/heads/main/epg11.xml.gz"
]

def fetch(url):
    print(f"Fetching: {url}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as r:
        data = r.read()
        print(f"  Downloaded {len(data)} bytes")

        if data[:2] == b"\x1f\x8b":  # gzip
            print("  Detected GZIP compression, decompressing...")
            data = gzip.decompress(data)
        elif data[:6] == b"\xfd7zXZ\x00":  # xz
            print("  Detected XZ compression, decompressing...")
            data = lzma.decompress(data)
        else:
            print("  No compression detected")

        print(f"  After decompression: {len(data)} bytes")
        return data

def parse(data):
    print("  Parsing XML...")
    return ET.fromstring(data)

def merge(tv1, tv2):
    print("Merging channels and programmes...")

    ids = {ch.get("id") for ch in tv1.findall("channel")}
    added_channels = 0
    for ch in tv2.findall("channel"):
        if ch.get("id") not in ids:
            tv1.append(ch)
            ids.add(ch.get("id"))
            added_channels += 1
    print(f"  Added {added_channels} new channels")

    keys = {(p.get("channel"), p.get("start"), p.get("stop")) for p in tv1.findall("programme")}
    added_programmes = 0
    for p in tv2.findall("programme"):
        k = (p.get("channel"), p.get("start"), p.get("stop"))
        if k not in keys:
            tv1.append(p)
            keys.add(k)
            added_programmes += 1
    print(f"  Added {added_programmes} new programmes")

    return tv1

# Fetch and parse all sources
trees = [parse(fetch(u)) for u in urls]

# Merge them
merged = merge(trees[0], trees[1])

# Convert back to string
output = ET.tostring(merged, encoding="utf-8", xml_declaration=True)

# Debug: print first 100 characters of XML
print("\n===== Preview of merged EPG.xml =====")
print(output.decode("utf-8")[:100])
print("... (truncated)")
print("=====================================\n")

# Write to file
with open("epg.xml", "wb") as f:
    f.write(output)

print("✅ epg.xml written successfully")
