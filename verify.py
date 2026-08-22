# -*- coding: utf-8 -*-
"""ozel-liste yapısal + ağ kontrollü doğrulama script'i.

Kullanım:
    python verify.py            # yapısal + ağ kontrolleri (varsayılan)
    python verify.py --offline  # yalnızca yapısal kontroller (CI push için)
    python verify.py --deep     # ağ kontrolleri + .cs3 icinden gercek cekim
                                # domainlerini cikarip site sagligini kontrol et
    python verify.py --health   # aktif eklentilerin cekim domainleri TAMAMEN
                                # olmus ise plugins.json'da status:0 uygula
                                # (yalnizca elle calistirilir, otomatik degil)

Ağ kontrolleri (varsayılan modda çalışır):
    - Her eklentinin .cs3 dosyasını indirir; HTTP durumunu, fileSize ve
      fileHash (sha256) uyumunu doğrular.
    - iconUrl adresine GET atar, HTTP 200 dönüp dönmediğine bakar.
    - Kaynak depolar geçici erişilemezse "atlanabilir" kabul edilir ve
      uyarı olarak raporlanır; ancak dosya 404 ise hata sayılır.

--deep modu (deneysel):
    - Her eklentinin .cs3 arsivi acilir, classes.dex icinden ASCII hostname
      adaylari cikarilir (bilinen TLD'ler + filtreler) ve DNS + HTTP ile
      test edilir. Ikon domaini yerine eklentinin GERCEKTEN veri cektigi
      domainler izlendigi icin yanlis alarm riski dusuktur. Yalnizca uyari
      uretir; karar icin referans alinmaz.
"""
import argparse
import hashlib
import io
import json
import os
import re
import socket
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
import zipfile

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
PLUGINS_PATH = os.path.join(REPO_DIR, "plugins.json")
REPO_JSON_PATH = os.path.join(REPO_DIR, "repo.json")

HASH_RE = re.compile(r"^sha256-[0-9a-f]{64}$")
REQUIRED = ["url", "status", "version", "apiVersion", "name", "internalName", "authors", "fileHash", "fileSize"]
VALID_TVTYPES = {"Movie", "TvSeries", "Anime", "Live", "AsianDrama", "Others", "Documentary", "AnimeMovie", "OVA", "Cartoon"}
VALID_LANGS = {"tr", "en", "es", "fr", "ar", "id", "ru", "mx", "hi", "pt", "de", "it", "nl", "ja", "ko", "zh", "az", "fa"}
NET_TIMEOUT = 30
MAX_DOWNLOAD = 10 * 1024 * 1024  # 10 MB güvenlik sınırı
USER_AGENT = "Mozilla/5.0 (ozel-liste-verify)"


def percent_encode(url):
    """URL'nin path kısmındaki ASCII olmayan karakterleri encode eder."""
    parts = urllib.parse.urlsplit(url)
    path = urllib.parse.quote(parts.path, safe="/%._~-")
    return urllib.parse.urlunsplit((parts.scheme, parts.netloc, path, parts.query, parts.fragment))


def http_get(url, timeout=NET_TIMEOUT):
    req = urllib.request.Request(percent_encode(url), headers={"User-Agent": USER_AGENT})
    return urllib.request.urlopen(req, timeout=timeout)


def fetch(url, timeout=NET_TIMEOUT):
    """İçeriği döndürür. HTTP hatalarında (durum, url, reason) tuple fırlatır."""
    with http_get(url, timeout) as resp:
        status = getattr(resp, "status", resp.getcode())
        return resp.read(), status


