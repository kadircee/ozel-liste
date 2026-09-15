# -*- coding: utf-8 -*-
"""audit.py: tum kaynak repolari tarar, internalName'e gore gruplar, en yeni tarihi secer.

Kullanim:
    python audit.py --check    # sadece rapor (varsayilan; degisiklik varsa exit 1)
    python audit.py --apply    # guvenli durumlari uygula (belirsizler rapora duser)

Kurallar (DEPO-BILGILERI.md Tarih Takip Kurali):
    - Anahtar = normalize(internalName): TR duzeltmeli casefold (İ->i, I->ı).
    - Yasaklilar (Istenmeyenler tablosu) sonsuza dek yasak: asla eklenmez/degistirilmez.
    - Esit-tarih tie'lar otomatik cozulur: kazananlar repo adina gore alfabetik
      siralanir, her zaman ilki (kazananlar[0]) secilir; script durup sormaz.
      status takibi yoktur (Pure Mirror).
    - Yeni site tercihen tr + {Movie,TvSeries,Documentary}; uymayanlar rapora duser.
    - plugins.json'da yasakli kayit kalmissa ihlal raporu verilir (exit 1).
    - --check: yalnizca aksiyon (flip/yeni), orphan ve ihlal exit 1 uretir;
      filtre-disi ve yasakli-eleme kalici bilgi olarak raporlanir.
    - --apply bitiminde registry.py --sync --render --write otomatik cagrilir
      (yeni kayitlar icin tablo satiri elle eklenmeli).
    - Ag istekleri 429/5xx/gecici hatalarda backoff'lu yeniden denenir (3 deneme).
    - Yazmadan once .cs3 indirilir, sha256 dogrulanir.
    - Tarihler GitHub API'den (builds branch, dosya bazinda son commit). Token:
      GITHUB_TOKEN env, yoksa `gh auth token` ciktisi.
"""
import argparse
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse
import urllib.request

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
PLUGINS_PATH = os.path.join(REPO_DIR, 'plugins.json')
REGISTRY_PATH = os.path.join(REPO_DIR, 'registry.json')
DEPO_PATH = os.path.join(REPO_DIR, 'DEPO-BILGILERI.md')
API = 'https://api.github.com'
RAW = 'https://raw.githubusercontent.com/%s/builds/plugins.json'
UA = 'Mozilla/5.0 (ozel-liste-audit)'
ALLOWED_TV = {'Movie', 'TvSeries', 'Documentary'}


def norm(s):
    return (s or '').replace('İ', 'i').replace('I', 'ı').casefold()


def token():
    t = os.environ.get('GITHUB_TOKEN', '').strip()
    if t:
        return t
    try:
        out = subprocess.run(['gh', 'auth', 'token'], capture_output=True, text=True, timeout=30)
        if out.returncode == 0 and out.stdout.strip():
            return out.stdout.strip()
    except Exception:
        pass
    print('HATA: GitHub token yok (GITHUB_TOKEN ya da gh auth login)')
    sys.exit(2)


def percent_encode(url):
    """Turkce/ozel karakterli adresler icin cift-kodlamasiz quoted URL uretir:
    once unquote (hazir %XX cozulur), sonra quote (ham karakter kodlanir).
    GitHub API adresinde dosya adi QUERY icinde (`?path=...cs3`), .cs3
    indirmede PATH icinde olabilir; ikisi de kodlanir. urllib ASCII disi
    karakteri tasiyamadigi icin bu adim zorunludur."""
    parts = urllib.parse.urlsplit(url)
    path = urllib.parse.quote(urllib.parse.unquote(parts.path), safe='/%._~-')
    query = urllib.parse.quote(urllib.parse.unquote(parts.query), safe='=&%._~-')
    return urllib.parse.urlunsplit((parts.scheme, parts.netloc, path, query, parts.fragment))


def _open(req, timeout):
    """429/5xx/gecici ag hatalarinda backoff'lu yeniden deneme (en fazla 3 deneme).
    401/404 gibi kesin hatalarda beklemeden firlatir."""
    delay = 2
    for i in range(3):
        try:
            return urllib.request.urlopen(req, timeout=timeout)
        except urllib.error.HTTPError as ex:
            if ex.code in (429, 500, 502, 503, 504) and i < 2:
                time.sleep(delay)
                delay *= 2
                continue
            raise
        except Exception:
            if i < 2:
                time.sleep(delay)
                delay *= 2
                continue
            raise


