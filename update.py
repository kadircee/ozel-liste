# -*- coding: utf-8 -*-
"""Kaynak depolardan guncel eklenti verilerini cekip plugins.json'u senkronize eder
ve DEPO-BILGILERI.md tablosunun alanlarini tazeler.

Kaynak builds/plugins.json adresi, listedeki .cs3 url'sinden turetilir:
    https://raw.githubusercontent.com/<owner>/<repo>/builds/<Isim>.cs3
    -> https://raw.githubusercontent.com/<owner>/<repo>/builds/plugins.json

Pure Mirror: kaynak ne yayinliyorsa birebir yansitilir. Senkronize edilen
alanlar: status, version, fileSize, fileHash, description, authors,
language, tvTypes. Kaynakta bulunamayan eklenti (404 veya kaynak
plugins.json'da kayit yok) yerel listeden TAMAMEN SILINIR: kaynakta
olmayan bizde de olmaz. iconUrl bilinçli olarak senkronize EDILMEZ:
bu depo ikon adreslerini normalize eder (kaynaktaki %size% yer tutuculari
sabit sz=128'e cevrilir) ve kaynak guncellemesi bu duzeltmeyi geri almasin.

Kullanim:
    python update.py            # senkron + tablo tazeleme (dosyaya yazar)
    python update.py --check    # sadece farklari raporlar, dosyaya yazmaz
    python update.py --purge    # tum eklentilerin jsDelivr cache'ini temizler (push sonrasi)
    python update.py --no-table # yalnizca plugins.json senkronu
"""
import argparse
import io
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
PLUGINS_PATH = os.path.join(REPO_DIR, "plugins.json")
DEPO_PATH = os.path.join(REPO_DIR, "DEPO-BILGILERI.md")
API = "https://api.github.com"

NET_TIMEOUT = 30
USER_AGENT = "Mozilla/5.0 (ozel-liste-update)"
# Simge barindiran CDN'ler site adresi sayilmaz; tablodaki Site hucresi bu
# adreslerle degistirilmez.
CDN_HOSTS = {
    "raw.githubusercontent.com", "blogger.googleusercontent.com",
    "play-lh.googleusercontent.com", "t3.gstatic.com", "gstatic.com",
    "themoviedb.org", "image.tmdb.org", "i.imgur.com",
    "google.com", "www.google.com",
}
# iconUrl bilinçli olarak senkronize edilmiyor: bu depo ikon adreslerini normalize
# ediyor (kaynaktaki %size% yer tutucuları sabit sz=128'e çevriliyor). Kaynak
# güncellemesi bu düzeltmeyi geri almasın diye sync alanları dışında tutulur.
# status BILINCLI olarak senkronize EDILIR (Pure Mirror): kaynak ne yayinliyorsa
# (1, 0, ...) aynen alinir; manuel status korumasi yoktur.
SYNC_FIELDS = ["status", "version", "fileSize", "fileHash", "description", "authors", "language", "tvTypes"]

# Bu deponun kendi plugins.json adresi (jsDelivr purge için)
OWN_REPO = "kadircee/ozel-liste"
OWN_BRANCH = "main"


def fix_mojibake(s):
    """Kaynak description'da coklu-UTF8 (mojibake) bozuklugu varsa onarir.

    Ozellikle lepotane/MRC-builds aciklamalari defalarca yanlis cozulmus
    yayinlaniyor ('güvenli' -> 'gÃ...Â¼venli'). ftfy varsa onu kullanir; yoksa
    cp1252/latin-1 geri kodlama zinciriyle en iyi cabayi dener. Okunabilir
    metin onarilir, Pure Mirror icin gorsel duzeltme sayilir.
    """
    try:
        import ftfy
        return ftfy.fix_text(s)
    except Exception:
        pass
    cur = s
    for _ in range(6):
        for enc in ("cp1252", "latin-1"):
            try:
                nxt = cur.encode(enc).decode("utf-8")
            except (UnicodeEncodeError, UnicodeDecodeError):
                continue
            cur = nxt
            break
        else:
            break
    return cur


def normalize_icon_url(icon):
    """Normalize source favicon size placeholders without duplicating ``sz=``."""
    return (icon or "").replace("sz=sz=128", "sz=128").replace(
        "sz=%size%", "sz=128").replace("%size%", "128")


def percent_encode(url):
    parts = urllib.parse.urlsplit(url)
    path = urllib.parse.quote(parts.path, safe="/%._~-")
    return urllib.parse.urlunsplit((parts.scheme, parts.netloc, path, parts.query, parts.fragment))