def check_entry_offline(e, errors, warnings, seen):
    name = e.get("internalName", "?")
    for f in REQUIRED:
        if f not in e:
            errors.append(f"{name}: eksik alan '{f}'")
    for f in ["status", "version", "apiVersion", "fileSize"]:
        if f in e and not isinstance(e[f], int):
            errors.append(f"{name}: '{f}' int olmali (tip={type(e[f]).__name__})")
    if e.get("authors") is not None:
        if not isinstance(e["authors"], list):
            errors.append(f"{name}: 'authors' liste olmali")
        else:
            for a in e["authors"]:
                if not isinstance(a, str) or not a.strip():
                    errors.append(f"{name}: 'authors' bos/gecersiz yazar adi")
                elif a != a.strip():
                    errors.append(f"{name}: 'authors' icinde kirpilamamis bosluk: '{a}'")
    for key in ["internalName", "url", "fileHash"]:
        v = e.get(key)
        if v in seen:
            errors.append(f"duplicate {key}: {v} ({name} ve {seen[v]})")
        else:
            seen[v] = name
    if not e.get("url", "").endswith(".cs3"):
        errors.append(f"{name}: url .cs3 ile bitmiyor")
    if e.get("fileHash") and not HASH_RE.match(str(e["fileHash"])):
        errors.append(f"{name}: fileHash format gecersiz")
    if "status" in e and e["status"] not in (0, 1, 2, 3):
        errors.append(f"{name}: 'status' 0-3 arasi olmali (0=kapali, 1=acik, 2=yavas, 3=sadece beta) ({e['status']})")
    if "tvTypes" in e and e["tvTypes"] is not None:
        if not isinstance(e["tvTypes"], list) or not e["tvTypes"]:
            errors.append(f"{name}: 'tvTypes' dolu liste olmali")
        else:
            for t in e["tvTypes"]:
                if t not in VALID_TVTYPES:
                    errors.append(f"{name}: gecersiz tvType '{t}' (gecerli: {', '.join(sorted(VALID_TVTYPES))})")
    if "language" in e and e["language"] is not None:
        lang = str(e["language"]).lower()
        if lang not in VALID_LANGS:
            errors.append(f"{name}: taninmayan language '{e['language']}'")
    for field in ["description", "name"]:
        v = e.get(field)
        if isinstance(v, str) and v != v.strip():
            errors.append(f"{name}: '{field}' basinda/sonunda bosluk var")
    icon = e.get("iconUrl")
    if icon is not None:
        if not isinstance(icon, str):
            errors.append(f"{name}: 'iconUrl' string olmali")
        elif "%size%" in icon:
            warnings.append(f"{name}: 'iconUrl' icinde %size% yer tutucusu var (ekosistemde gecerli desen; CloudStream runtime'da boyutu doldurur)")
    desc = e.get("description")
    if isinstance(desc, str) and len(desc.strip()) == 0:
        errors.append(f"{name}: 'description' bos")


def check_online(e, errors, warnings):
    name = e.get("internalName", "?")
    url = e.get("url")
    expected_size = e.get("fileSize")
    expected_hash = e.get("fileHash")

    if not url:
        return None
    try:
        data, status = fetch(url)
    except urllib.error.HTTPError as ex:
        if ex.code == 404:
            errors.append(f"{name}: .cs3 404 (kaynak kapali veya dosya yok): {url}")
        else:
            warnings.append(f"{name}: .cs3 HTTP {ex.code} (atlandi): {url}")
        return None
    except Exception as ex:
        warnings.append(f"{name}: .cs3 indirilemedi (atlandi: {ex})")
        return None

    if isinstance(expected_size, int):
        if len(data) != expected_size:
            errors.append(f"{name}: fileSize uyumsuz (listedeki={expected_size}, gercek={len(data)})")
    if isinstance(expected_hash, str) and expected_hash.startswith("sha256-"):
        digest = hashlib.sha256(data).hexdigest()
        if digest != expected_hash[len("sha256-"):]:
            errors.append(f"{name}: fileHash uyumsuz (beklenen={expected_hash[7:12]}..., gercek={digest[:5]}...)")

    icon = e.get("iconUrl")
    if icon:
        try:
            req = urllib.request.Request(percent_encode(icon), method="HEAD", headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=NET_TIMEOUT) as resp:
                if getattr(resp, "status", resp.getcode()) != 200:
                    warnings.append(f"{name}: iconUrl HTTP {resp.status} (atlandi)")
        except Exception as ex:
            warnings.append(f"{name}: iconUrl kontrol edilemedi (atlandi: {ex})")

    return data


ICON_CDN_HOSTS = {
    "play-lh.googleusercontent.com", "lh3.googleusercontent.com",
    "cdn.discordapp.com", "avatars.githubusercontent.com",
    "raw.githubusercontent.com", "githubusercontent.com",
}


