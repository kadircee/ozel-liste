# -*- coding: utf-8 -*-
"""audit.py: tum kaynak repolari tarar, internalName'e gore gruplar, en yeni tarihi secer.

Kullanim:
    python audit.py --check    # sadece rapor (varsayilan; degisiklik varsa exit 1)
    python audit.py --apply    # guvenli durumlari uygula (belirsizler rapora duser)

Kurallar (DEPO-BILGILERI.md Tarih Takip Kurali):
    - Anahtar = normalize(internalName): TR duzeltmeli casefold (İ->i, I->ı).
    - Yasaklilar (Istenmeyenler tablosu) sonsuza dek yasak: asla eklenmez/degistirilmez.
    - Kapali (status:0) satirlar ve esit-tarih tie'lar OTOMATIK karar disi: sorulur.
    - Yeni site tercihen tr + {Movie,TvSeries,Documentary}; uymayanlar rapora duser.
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
import urllib.request

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
PLUGINS_PATH = os.path.join(REPO_DIR, 'plugins.json')
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


def api_json(url, tok):
    req = urllib.request.Request(url, headers={'Authorization': 'Bearer ' + tok,
                                               'Accept': 'application/vnd.github+json',
                                               'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode('utf-8'))


def raw_json(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read().decode('utf-8'))


def raw_bytes(url):
    req = urllib.request.Request(url, headers={'User-Agent': UA})
    with urllib.request.urlopen(req, timeout=120) as r:
        return r.read()


def main():
    ap = argparse.ArgumentParser(description='ozel-liste kaynak denetimi')
    ap.add_argument('--apply', action='store_true', help='guvenli durumlari uygula')
    args = ap.parse_args()
    tok = token()

    depo = io.open(DEPO_PATH, encoding='utf-8').read().replace('\r\n', '\n')

    # Yasaklilar: Istenmeyenler tablosu ilk sutunu
    banned = set()
    in_zone = False
    for line in depo.split('\n'):
        if re.search(r'#+ .*Istenmeyenler', line):
            in_zone = True
            continue
        if in_zone and line.startswith('## '):
            break
        if in_zone:
            m = re.match(r'^\| (.*?) \|', line)
            if m and not m.group(1).startswith('Eklenti') and not set(m.group(1)) <= set('-| '):
                banned.add(norm(re.sub(r'^[^\w]+', '', m.group(1)).strip()))
    print('yasakli sayisi: %d' % len(banned))

    # Kaynak evren: tablo Kaynak sutunu + plugins.json url'leri
    repos = set()
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
            fn = it.get('url', '').rsplit('/', 1)[-1]
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

    flips, closed, yeniler, elenen_yeni, baglar, guard = [], [], [], [], [], []
    for key in sorted(pool):
        grp = sorted(pool[key], key=lambda x: x[2], reverse=True)
        top_tarih = grp[0][2]
        kazananlar = [g for g in grp if g[2] == top_tarih]
        cur = listed_by_norm.get(key)
        if cur:
            m = re.match(r'https://raw\.githubusercontent\.com/([^/]+)/([^/]+)/builds/', cur.get('url', ''))
            cur_repo = (m.group(1) + '/' + m.group(2)) if m else '?'
            cur_hist = [g for g in grp if g[0] == cur_repo]
            cur_tarih = cur_hist[0][2] if cur_hist else None
            if cur_tarih and top_tarih > cur_tarih:
                w = kazananlar[0]
                if len(kazananlar) > 1:
                    baglar.append('%s: %s' % (cur.get('internalName'), ', '.join('%s %s' % (r, t) for r, _, t in kazananlar)))
                elif cur.get('status') == 0:
                    closed.append('%s: %s %s -> %s %s (status:0, sorulacak)' % (
                        cur.get('internalName'), cur_repo, cur_tarih, w[0], top_tarih))
                else:
                    flips.append((cur, w))
        else:
            if key in banned:
                guard.append('%s yasakli, kaynaklarda goruldu ama eleniyor' % grp[0][1].get('internalName'))
                continue
            if len(kazananlar) > 1:
                baglar.append('%s (yeni): %s' % (grp[0][1].get('internalName'), ', '.join('%s %s' % (r, t) for r, _, t in kazananlar)))
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
    print('=== KAPALI SORULACAK (%d) ===' % len(closed))
    print('\n'.join('  ' + c for c in closed) or '  (yok)')
    print('=== YENI SITE (%d) ===' % len(yeniler))
    for repo, it, tarih in yeniler:
        print('  %s (%s) %s' % (it.get('internalName'), repo, tarih))
    print('=== FILTRE-DISI YENI (%d) ===' % len(elenen_yeni))
    print('\n'.join('  ' + c for c in elenen_yeni) or '  (yok)')
    print('=== TIE SORULACAK (%d) ===' % len(baglar))
    print('\n'.join('  ' + c for c in baglar) or '  (yok)')

    action = flips + [(None, w) for w in yeniler]
    if not args.apply:
        if action or closed or baglar or elenen_yeni:
            print('\n--apply siz calisti, yazilmadi (exit 1).')
            sys.exit(1)
        print('\nYapilacak is yok.')
        return

    # --apply: sadece flips + yeniler, hash dogrulamali
    data = listed
    for cur, (repo, it, tarih) in flips:
        blob = raw_bytes(it['url'])
        assert 'sha256-' + hashlib.sha256(blob).hexdigest() == it['fileHash'] and len(blob) == it['fileSize'], \
            'hash/boyut tutmadi: %s' % it.get('internalName')
        for f in ['url', 'version', 'fileSize', 'fileHash', 'description', 'authors', 'language', 'tvTypes']:
            cur[f] = it[f]
        cur['repositoryUrl'] = 'https://github.com/' + repo
        if cur.get('internalName') != it.get('internalName'):
            print('CASE %s -> %s' % (cur.get('internalName'), it.get('internalName')))
            cur['internalName'] = it.get('internalName')
            cur['name'] = it.get('name', it.get('internalName'))
        print('UYGULANDI flip %s -> %s' % (cur.get('internalName'), repo))
    for _, (repo, it, tarih) in yeniler:
        blob = raw_bytes(it['url'])
        assert 'sha256-' + hashlib.sha256(blob).hexdigest() == it['fileHash'] and len(blob) == it['fileSize'], \
            'hash/boyut tutmadi: %s' % it.get('internalName')
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
    json.dump(data, io.open(PLUGINS_PATH, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=2)
    io.open(PLUGINS_PATH, 'a', encoding='utf-8').write('\n')
    print('plugins.json yazildi; tablo yamasi + purge elle/sonraki adim.')


if __name__ == '__main__':
    main()