def api_json(url, tok):
    req = urllib.request.Request(percent_encode(url), headers={'Authorization': 'Bearer ' + tok,
                                               'Accept': 'application/vnd.github+json',
                                               'User-Agent': UA})
    with _open(req, timeout=30) as r:
        return json.loads(r.read().decode('utf-8'))


def raw_json(url):
    req = urllib.request.Request(percent_encode(url), headers={'User-Agent': UA})
    with _open(req, timeout=60) as r:
        return json.loads(r.read().decode('utf-8'))


def raw_bytes(url):
    req = urllib.request.Request(percent_encode(url), headers={'User-Agent': UA})
    with _open(req, timeout=120) as r:
        return r.read()


def main():
    ap = argparse.ArgumentParser(description='ozel-liste kaynak denetimi')
    ap.add_argument('--apply', action='store_true', help='guvenli durumlari uygula')
    ap.add_argument('--check', action='store_true',
                    help='rapor modu (varsayilan); yazma yapilmaz, degisiklik varsa exit 1')
    args = ap.parse_args()
    tok = token()

    depo = io.open(DEPO_PATH, encoding='utf-8').read().replace('\r\n', '\n')

    # Yasaklilar: Istenmeyenler tablosu ilk sutunu
    banned = set()
    in_zone = False
    for line in depo.split('\n'):
        if re.match(r'^#+\s+.*(Istenmeyenler|İstenmeyenler)', line):
            in_zone = True
            continue
        if in_zone and line.startswith('## '):
            break
        if in_zone:
            m = re.match(r'^\| (.*?) \|', line)
            if m and not m.group(1).startswith('Eklenti') and not set(m.group(1)) <= set('-| '):
                banned.add(norm(re.sub(r'^[^\w]+', '', m.group(1)).strip()))
    print('yasakli sayisi: %d' % len(banned))
    if not banned:
        # Fail-loud: baslik tablo satirina yapistirilirsa (bkz. DEPO-BILGILERI.md
        # "Yasakli sayisi tek dogruluk kaynagidir") yasakli listesi sessizce bosalir
        # ve delete-zone korumasi devre disi kalir. Bos liste = dur.
        print('HATA: yasakli listesi BOS cikti — "## Istenmeyenler" basligi kendi satirinda mi? '
              '(delete-zone korumasi devre disi kalirdi; durduruldu)')
        sys.exit(2)

    # Kaynak evren: makine-okur registry.json (birincil) + plugins.json url'leri.
    # registry.json okunamazsa DEPO-BILGILERI.md Kaynak sutununa dusulur.
    repos = set()
    try:
        reg = json.load(io.open(REGISTRY_PATH, encoding='utf-8'))
        for g in reg['groups'].values():
            for c in g['candidates']:
                if c.get('source'):
                    repos.add(c['source'])
    except Exception as ex:
        print('UYARI: registry.json okunamadi (%s); DEPO-BILGILERI.md taraniyor' % ex)
        for m in re.finditer(r'\[.+?\]\(https://github\.com/([^/\)]+)/([^/\)]+)\)', depo):
            repos.add(m.group(1) + '/' + m.group(2))
    listed = json.load(io.open(PLUGINS_PATH, encoding='utf-8'))
    for p in listed:
        m = re.match(r'https://raw\.githubusercontent\.com/([^/]+)/([^/]+)/builds/', p.get('url', ''))
        if m:
            repos.add(m.group(1) + '/' + m.group(2))
    repos = sorted(repos)
    print('kaynak repo: %d' % len(repos))

    # Tum kaynak listeleri + dosya tarihleri
    pool = {}   # norm ad -> [(repo, kayit, tarih)]
    for repo in repos:
        try:
            d = raw_json(RAW % repo)
        except Exception as ex:
            print('ATLANDI %s: liste alinamadi (%s)' % (repo, ex))
            continue
        items = d if isinstance(d, list) else d.get('plugins', [])
        for it in items:
            if not isinstance(it, dict) or not it.get('internalName'):
                continue
            fn = urllib.parse.unquote(it.get('url', '').rsplit('/', 1)[-1])
            if not fn.endswith('.cs3'):
                continue
            try:
                c = api_json('%s/repos/%s/commits?sha=builds&path=%s&per_page=1' % (API, repo, fn), tok)
                tarih = c[0]['commit']['committer']['date'][:10] if c else None
            except Exception as ex:
                print('ATLANDI %s/%s: tarih alinamadi (%s)' % (repo, fn, ex))
                continue
            if tarih:
                pool.setdefault(norm(it['internalName']), []).append((repo, it, tarih))
    print('havuzda grup: %d' % len(pool))

    listed_by_norm = {}
    for p in listed:
        listed_by_norm[norm(p.get('internalName', ''))] = p

    flips, yeniler, elenen_yeni, guard, orphan, ihlal = [], [], [], [], [], []
    for key in sorted(pool):
        grp = sorted(pool[key], key=lambda x: x[2], reverse=True)
        top_tarih = grp[0][2]
        # Tie-breaker (Pure Mirror): esit tarihliler repo adina gore alfabetik
        # siralanir, HER ZAMAN ilki otomatik secilir; soru yok, bekleme yok.
        kazananlar = sorted([g for g in grp if g[2] == top_tarih], key=lambda g: g[0])
        cur = listed_by_norm.get(key)
        if cur:
            if key in banned:
                # YASAKLI-IHLAL: delete-zone'daki kayit plugins.json'da kalmis.
                # Flip uygulanmaz; listeden cikarma insan karari bekler.
                ihlal.append('%s yasakli ama plugins.json\'da duruyor (listeden cikarilmali)' % cur.get('internalName'))
                continue
            m = re.match(r'https://raw\.githubusercontent\.com/([^/]+)/([^/]+)/builds/', cur.get('url', ''))
            cur_repo = (m.group(1) + '/' + m.group(2)) if m else '?'
            cur_hist = [g for g in grp if g[0] == cur_repo]
            cur_tarih = cur_hist[0][2] if cur_hist else None
            if cur_tarih is None:
                # ORPHAN: listedeki kopyanin kaynagi bu grupta yok (rename/case-kaymasi).
                # Grup yine de degerlendirilir, kazanan otomatik secilir.
                orphan.append('%s: listede %s ama grupta yok (grup: %s)' % (
                    cur.get('internalName'), cur_repo, ', '.join('%s %s' % (r, t) for r, _, t in grp)))
                flips.append((cur, kazananlar[0]))
            elif top_tarih > cur_tarih:
                flips.append((cur, kazananlar[0]))
        else:
            if key in banned:
                guard.append('%s yasakli, kaynaklarda goruldu ama eleniyor' % grp[0][1].get('internalName'))
                continue
            repo, it, tarih = kazananlar[0]
            tv = set(it.get('tvTypes', []))
            if it.get('language') == 'tr' and tv and tv <= ALLOWED_TV:
                yeniler.append((repo, it, tarih))
            else:
                elenen_yeni.append('%s (%s): dil=%s tur=%s' % (it.get('internalName'), repo, it.get('language'), sorted(tv)))

    print('\n=== FLIP (%d) ===' % len(flips))
    for cur, (repo, it, tarih) in flips:
        print('  %s: %s -> %s %s' % (cur.get('internalName'), cur.get('url', '').split('/')[3:5], repo, tarih))
    print('=== YENI SITE (%d) ===' % len(yeniler))
    for repo, it, tarih in yeniler:
        print('  %s (%s) %s' % (it.get('internalName'), repo, tarih))
    print('=== FILTRE-DISI YENI (%d) ===' % len(elenen_yeni))
    print('\n'.join('  ' + c for c in elenen_yeni) or '  (yok)')
    print('=== YASAKLI-ELEME (kaynakta goruldu, delete-zone geregi elendi) (%d) ===' % len(guard))
    print('\n'.join('  ' + g for g in guard) or '  (yok)')
    print('=== ORPHAN (listedeki kaynak grupta yok) (%d) ===' % len(orphan))
    print('\n'.join('  ' + c for c in orphan) or '  (yok)')
    print('=== YASAKLI-IHLAL (delete-zone kaydi listede) (%d) ===' % len(ihlal))
    print('\n'.join('  ' + c for c in ihlal) or '  (yok)')

    action = flips + [(None, w) for w in yeniler]
    if not args.apply:
        # CI/CD dostu: kalici bilgi (filtre-disi, yasakli-eleme) exit uretmez;
        # yalnizca aksiyon, orphan ve ihlal dondurur.
        if action or orphan or ihlal:
            print('\n--apply siz calisti, aksiyon gerekiyor (exit 1).')
            sys.exit(1)
        print('\nYapilacak is yok.')
        return

    # --apply: sadece flips + yeniler, hash dogrulamali.
    # Tek eklentideki hata (indirilemedi/hash tutmadi) tum kosuyu durdurmaz:
    # hatali kayit atlanir, rapora duser.
    data = listed
    hatali = []
    for cur, (repo, it, tarih) in flips:
        try:
            blob = raw_bytes(it['url'])
            if 'sha256-' + hashlib.sha256(blob).hexdigest() != it['fileHash'] or len(blob) != it['fileSize']:
                raise ValueError('hash/boyut tutmadi')
        except Exception as ex:
            hatali.append('%s (%s): %s' % (it.get('internalName'), repo, ex))
            continue
        # status ve apiVersion dahil tum alanlar yeni kaynaktan aktarilir;
        # kaynakta olmayan alan yereli ezmez.
        for f in ['url', 'version', 'fileSize', 'fileHash', 'description', 'authors', 'language', 'tvTypes', 'status', 'apiVersion']:
            if f in it:
                cur[f] = it[f]
        if 'iconUrl' in it:
            icon = it['iconUrl'] or ''
            if '%size%' in icon:
                icon = icon.replace('%size%', 'sz=128')
            cur['iconUrl'] = icon
        cur['repositoryUrl'] = 'https://github.com/' + repo
        if cur.get('internalName') != it.get('internalName'):
            print('CASE %s -> %s' % (cur.get('internalName'), it.get('internalName')))
            cur['internalName'] = it.get('internalName')
            cur['name'] = it.get('name', it.get('internalName'))
        print('UYGULANDI flip %s -> %s' % (cur.get('internalName'), repo))
    for _, (repo, it, tarih) in yeniler:
        try:
            blob = raw_bytes(it['url'])
            if 'sha256-' + hashlib.sha256(blob).hexdigest() != it['fileHash'] or len(blob) != it['fileSize']:
                raise ValueError('hash/boyut tutmadi')
        except Exception as ex:
            hatali.append('%s (%s, yeni): %s' % (it.get('internalName'), repo, ex))
            continue
        icon = it.get('iconUrl', '')
        if '%size%' in icon:
            icon = icon.replace('%size%', 'sz=128')
        data.append({'url': it['url'], 'status': 1, 'version': it.get('version', 1),
                     'name': it.get('name', it.get('internalName')), 'internalName': it.get('internalName'),
                     'authors': it.get('authors', []), 'description': it.get('description', ''),
                     'fileSize': it.get('fileSize'), 'repositoryUrl': 'https://github.com/' + repo,
                     'language': it.get('language'), 'tvTypes': it.get('tvTypes', []),
                     'iconUrl': icon, 'apiVersion': it.get('apiVersion', 3), 'fileHash': it.get('fileHash')})
        print('UYGULANDI yeni %s (%s)' % (it.get('internalName'), repo))
    data.sort(key=lambda p: (p.get('internalName') or '').casefold())
    # Atomik yazma: once gecici dosyaya, sonra os.replace (yarim yazim olmaz).
    tmp = PLUGINS_PATH + '.tmp'
    json.dump(data, io.open(tmp, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=2)
    io.open(tmp, 'a', encoding='utf-8').write('\n')
    os.replace(tmp, PLUGINS_PATH)
    print('plugins.json yazildi.')
    if hatali:
        print('=== HATALI-ATLANDI (indirilemedi/hash tutmadi) (%d) ===' % len(hatali))
        print('\n'.join('  ' + c for c in hatali))
    try:
        subprocess.run([sys.executable, os.path.join(REPO_DIR, 'registry.py'),
                        '--sync', '--render', '--write'], check=True)
        print('registry.json ve DEPO-BILGILERI.md otomatik senkronize edildi.')
    except Exception as ex:
        print('UYARI: registry senkronizasyonu tetiklenemedi: %s' % ex)
    print('Not: yeni kayitlar icin tablo satiri elle eklenmeli; jsDelivr purge sonraki adim.')
    if hatali:
        print('HATALI kayitlar vardi (exit 1).')
        sys.exit(1)


if __name__ == '__main__':
    main()