def extract_site_domain(icon):
    """iconUrl'den icerik cekilen kaynak site domainini turetir.

    Desteklenen desenler:
      - https://www.google.com/s2/favicons?domain=<site>&sz=...
      - https://t2.gstatic.com/faviconV2?...&url=<https://site>...
      - dogrudan ikon URL'si (https://<site>/favicon.ico gibi)
    Ikon CDN'lerinden (play-lh, discord, avatars, raw.githubusercontent)
    site domaini turetilmez -> None doner.
    """
    if not isinstance(icon, str) or not icon:
        return None
    parts = urllib.parse.urlsplit(icon)
    host = (parts.netloc or "").lower()
    if not host:
        return None
    query = urllib.parse.parse_qs(parts.query)
    if host in ("www.google.com", "google.com"):
        dom = query.get("domain")
        return dom[0].strip() if dom else None
    if host.endswith("gstatic.com"):
        u = query.get("url")
        if u:
            inner = urllib.parse.urlsplit(u[0])
            return inner.netloc or None
        return None
    if host in ICON_CDN_HOSTS or host.endswith("githubusercontent.com"):
        return None
    return host


def check_site(e, errors, warnings):
    """Kaynak site domaininin DNS + ana sayfa sagligini kontrol eder.

    Amac: .cs3 dosyasi indirilebilir ama icerik cekilen site olmus olabilir
    (9 Feroxx eklentisi bu yuzden calismiyordu). Bu kontrol o durumu yakalar.
    Not: bot korumasi (403) / gecici hatalar 'atlandi' uyarisi olarak yazilir;
    karar icin referans alinmaz, yalnizca uyari uretir.
    """
    name = e.get("internalName", "?")
    domain = extract_site_domain(e.get("iconUrl"))
    if not domain:
        return
    bare = domain.split(":")[0].lstrip("www.")
    try:
        ip = socket.gethostbyname(bare)
        if ip.startswith(("127.", "0.", "169.254.")) or ip == "::1":
            warnings.append(f"[SITE] {name}: '{domain}' loopback'a cozuluyor ({ip}) - engellenmis/ele gecirilmis olabilir")
            return
    except socket.gaierror:
        warnings.append(f"[SITE] {name}: '{domain}' DNS'te cozulemiyor (alan adi olmus/ele gecirilmis olabilir)")
        return

    for method in ("HEAD", "GET"):
        try:
            req = urllib.request.Request(percent_encode("https://" + domain), method=method,
                                         headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=NET_TIMEOUT) as resp:
                status = getattr(resp, "status", resp.getcode())
                if 200 <= status < 400:
                    return  # site ayakta
                warnings.append(f"[SITE] {name}: site HTTP {status} (atlandi): {domain}")
                return
        except urllib.error.HTTPError as ex:
            if method == "HEAD" and ex.code in (400, 405, 501):
                continue  # HEAD desteklenmiyor, GET'e dus
            if ex.code in (403, 401):
                warnings.append(f"[SITE] {name}: site erisim engelliyor ({ex.code}, bot korumasi olabilir): {domain}")
            elif ex.code == 404:
                warnings.append(f"[SITE] {name}: site ana sayfasi 404 ({domain} tasinmis/kapali olabilir)")
            else:
                warnings.append(f"[SITE] {name}: site HTTP {ex.code} (atlandi): {domain}")
            return
        except Exception as ex:
            if method == "GET":
                warnings.append(f"[SITE] {name}: siteye ulasilamadi (atlandi: {ex}): {domain}")
            continue  # HEAD ag hatasi verdi, GET ile tekrar dene


# --deep modu: .cs3 icindeki classes.dex'ten gercek cekim domainlerini cikarir

DEX_TLD_RE = re.compile(
    r"\.(com|net|org|io|tv|me|app|live|club|site|dev|de|nl|co|vip|biz|info|top|"
    r"online|xyz|cc|gg|ru|es|us|uk|in|tr|mobi|tech|pro|click|link|today|stream|"
    r"watch|cloud|media|video|play|fun|zone|news|art)\b", re.I)
