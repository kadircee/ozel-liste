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
    python update.py --purge    # degisiklik olmasa bile tum eklentilerin jsDelivr cache'ini temizler
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

# Bu deponun kendi plugins.json adresi (jsDelivr purge için)
OWN_REPO = "kadircee/ozel-liste"
OWN_BRANCH = "main"


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


def cs3_to_purge_url(cs3_url):
    """raw.githubusercontent.com .cs3 url'sini jsDelivr purge URL'sine cevirir."""
    m = re.match(r"https://raw\.githubusercontent\.com/([^/]+)/([^/]+)/builds/(.+)", cs3_url)
    if not m:
        return None
    owner, repo, fname = m.group(1), m.group(2), m.group(3)
    return "https://purge.jsdelivr.net/gh/{0}/{1}@builds/{2}".format(owner, repo, fname)


def build_purge_list(data, updated_names=None):
    """jsDelivr purge yapilacak URL listesini olusturur.

    updated_names=None  -> tum eklentiler (--purge modu)
    updated_names=set() -> yalnizca guncellenen eklentiler (normal mod)
    """
    # Her zaman kendi plugins.json'u temizle
    urls = ["https://purge.jsdelivr.net/gh/{0}@{1}/plugins.json".format(OWN_REPO, OWN_BRANCH)]
    seen = set()
    for p in data:
        name = p.get("internalName", p.get("name", ""))
        if updated_names is not None and name not in updated_names:
            continue
        cs3 = p.get("url", "")
        if cs3 in seen:
            continue
        seen.add(cs3)
        purge_url = cs3_to_purge_url(cs3)
        if purge_url:
            urls.append(purge_url)
    return urls


def do_purge(purge_urls):
    """Verilen URL listesindeki jsDelivr cache'lerini temizler."""
    print("\n[JSDELIVR] CDN cache temizleniyor ({0} adres)...".format(len(purge_urls)))
    ok = 0
    fail = 0
    for url in purge_urls:
        label = url.replace("https://purge.jsdelivr.net/gh/", "")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=NET_TIMEOUT) as resp:
                status = resp.status
            if status == 200:
                print("  [OK] {0}".format(label))
                ok += 1
            else:
                print("  [HTTP {0}] {1}".format(status, label))
                fail += 1
        except Exception as ex:
            print("  [HATA] {0}: {1}".format(label, ex))
            fail += 1
    print("[JSDELIVR] Tamamlandi: {0} OK, {1} basarisiz.".format(ok, fail))


def main():
    parser = argparse.ArgumentParser(description="ozel-liste kaynak senkronizasyonu")
    parser.add_argument("--check", action="store_true", help="yazmadan sadece farklari raporla (degisiklik varsa exit 1)")
    parser.add_argument("--purge", action="store_true", help="degisiklik olmasa bile tum eklentilerin jsDelivr cache'ini temizle")
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
            missing.append((name, "kaynak plugins.json {0}: {1}".format(ex.code, src_url)))
            continue
        except Exception as ex:
            missing.append((name, "kaynak cekilemedi: {0}".format(ex)))
            continue

        items = src if isinstance(src, list) else src.get("plugins", [])
        match = None
        for item in items:
            if isinstance(item, dict) and item.get("internalName") == name:
                match = item
                break
        if not match:
            missing.append((name, "kaynaktaki plugins.json icinde '{0}' bulunamadi".format(name)))
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
        print("[GUNCELLEME] {0}:".format(name))
        for field, (old_v, new_v) in diffs.items():
            print("    {0}: {1} -> {2}".format(field, old_v, new_v))
    for name, reason in missing:
        print("[ATLANDI] {0}: {1}".format(name, reason))
    print("\nOzets: {0} eklenti guncel, {1} guncellenmeli, {2} erisilemedi.".format(
        unchanged, len(changed), len(missing)))

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
        # Guncellenen eklentilerin + kendi plugins.json'un CDN cache'ini temizle
        updated_names = {name for name, _ in changed}
        do_purge(build_purge_list(data, updated_names=updated_names))
    else:
        print("Yazma gerekmiyor.")

    # --purge: degisiklik olmasa bile tum eklentilerin cache'ini zorla temizle
    if args.purge and not changed:
        do_purge(build_purge_list(data, updated_names=None))


if __name__ == "__main__":
    main()