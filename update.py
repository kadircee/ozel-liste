# -*- coding: utf-8 -*-
"""Kaynak depolardan guncel eklenti verilerini cekip plugins.json'u senkronize eder.

Kaynak builds/plugins.json adresi, listedeki .cs3 url'sinden turetilir:
    https://raw.githubusercontent.com/<owner>/<repo>/builds/<Isim>.cs3
    -> https://raw.githubusercontent.com/<owner>/<repo>/builds/plugins.json

Senkronize edilen alanlar: version, fileSize, fileHash, description,
authors, language, tvTypes. iconUrl bilinçli olarak senkronize EDILMEZ:
bu depo ikon adreslerini normalize eder (kaynaktaki %size% yer tutuculari
sabit sz=128'e cevrilir) ve kaynak guncellemesi bu duzeltmeyi geri almasin.

Kullanim:
    python update.py            # guncellemeleri uygular (dosyaya yazar)
    python update.py --check    # sadece farklari raporlar, dosyaya yazmaz
"""
import argparse
import io
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
PLUGINS_PATH = os.path.join(REPO_DIR, "plugins.json")

NET_TIMEOUT = 30
USER_AGENT = "Mozilla/5.0 (ozel-liste-update)"
# iconUrl bilinçli olarak senkronize edilmiyor: bu depo ikon adreslerini normalize
# ediyor (kaynaktaki %size% yer tutucuları sabit sz=128'e çevriliyor). Kaynak
# güncellemesi bu düzeltmeyi geri almasın diye sync alanları dışında tutulur.
SYNC_FIELDS = ["version", "fileSize", "fileHash", "description", "authors", "language", "tvTypes"]


def percent_encode(url):
    parts = urllib.parse.urlsplit(url)
    path = urllib.parse.quote(parts.path, safe="/%._~-")
    return urllib.parse.urlunsplit((parts.scheme, parts.netloc, path, parts.query, parts.fragment))


def fetch_json(url):
    req = urllib.request.Request(percent_encode(url), headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=NET_TIMEOUT) as resp:
        return json.loads(resp.read().decode("utf-8"))


def source_plugins_url(cs3_url):
    """.cs3 url'sinden ayni deponun builds/plugins.json adresini turetir."""
    m = re.match(r"^(https://raw\.githubusercontent\.com/[^/]+/[^/]+/builds/)([^/?#]+\.cs3)([?#].*)?$", cs3_url)
    if not m:
        return None
    return m.group(1) + "plugins.json"


def main():
    parser = argparse.ArgumentParser(description="ozel-liste kaynak senkronizasyonu")
    parser.add_argument("--check", action="store_true", help="yazmadan sadece farklari raporla (degisiklik varsa exit 1)")
    args = parser.parse_args()

    with io.open(PLUGINS_PATH, encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        print("HATA: plugins.json liste degil")
        sys.exit(1)

    changed = []
    missing = []
    unchanged = 0

    for e in data:
        name = e.get("internalName", "?")
        cs3 = e.get("url", "")
        src_url = source_plugins_url(cs3)
        if not src_url:
            missing.append((name, "kaynak plugins.json url'si turetilemedi: " + cs3))
            continue
        try:
            src = fetch_json(src_url)
        except urllib.error.HTTPError as ex:
            missing.append((name, f"kaynak plugins.json {ex.code}: {src_url}"))
            continue
        except Exception as ex:
            missing.append((name, f"kaynak cekilemedi: {ex}"))
            continue

        items = src if isinstance(src, list) else src.get("plugins", [])
        match = None
        for item in items:
            if isinstance(item, dict) and item.get("internalName") == name:
                match = item
                break
        if not match:
            missing.append((name, f"kaynaktaki plugins.json icinde '{name}' bulunamadi"))
            continue

        diffs = {}
        for field in SYNC_FIELDS:
            if field not in match:
                continue
            new_val = match[field]
            old_val = e.get(field)
            if old_val != new_val:
                diffs[field] = (old_val, new_val)
                e[field] = new_val
        if diffs:
            changed.append((name, diffs))
        else:
            unchanged += 1

    for name, diffs in changed:
        print(f"[GUNCELLEME] {name}:")
        for field, (old_v, new_v) in diffs.items():
            print(f"    {field}: {old_v} -> {new_v}")
    for name, reason in missing:
        print(f"[ATLANDI] {name}: {reason}")
    print(f"\nOzets: {unchanged} eklenti guncel, {len(changed)} guncellenmeli, {len(missing)} erisilemedi.")

    if args.check:
        if changed or missing:
            print("Degisiklik var; --check modunda yazilmadi.")
            sys.exit(1)
        print("Her sey guncel.")
        return

    if changed:
        with io.open(PLUGINS_PATH, "w", encoding="utf-8", newline="\n") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        print("plugins.json guncellendi.")
    else:
        print("Yazma gerekmiyor.")


if __name__ == "__main__":
    main()