DEX_HOST_RE = re.compile(r"[a-z0-9](?:[a-z0-9-]{0,62})?(?:\.[a-z0-9-]{1,30}){1,4}", re.I)
DEX_SKIP_KEYWORDS = (
    "youtube", "youtu.be", "twitter", "x.com", "facebook", "instagram",
    "tiktok", "telegram", "discord", "whatsapp", "snapchat", "reddit",
    "pinterest", "w3.org", "schema.org", "apache", "mozilla", "wikipedia",
    "google", "gstatic", "googleapis", "googleusercontent", "githubusercontent",
    "raw.github", "jsdelivr", "cloudflare", "amazonaws", "themoviedb", "tmdb",
    "exoplayer", "kotlin", "coroutines", "okhttp", "retrofit", "coil", "glide",
    "ktor", "java", "openjdk", "oracle", "gradle", "android", "microsoft",
    "apple", "example.com", "localhost", "serialization", "continuation",
    "ffmpeg", "gmail", "mailto", "xmlns", "mime",
)


def extract_dex_domains(cs3_bytes, limit=8):
    """.cs3 arsivindeki classes.dex icinden hostname adaylarini cikarir."""
    try:
        zf = zipfile.ZipFile(io.BytesIO(cs3_bytes))
        names = [n for n in zf.namelist() if n.endswith((".dex", ".class"))]
        if not names:
            return []
        blob = b" ".join(zf.read(n) for n in names).decode("latin1")
    except Exception:
        return []
    seen = {}
    for m in DEX_HOST_RE.finditer(blob):
        tok = m.group(0).lower().strip(".-")
        if not DEX_TLD_RE.search(tok):
            continue
        labels = tok.split(".")
        if len(labels) < 2 or len(labels[-1]) < 2:
            continue
        if not labels[-1].isalpha():
            continue  # son etiket (TLD) harf disi karakter iceriyorsa gercek domain degil
        if any(len(x) > 30 for x in labels):
            continue
        if any(k in tok for k in DEX_SKIP_KEYWORDS):
            continue
        seen[tok] = seen.get(tok, 0) + 1
    if not seen:
        return []
    # once cok gecenler (gercek hedef domainler tekrar tekrar kullanilir)
    return [t for t, _ in sorted(seen.items(), key=lambda kv: -kv[1])][:limit]


def site_responds(domain):
    """DNS + HTTP ile domainin ayakta olup olmadigina bakar."""
    try:
        socket.setdefaulttimeout(5)
        ip = socket.gethostbyname(domain)
        if ip.startswith(("127.", "0.", "169.254.")) or ip == "::1":
            return False
    except socket.gaierror:
        return False
    for scheme in ("https", "http"):
        for method in ("GET", "HEAD"):  # GET once: parking (satilik) sayfasi ancak govdeden tespit edilir
            try:
                req = urllib.request.Request(percent_encode(scheme + "://" + domain), method=method,
                                             headers={"User-Agent": USER_AGENT})
                with urllib.request.urlopen(req, timeout=8) as resp:
                    status = getattr(resp, "status", resp.getcode())
                    if 200 <= status < 400:
                        if method == "GET" and _is_parking(resp.read(8192)):
                            return False  # "satilik/parking" sayfasi ayakta sayilmaz
                        return True
            except urllib.error.HTTPError as ex:
                if ex.code == 403:
                    return True  # sunucu yanitliyor; Cloudflare/bot korumasi engelliyor
                if 200 <= ex.code < 400:
                    return True
                if method == "HEAD" and ex.code in (400, 405, 501):
                    continue  # HEAD reddedildi, GET'e dus
                return False
            except Exception:
                if method == "GET":
                    break
                continue
    return False


def check_deep_site(e, cs3_bytes, warnings):
    """Eklentinin gercekten veri cektigi domainlerin sagligini kontrol eder.

    --deep modunda icon-domain yerine bu kontrol kullanilir. Eklentinin
    birden fazla kaynagindan en az biri ayaktaysa sorun sayilmaz; ancak
    hepsi yanit vermiyorsa [SITE] uyarisi uretilir.
    """
    name = e.get("internalName", "?")
    domains = extract_dex_domains(cs3_bytes)
    if not domains:
        return  # domainler dinamik uretiliyor; bu eklenti icin gecersiz
    dead = []
    alive = 0
    for d in domains[:6]:
        if site_responds(d):
            alive += 1
        else:
            dead.append(d)
    if alive == 0 and dead:
        warnings.append(f"[SITE] {name}: cekim domainlerinin tamami yanit vermiyor"
                        f" ({', '.join(dead)}) - site kapanmis olabilir")
    elif dead:
        warnings.append(f"[SITE] {name}: bazi cekim domainleri yanit vermiyor"
                        f" ({', '.join(dead)}) - ana kaynak ayakta")