def norm_name(s):
    """registry.py/audit.py ile ayni kimlik anahtari."""
    value = (s or "").replace("\u0130", "i").replace("I", "i").casefold()
    return value.replace("\u0131", "i")


def domain_from_text(value):
    if not value:
        return ""
    value = value.strip()
    if "://" not in value:
        value = "https://" + value
    try:
        host = urllib.parse.urlsplit(value).hostname or ""
    except ValueError:
        return ""
    host = host.lower().strip(".")
    if host.startswith("www."):
        host = host[4:]
    if host.startswith("cdn."):
        host = host[4:]
    return host


def item_domain(item):
    """Kaynak kaydinin iconUrl'sinden site domainini cikarir."""
    icon = (item or {}).get("iconUrl", "")
    match = re.search(r"(?:domain=|url=)(https?%3A%2F%2F|https?://)?([^&\"\s]+)", icon, re.I)
    value = urllib.parse.unquote(match.group(2)) if match else icon
    return domain_from_text(value)


def github_token():
    tok = os.environ.get("GITHUB_TOKEN", "").strip()
    if tok:
        return tok
    try:
        out = subprocess.run(["gh", "auth", "token"], capture_output=True, text=True, timeout=30)
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()
    except Exception:
        pass
    return ""


def commit_date(repo, filename, tok, cache):
    """builds dalindaki dosyanin son commit tarihi (YYYY-MM-DD)."""
    key = (repo, filename)
    if key in cache:
        return cache[key]
    if not tok:
        cache[key] = None
        return None
    url = "%s/repos/%s/commits?sha=builds&path=%s&per_page=1" % (
        API, repo, urllib.parse.quote(filename, safe=""))
    try:
        req = urllib.request.Request(url, headers={
            "Authorization": "Bearer " + tok,
            "Accept": "application/vnd.github+json",
            "User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=NET_TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        value = data[0]["commit"]["committer"]["date"][:10] if data else None
    except Exception as ex:
        print("[TARIH] {0}/{1} alinamadi: {2}".format(repo, filename, ex))
        value = None
    cache[key] = value
    return value


def refresh_table(plugins, source_items, tok):
    """DEPO-BILGILERI.md tablosunu tazeler.

    - v                 <- plugins.json (kaynak manifesti)
    - Kaynak Tarih      <- builds dalindaki .cs3 dosyasinin son commit tarihi
    - Bizim Tarih       <- kaynak ilerlediyse Kaynak Tarih'e esitlenir
    - Site (domain)     <- kaynak iconUrl'sindeki site adresi (CDN'ler haric)
    """
    bykey = {}
    for p in plugins:
        m = re.match(r"https://raw\.githubusercontent\.com/([^/]+/[^/]+)/builds/", p.get("url", ""))
        if m:
            bykey[(norm_name(p.get("internalName", "")), m.group(1))] = p

    lines = io.open(DEPO_PATH, encoding="utf-8").read().replace("\r\n", "\n").split("\n")
    hdr = next((i for i, l in enumerate(lines) if l.startswith("| # |")), None)
    if hdr is None:
        print("[TABLO] tablo basligi bulunamadi, tazeleme atlandi")
        return 0
    zone = next((i for i, l in enumerate(lines)
                 if re.match(r"^#+\s+.*(Istenmeyenler|\u0130stenmeyenler)", l)), len(lines))

    # Kaynak manifestleri: kaynakta artik yayinlanmayan satirlar tablodan dusurulur.
    repos = set()
    for i in range(hdr, zone):
        m = re.match(r"^\| (\d+) \|", lines[i])
        if m:
            cells = [x.strip() for x in lines[i].strip().strip("|").split("|")]
            r = (re.search(r"github\.com/([^)]+)", cells[2]) or [None, ""])[1]
            if r:
                repos.add(r)
    manifests = {}
    for repo in sorted(repos):
        try:
            src = fetch_json("https://raw.githubusercontent.com/%s/builds/plugins.json" % repo)
            items = src if isinstance(src, list) else src.get("plugins", [])
            manifests[repo] = {norm_name(i.get("internalName", "")): i
                               for i in items if isinstance(i, dict)}
        except Exception as ex:
            print("[TABLO] %s manifesti alinamadi, satirlar korunuyor (%s)" % (repo, ex))

    cache = {}
    changed = 0
    drop = []
    for i in range(hdr, zone):
        line = lines[i]
        m = re.match(r"^\| (\d+) \|", line)
        if not m:
            continue
        cells = [x.strip() for x in line.strip().strip("|").split("|")]
        if len(cells) < 8:
            continue
        name = re.sub(r"^[^A-Za-z0-9]+", "", cells[1])
        repo = (re.search(r"github\.com/([^)]+)", cells[2]) or [None, ""])[1]
        if repo in manifests:
            item0 = manifests[repo].get(norm_name(name))
            if item0 is None:
                print("[TABLO] satir dusuruldu (kaynakta yok): %s (%s)" % (name, repo))
                drop.append(i)
                continue
        entry = bykey.get((norm_name(name), repo))
        item = source_items.get((norm_name(name), repo)) or (
            manifests.get(repo, {}).get(norm_name(name)))
        rec = entry or item
        if rec:
            version = str(rec.get("version", ""))
            if version and cells[4] != version:
                cells[4] = version
            fname = urllib.parse.unquote(rec.get("url", "").rsplit("/", 1)[-1])
            tarih = commit_date(repo, fname, tok, cache) if fname.endswith(".cs3") else None
            if tarih:
                if cells[5] != tarih:
                    cells[5] = tarih
                # Bizim Tarih yalnizca aktif (benimsenmis) satirlarda esitlenir.
                if entry and cells[6] < tarih:
                    cells[6] = tarih
        dom = item_domain(item) if item else ""
        if dom and dom not in CDN_HOSTS:
            link = re.search(r"\[([^\]]+)\]\((https?://[^)]+)\)", cells[3])
            if not link or domain_from_text(link.group(2)) != dom:
                cells[3] = "[{0}](https://{0})".format(dom)
        link = re.search(r"\[([^\]]+)\]\((https?://[^)]+)\)", cells[3])
        if link:
            host = domain_from_text(link.group(2))
            if host and link.group(1).lower() != host:
                cells[3] = "[{0}]({1})".format(host, link.group(2))
        newline = "| " + " | ".join(cells) + " |"
        if newline != line:
            lines[i] = newline
            changed += 1
    for i in reversed(drop):
        del lines[i]
    if drop:
        # Sira numaralarini yeniden ver (render zaten yeniden numaralar).
        zone2 = next((i for i, l in enumerate(lines)
                      if re.match(r"^#+\s+.*(Istenmeyenler|\u0130stenmeyenler)", l)), len(lines))
        n = 0
        for i in range(hdr, zone2):
            m = re.match(r"^\| (\d+) \|", lines[i])
            if not m:
                continue
            n += 1
            if m.group(1) != str(n):
                lines[i] = "| %d |" % n + lines[i][m.end():]
                changed += 1
    if changed:
        tmp = DEPO_PATH + ".tmp"
        io.open(tmp, "w", encoding="utf-8", newline="\n").write("\n".join(lines))
        os.replace(tmp, DEPO_PATH)
        print("[TABLO] {0} satir tazelendi, {1} satir dusuruldu.".format(changed, len(drop)))
    else:
        print("[TABLO] degisiklik yok.")
    return changed


def fetch_with_retry(op, tries=3):
    """429/5xx/gecici ag hatalarinda backoff'lu yeniden deneme (en fazla 3 deneme).
    404/401 gibi kesin hatalarda beklemeden firlatir."""
    delay = 2
    for i in range(tries):
        try:
            return op()
        except urllib.error.HTTPError as ex:
            if ex.code in (429, 500, 502, 503, 504) and i < tries - 1:
                time.sleep(delay)
                delay *= 2
                continue
            raise
        except Exception:
            if i < tries - 1:
                time.sleep(delay)
                delay *= 2
                continue
            raise


def fetch_json(url):
    def _get():
        req = urllib.request.Request(percent_encode(url), headers={"User-Agent": USER_AGENT})
        with urllib.request.urlopen(req, timeout=NET_TIMEOUT) as resp:
            return json.loads(resp.read().decode("utf-8"))
    return fetch_with_retry(_get)


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
    parser.add_argument("--apply", action="store_true",
                        help="guncellemeleri uygula (varsayilan; geriye donuk acik secenek)")
    parser.add_argument("--check", action="store_true", help="yazmadan sadece farklari raporla (degisiklik varsa exit 1)")
    parser.add_argument("--purge", action="store_true", help="tum eklentilerin jsDelivr cache'ini temizle (push sonrasi)")
    parser.add_argument("--no-table", action="store_true", help="DEPO-BILGILERI.md tablosunu tazeleme")
    args = parser.parse_args()

    with io.open(PLUGINS_PATH, encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        print("HATA: plugins.json liste degil")
        sys.exit(1)

    changed = []
    silinen = []
    missing = []
    unchanged = 0
    kept = []
    source_items = {}

    for e in data:
        name = e.get("internalName", "?")
        cs3 = e.get("url", "")
        src_url = source_plugins_url(cs3)
        if not src_url:
            # Yerel adres bozuk: kaynak dogrulanamiyor, silme; raporla ve koru.
            missing.append((name, "kaynak plugins.json url'si turetilemedi: " + cs3))
            kept.append(e)
            continue
        try:
            src = fetch_json(src_url)
        except urllib.error.HTTPError as ex:
            if ex.code == 404:
                # Pure Mirror: kaynakta yok -> yerelden sil (yoklugun kaniti).
                silinen.append((name, "kaynak plugins.json {0}: {1}".format(ex.code, src_url)))
                continue
            # 404 disi kalici HTTP hatasi (403/5xx retry sonrasi): yokluk kaniti
            # degil; gozetimsiz silmemek icin silme, raporla ve koru.
            missing.append((name, "kaynak plugins.json kalici hata {0}: {1}".format(ex.code, src_url)))
            kept.append(e)
            continue
        except Exception as ex:
            # Gecici erisim sorunu yokluga kanit degil: silme, raporla ve koru.
            missing.append((name, "kaynak cekilemedi: {0}".format(ex)))
            kept.append(e)
            continue

        items = src if isinstance(src, list) else src.get("plugins", [])
        match = None
        for item in items:
            if isinstance(item, dict) and item.get("internalName") == name:
                match = item
                break
        if not match:
            # Pure Mirror: kaynak listeden dusurmus -> yerelden sil.
            silinen.append((name, "kaynaktaki plugins.json icinde '{0}' bulunamadi".format(name)))
            continue
        if match.get("status") == 0:
            # Kaynak eklentiyi devre disi biraktiysa yayinlamaya devam etme.
            silinen.append((name, "kaynak plugins.json status=0 yayinliyor"))
            continue

        mrepo = re.match(r"https://raw\.githubusercontent\.com/([^/]+/[^/]+)/builds/", cs3)
        if mrepo:
            source_items[(norm_name(name), mrepo.group(1))] = match

        diffs = {}
        for field in SYNC_FIELDS:
            if field not in match:
                continue
            new_val = match[field]
            if field == 'description' and isinstance(new_val, str):
                # Kaynak mojibake yayinliyorsa okunabilir hale onar; karsilastirma
                # ve yazim onarilmis degerle yapilir (yeni CI kosusunda geri donmez).
                new_val = fix_mojibake(new_val)
            if field == 'authors' and isinstance(new_val, list):
                # kaynakta bas/son bosluklu yazar adlari gelir (or. 'ByAyzen ');
                # bu depo trim edilmis tutar (iconUrl kurali gibi normalizasyon)
                new_val = [a.strip() for a in new_val if isinstance(a, str)]
            old_val = e.get(field)
            if old_val != new_val:
                diffs[field] = (old_val, new_val)
                e[field] = new_val
        if diffs:
            changed.append((name, diffs))
        else:
            unchanged += 1
        kept.append(e)
    data = kept

    for name, diffs in changed:
        print("[GUNCELLEME] {0}:".format(name))
        for field, (old_v, new_v) in diffs.items():
            print("    {0}: {1} -> {2}".format(field, old_v, new_v))
    for name, reason in silinen:
        print("[SILINDI] {0}: {1}".format(name, reason))
    for name, reason in missing:
        print("[ATLANDI] {0}: {1}".format(name, reason))
    print("\nOzet: {0} eklenti guncel, {1} guncellenmeli, {2} silinecek, {3} erisilemedi.".format(
        unchanged, len(changed), len(silinen), len(missing)))

    if args.check:
        if changed or silinen or missing:
            print("Degisiklik var; --check modunda yazilmadi.")
            sys.exit(1)
        print("Her sey guncel.")
        return

    if changed or silinen:
        # Atomik yazma: once gecici dosyaya, sonra os.replace (yarim yazim olmaz).
        tmp = PLUGINS_PATH + ".tmp"
        with io.open(tmp, "w", encoding="utf-8", newline="\n") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
            f.write("\n")
        os.replace(tmp, PLUGINS_PATH)
        print("plugins.json guncellendi ({0} guncelleme, {1} silme).".format(len(changed), len(silinen)))
    else:
        print("Yazma gerekmiyor.")

    if not args.no_table:
        tok = github_token()
        if not tok:
            print("[TARIH] GitHub token yok: tablo tarihleri tazelenemedi "
                  "(GITHUB_TOKEN ya da gh auth login gerekli).")
        refresh_table(data, source_items, tok)

    # --purge: tum eklentilerin jsDelivr cache'ini temizler (push sonrasi calistirin)
    if args.purge:
        do_purge(build_purge_list(data, updated_names=None))


if __name__ == "__main__":
    main()