# --health modu: olumlu kanitlara dayanarak otomatik status:0 karari

PARKING_MARKERS = (
    "satılıktır", "web sitesi satılık", "site is for sale", "website is for sale",
    "domain is for sale", "buy this domain", "domain is parked", "parked domain",
    "is pending renewal", "kaynaklar ve bilgiler", "dan.com", "afternic",
    "sedo.com", "nicsell", "bodis", "parkingcrew", "buydomains", "undeveloped",
)
TITLE_RE = re.compile(rb"<title[^>]*>(.*?)</title>", re.I | re.S)


def _is_parking(body):
    """Sayfa icerigi bir domain-parking (satilik) sayfasi mi?"""
    if not body:
        return False
    m = TITLE_RE.search(body)
    title = m.group(1).decode("latin1", "ignore").lower() if m else ""
    snippet = title + " " + body[:4096].decode("latin1", "ignore").lower()
    return any(k in snippet for k in PARKING_MARKERS)


def site_classify(domain):
    """Bir cekim domainini siniflandirir.

    Donus:
      'alive'  - kesin ayakta (HTTP 2xx/3xx normal icerik, veya 403 bot korumasi)
      'dead'   - kesin olmus (DNS cozulmuyor, 404/410, TLS hatali + http de olmus,
                 veya sayfa parking/''satilik'' sayfasi)
      'unknown'- karar verilemez (gecici ag hatasi/zaman asimi) -> otomatik karar YOK
    Yalnizca 'dead' olan siniflar otomatik status:0'a yol acar; herhangi bir
    'unknown' varsa o eklenti icin karar verilmez (yanlis pozitifi onlemek icin).
    """
    try:
        ip = socket.gethostbyname(domain)
        if ip.startswith(("127.", "0.", "169.254.", "::1")) or ip == "::1":
            return "dead"  # loopback'a cozuluyor (ele gecirilmis/engellenmis)
    except socket.gaierror:
        return "dead"  # DNS'te yok
    for scheme in ("https", "http"):
        try:
            req = urllib.request.Request(percent_encode(scheme + "://" + domain),
                                         method="GET", headers={"User-Agent": USER_AGENT})
            with urllib.request.urlopen(req, timeout=12) as resp:
                status = getattr(resp, "status", resp.getcode())
                if 200 <= status < 400:
                    if _is_parking(resp.read(8192)):
                        return "dead"
                    return "alive"
                if status in (404, 410, 451):
                    return "dead"
                if status in (403, 401):
                    return "alive"  # sunucu yanitliyor; Cloudflare/bot korumasi
                return "unknown"
        except urllib.error.HTTPError as ex:
            if ex.code in (404, 410, 451):
                return "dead"
            if ex.code in (403, 401):
                return "alive"
            return "unknown"
        except ssl.SSLError:
            continue  # https TLS sorunu; http'ye dus
        except (socket.timeout, TimeoutError):
            continue  # zaman asimi gecici olabilir; diger scheme'i dene
        except Exception:
            continue
    return "unknown"


def check_health(e, cs3_bytes, data, disabled):
    """Aktif eklentinin tum cekim domainleri kesin olmus ise status:0 uygular.

    Guvenlik onlemleri:
      - domain cikarilamayan (dinamik) eklentilere dokunulmaz,
      - en az bir domain 'alive' ise dokunulmaz,
      - herhangi bir domain 'unknown' ise dokunulmaz (belirsizlik = karar yok),
      - status:1'e (yeniden acma) ASLA otomatik donulmez; bunu yalnizca kullanici yapar.
    """
    name = e.get("internalName", "?")
    if e.get("status") == 0:
        return  # zaten kapali
    domains = extract_dex_domains(cs3_bytes)
    if not domains:
        print(f" SAGLIK {name}: domain cikarilamadi (dinamik) - karar verilmedi")
        return
    statuses = {d: site_classify(d) for d in domains[:6]}
    alive = [d for d, s in statuses.items() if s == "alive"]
    dead = [d for d, s in statuses.items() if s == "dead"]
    unknown = [d for d, s in statuses.items() if s == "unknown"]
    if alive:
        print(f" SAGLIK {name}: ayakta ({', '.join(alive)})")
        return
    if dead and not unknown:
        for entry in data:
            if entry.get("internalName") == name:
                entry["status"] = 0
                break
        disabled.append(name)
        print(f" SAGLIK {name}: OLU - status:0 yapildi (olmus domainler: {', '.join(dead)})")
    else:
        print(f" SAGLIK {name}: belirsiz (alive=yok, dead={len(dead)}, unknown={len(unknown)}) - dokunulmadi")


def save_plugins(data):
    # newline="\n" (update.py ile ayni): Windows'ta CRLF'ye cevrilip butun dosyanin
    # satir-sonu diff'i cikmamasi icin LF sabit tutulur.
    with io.open(PLUGINS_PATH, "w", encoding="utf-8", newline="\n") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


def main():
    parser = argparse.ArgumentParser(description="ozel-liste dogrulama")
    parser.add_argument("--offline", action="store_true", help="yalnizca yapisal kontroller (ag istegi yok)")
    parser.add_argument("--skip-icons", action="store_true", help="iconUrl ag kontrolunu atla")
    parser.add_argument("--deep", action="store_true",
                        help=".cs3 icinden gercek cekim domainlerini cikarip site sagligini kontrol et (icon-domain kontrolu yerine)")
    parser.add_argument("--health", action="store_true",
                        help="aktif eklentilerin cekim domainleri TAMAMEN olmus ise plugins.json'da status:0 uygula "
                             "(yalnizca elle calistirilir; dinamik domainli/ayakta/belirsiz eklentilere dokunmaz)")
    args = parser.parse_args()

    if args.health and args.offline:
        print("HATA: --health ile --offline birlikte kullanilamaz (health ag ister).")
        sys.exit(1)

    errors = []
    warnings = []
    disabled = []

    try:
        data = json.load(io.open(PLUGINS_PATH, encoding="utf-8"))
    except Exception as ex:
        print(f"HATA: plugins.json okunamadi: {ex}")
        sys.exit(1)
    if not isinstance(data, list):
        errors.append("plugins.json: kok tum bir liste degil")

    seen = {}
    for e in data if isinstance(data, list) else []:
        if not isinstance(e, dict):
            errors.append("plugins.json: liste elemani nesne degil")
            continue
        check_entry_offline(e, errors, warnings, seen)
        if args.health:
            if e.get("status") == 0:
                continue
            try:
                cs3, _ = fetch(e["url"])
            except Exception as ex:
                warnings.append(f"{e.get('internalName', '?')}: .cs3 indirilemedi (health atlandi: {ex})")
                continue
            check_health(e, cs3, data, disabled)
        elif not args.offline:
            cs3 = check_online(e, errors, warnings)
            if args.deep:
                if cs3 is not None:
                    check_deep_site(e, cs3, warnings)
            elif not args.skip_icons:
                check_site(e, errors, warnings)

    if not args.offline and not args.skip_icons:
        pass  # ikon kontrolleri check_online icinde yapiliyor

    try:
        repo = json.load(io.open(REPO_JSON_PATH, encoding="utf-8"))
        if "pluginLists" not in repo:
            errors.append("repo.json: pluginLists eksik")
        elif not isinstance(repo["pluginLists"], list) or not repo["pluginLists"]:
            errors.append("repo.json: pluginLists dolu liste olmali")
    except Exception as ex:
        errors.append(f"repo.json parse hatasi: {ex}")

    mode = "(ag kontrollu)" if not args.offline else ""
    if args.deep:
        mode = "(ag kontrollu + derin cekim domain kontrolu)"
    if args.health:
        mode = "(health: otomatik status:0)"
    print(f"plugins.json: {len(data) if isinstance(data, list) else '?'} eklenti incelendi {mode}")
    for w in warnings:
        print(" UYARI:", w)
    if args.health and disabled:
        save_plugins(data)
        print(f"HEALTH: {len(disabled)} eklenti status:0 yapildi ve plugins.json yazildi: {', '.join(disabled)}")
    elif args.health:
        print("HEALTH: kapatilacak eklenti yok.")
    if errors:
        print("HATALAR:")
        for err in errors:
            print(" -", err)
        sys.exit(1)
    print("Her sey gecerli.")


if __name__ == "__main__":
    main()