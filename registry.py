# -*- coding: utf-8 -*-
"""Kayit Durumu Veri Modeli (Secim) araclari — Zero-Maintenance / Pure Mirror.

Model: her kayit tek eksene sahiptir.
    Secim  : aktif | duplicate | istenmeyen   -> plugins.json'a giriyor mu?
Kazanan: grup icinde en buyuk kaynak_tarih (Tarih Takip Kurali; versiyon kriter degil).

`status` (acik/kapali) bilgisi kaynaga aittir: update.py kaynagin
builds/plugins.json dosyasinda ne yayinliyorsa onu birebir yansitir
(Pure Mirror). Bu depo site canliligi (Saglik) takibi yapmaz.

Kaynaklar:
    registry.json      -> makine-okur asil kayit (bu arac uretir)
    DEPO-BILGILERI.md  -> "Tum Repolar" tablosu (uretilen blok) + "Istenmeyenler" tablosu
    plugins.json       -> yayindaki kayitlar; "aktif" kumesi buradan dogrulanir

Kullanim:
    python registry.py --sync              # tablolar + plugins.json -> registry.json
    python registry.py --check             # sema + kume + tarih denetimi (ihlalde exit 1)
    python registry.py --render            # tabloyu uretir, ekrana yazar
    python registry.py --render --write    # isaretli blogu uretilen tabloyla degistirir
"""
import argparse
import io
import json
import os
import re
import sys

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
DEPO = os.path.join(REPO_DIR, 'DEPO-BILGILERI.md')
PLUGINS = os.path.join(REPO_DIR, 'plugins.json')
REGISTRY = os.path.join(REPO_DIR, 'registry.json')

BEGIN = '<!-- KAYIT-DURUMU:OTOMATIK-BASLANGIC -->'
END = '<!-- KAYIT-DURUMU:OTOMATIK-SON -->'

HEADER = ['#', 'Eklenti', 'Kaynak', 'Site (domain)', 'v', 'Kaynak Tarih', 'Bizim Tarih',
          'Seçim', 'Not']
SEÇIM = ('aktif', 'duplicate', 'istenmeyen')

SECIM_TR = {'aktif': 'Aktif', 'duplicate': 'Duplicate', 'istenmeyen': 'İstenmeyen'}
# Hucre metni -> slug; ASCII/aksanli eski bicimler geriye uyumlu kabul edilir.
CELL_SECIM = {'Aktif': 'aktif', 'aktif': 'aktif', 'Duplicate': 'duplicate', 'duplicate': 'duplicate',
              'İstenmeyen': 'istenmeyen', 'Istenmeyen': 'istenmeyen', 'istenmeyen': 'istenmeyen'}


def norm(s):
    value = (s or '').replace('\u0130', 'i').replace('I', '\u0131').casefold()
    # Kaynaklar WebteIzle/InatBox adlarini buyuk I ile de yayinliyor.
    if value in {'webteizle', 'webte\u0131zle'}:
        return 'webteizle'
    if value in {'inatbox', '\u0131natbox'}:
        return 'inatbox'
    return value


def group_key(name, domain):
    """Ayni siteyi farkli internalName kullanan kaynaklarda birlestirir."""
    d = (domain or '').lower().strip()
    if d and d != 'raw.githubusercontent.com':
        return 'site:' + d
    return 'name:' + norm(name)


def clean_note(text):
    """Eski tek 'Durum' hucresinden serbest metni ayiklar (bastaki gosterge
    isaretleri ve durum kelimesi cikarilir; parantezli gecmis notu korunur)."""
    t = re.sub(r'^[^\w\(]+', '', text or '').strip()
    for w in ('\u00c7al\u0131\u015f\u0131yor', '\u00c7al\u0131\u015fm\u0131yor', 'Duplicate',
              '\u0130stenmeyen', 'Eklenebilir'):
        if t.lower().startswith(w.lower()):
            return t[len(w):].strip()
    return t


def parse_depo():
    """DEPO-BILGILERI.md'yi okur: liste satirlari + Istenmeyenler tablosu.
    Tablo uc formati da okuyabilir (eski tek 'Durum' / 10 sutunlu Secim+Saglik+Not /
    9 sutunlu Secim+Not); uretim her zaman 9 sutunludur."""
    lines = io.open(DEPO, encoding='utf-8').read().replace('\r\n', '\n').split('\n')
    hdr = next(i for i, l in enumerate(lines) if l.startswith('| # |'))
    new_fmt = ('Seçim' in lines[hdr]) or ('Secim' in lines[hdr])
    has_saglik = ('Sağlık' in lines[hdr]) or ('Saglik' in lines[hdr])
    zone = next(i for i, l in enumerate(lines)
                if re.match(r'^#+\s+.*(Istenmeyenler|İstenmeyenler)', l))
    liste = []
    for i in range(hdr, zone):
        l = lines[i]
        m = re.match(r'^\| (\d+) \|', l)
        if not m:
            continue
        c = [x.strip() for x in l.strip().strip('|').split('|')]
        r = {'line': i + 1, 'order': int(m.group(1)), 'name_cell': c[1],
             'name': re.sub(r'^[^A-Za-z0-9]+', '', c[1]), 'repo_cell': c[2], 'site_cell': c[3],
             'version': c[4], 'kaynak_tarih': c[5], 'bizim_tarih': c[6]}
        r['repo'] = (re.search(r'github\.com/([^)]+)', c[2]) or [None, ''])[1]
        r['domain'] = (re.search(r'\[([^\]]+)\]', c[3]) or [None, c[3]])[1]
        if new_fmt:
            r['secim'] = CELL_SECIM.get((c[7] if len(c) > 7 else '').strip(), '')
            if has_saglik:
                # Gecis: eski 10 sutunlu tablo (Saglik sutunu yoksayilir).
                r['not'] = c[9] if len(c) > 9 else ''
            else:
                r['not'] = c[8] if len(c) > 8 else ''
        else:
            r['secim'], r['not'] = None, clean_note(c[7] if len(c) > 7 else '')
        liste.append(r)
    zone_rows = []
    for i in range(zone, len(lines)):
        l = lines[i]
        if i > zone and l.startswith('## '):
            break
        if l.startswith('| ') and 'Eklenti' not in l:
            c = [x.strip() for x in l.strip().strip('|').split('|')]
            if len(c) < 3:
                continue
            zone_rows.append({'name': re.sub(r'^[^A-Za-z0-9]+', '', c[0]),
                              'repo': (re.search(r'github\.com/([^)]+)', c[1]) or [None, ''])[1],
                              'domain': (re.search(r'\[([^\]]+)\]', c[2]) or [None, c[2]])[1],
                              'repo_cell': c[1], 'site_cell': c[2],
                              'dil': c[3] if len(c) > 3 else '', 'tur': c[4] if len(c) > 4 else ''})
    return liste, zone_rows, new_fmt


def plugins_index():
    """plugins.json'i (normalize isim -> kayitlar) olarak indeksler."""
    data = json.load(io.open(PLUGINS, encoding='utf-8'))
    idx = {}
    for p in data:
        repo = (re.match(r'https://raw\.githubusercontent\.com/([^/]+/[^/]+)/builds/', p.get('url', '')) or [None, ''])[1]
        idx.setdefault(norm(p.get('internalName')), []).append({'repo': repo})
    return idx, data


def sync():
    """Tablolar + plugins.json -> registry sozlugu. 'Aktif' kumesi plugins.json'dan
    TURETILIR: dosyada olan kayit aktif, olmayan duplicate. Saglik/status izlenmez."""
    liste, zone, _ = parse_depo()
    idx, _ = plugins_index()
    groups = {}
    for r in liste:
        k = group_key(r['name'], r['domain'])
        c = {'name': r['name'], 'listed': True, 'order': r['order'], 'source': r['repo'],
             'source_cell': r['repo_cell'], 'site_cell': r['site_cell'], 'domain': r['domain'],
             'version': r['version'], 'kaynak_tarih': r['kaynak_tarih'], 'bizim_tarih': r['bizim_tarih'],
             'not': r['not']}
        hit = [h for h in idx.get(norm(r['name']), []) if h['repo'] == r['repo']]
        c['secim'] = 'aktif' if hit else 'duplicate'
        groups.setdefault(k, {'name': r['name'], 'candidates': []})['candidates'].append(c)
    for z in zone:
        k = norm(z['name'])
        groups.setdefault(k, {'name': z['name'], 'candidates': []})['candidates'].append(
            {'name': z['name'], 'listed': False, 'source': z['repo'], 'source_cell': z['repo_cell'],
             'site_cell': z['site_cell'], 'domain': z['domain'], 'version': None,
             'kaynak_tarih': None, 'bizim_tarih': None, 'secim': 'istenmeyen',
             'not': (z['dil'] + ' ' + z['tur']).strip()})
    return {'version': 1, 'groups': {k: groups[k] for k in sorted(groups)}}


def liste_rows(reg):
    rows = [c for g in reg['groups'].values() for c in g['candidates'] if c.get('listed')]
    return sorted(rows, key=lambda c: c['order'])


def validate(reg):
    """Sema + kume + tarih denetimi. (errors, conflicts) dondurur."""
    errors, conflicts = [], []
    for k, g in sorted(reg['groups'].items()):
        aktif = [c for c in g['candidates'] if c['secim'] == 'aktif']
        if len(aktif) > 1:
            errors.append('%s: %d Aktif kayit var (en fazla 1)' % (g['name'], len(aktif)))
        for c in g['candidates']:
            if c['secim'] not in SEÇIM:
                errors.append('%s/%s: gecersiz secim %r' % (g['name'], c.get('source'), c['secim']))
        listed = [c for c in g['candidates'] if c.get('listed') and c['kaynak_tarih']]
        if listed and aktif:
            en = max(c['kaynak_tarih'] for c in listed)
            if aktif[0]['kaynak_tarih'] < en:
                conflicts.append((g['name'], aktif[0]['source'], aktif[0]['kaynak_tarih'], en))
    # kume denetimi: aktif kayitlar == plugins.json
    idx, _ = plugins_index()
    reg_aktif = {(norm(c['name']), c['source']) for g in reg['groups'].values()
                 for c in g['candidates'] if c['secim'] == 'aktif'}
    pj = {(k, h['repo']) for k, hs in idx.items() for h in hs}
    for key in sorted(set(pj) | set(reg_aktif)):
        if key not in reg_aktif:
            errors.append('plugins.json\'da var ama registry\'de Aktif yok: %s (%s)' % key)
        elif key not in pj:
            errors.append('registry\'de Aktif ama plugins.json\'da yok: %s (%s)' % key)
    return errors, conflicts


def render(reg):
    def cell(x):
        # markdown tablo hucresi: pipe kacisi + satir sonu temizligi
        return ('' if x is None else str(x)).replace('|', '/').replace('\n', ' ').strip()

    out = ['| ' + ' | '.join(HEADER) + ' |', '|' + '|'.join(['---'] * len(HEADER)) + '|']
    for c in liste_rows(reg):
        out.append('| %d | %s | %s | %s | %s | %s | %s | %s | %s |' % (
            c['order'], cell(c['name']), cell(c['source_cell']), cell(c['site_cell']),
            cell(c['version']), cell(c['kaynak_tarih']), cell(c['bizim_tarih']),
            SECIM_TR[c['secim']], cell(c['not'])))
    return '\n'.join(out)


def write_block(block):
    """Uretilen tabloyu isaretli blok olarak DEPO-BILGILERI.md'ye yazar.
    Isaretci yoksa mevcut tablonun etrafina yerlestirir (tek seferlik gecis)."""
    lines = io.open(DEPO, encoding='utf-8').read().replace('\r\n', '\n').split('\n')
    hdr = next(i for i, l in enumerate(lines) if l.startswith('| # |'))
    try:
        blk_s = next(i for i, l in enumerate(lines) if l.strip() == BEGIN)
        blk_e = next(i for i, l in enumerate(lines) if l.strip() == END)
        if not (blk_s <= hdr <= blk_e):
            raise StopIteration
    except StopIteration:
        blk_s = blk_e = None
    if blk_s is not None:
        lines[blk_s:blk_e + 1] = [BEGIN] + block.split('\n') + [END]
        yeni = '\n'.join(lines)
    else:
        last = hdr
        for i in range(hdr, len(lines)):
            if lines[i].startswith('|'):
                last = i
            elif lines[i].strip() and i > hdr:
                break
        lines[hdr:last + 1] = [BEGIN] + block.split('\n') + [END]
        yeni = '\n'.join(lines)
    io.open(DEPO, 'w', encoding='utf-8', newline='\n').write(yeni)


def load_registry():
    return json.load(io.open(REGISTRY, encoding='utf-8'))


def save_registry(reg):
    io.open(REGISTRY, 'w', encoding='utf-8', newline='\n').write(
        json.dumps(reg, ensure_ascii=False, indent=2) + '\n')


def drift(reg):
    """Tablo registry ile ayni mi? Yalnizca secim ekseni denetlenir."""
    liste, _, new_fmt = parse_depo()
    if not new_fmt:
        return None
    # Sira numaralari grup icinde tekrar edebilir; kimlik olarak ad + kaynak
    # kullanilmazsa duplicate satirlarinin durumu yanlis eslesir.
    reg_rows = {(norm(c['name']), c['source']): c for c in liste_rows(reg)}
    out = []
    for r in liste:
        c = reg_rows.get((norm(r['name']), r['repo']))
        if not c:
            out.append('tablo satir %d (%s): registry\'de yok' % (r['order'], r['name']))
        elif r['secim'] != c['secim']:
            out.append('tablo satir %d (%s): tablo=%s registry=%s' % (
                r['order'], r['name'], r['secim'], c['secim']))
    return out


def main():
    ap = argparse.ArgumentParser(description='Kayit Durumu Veri Modeli (Secim) araclari — Pure Mirror')
    ap.add_argument('--sync', action='store_true', help='tablolar + plugins.json -> registry.json')
    ap.add_argument('--check', action='store_true', help='sema + kume + tarih denetimi (ihlalde exit 1)')
    ap.add_argument('--render', action='store_true', help='tabloyu uretir (dosyaya yazmaz)')
    ap.add_argument('--write', action='store_true', help='--render ile: isaretli blok yazilir')
    args = ap.parse_args()
    if not (args.sync or args.check or args.render):
        ap.print_help()
        return

    if args.sync:
        reg = sync()
        save_registry(reg)
        say = {'aktif': 0, 'duplicate': 0, 'istenmeyen': 0}
        for g in reg['groups'].values():
            for c in g['candidates']:
                say[c['secim']] += 1
        print('registry.json yazildi: %d grup | aktif=%d duplicate=%d istenmeyen=%d' % (
            len(reg['groups']), say['aktif'], say['duplicate'], say['istenmeyen']))

    if args.check or args.render:
        if not os.path.exists(REGISTRY):
            print('HATA: registry.json yok (once --sync calistir)')
            sys.exit(2)
        reg = load_registry()
        if args.check:
            errors, conflicts = validate(reg)
            print('\n=== SEMA + KUME DENETIMI ===')
            if errors:
                for e in errors:
                    print('  IHLAL: ' + e)
            else:
                print('  OK: sema gecerli; aktif kumesi plugins.json ile birebir')
            d = drift(reg)
            if d:
                print('=== TABLO <-> REGISTRY UYUSMAZLIGI (%d) ===' % len(d))
                for x in d:
                    print('  ' + x)
            elif d == []:
                print('  OK: tablo registry ile uyumlu')
            print('=== TARIH TAKIP KURALI: Aktif kayit en yeni mi? (%d celiski) ===' % len(conflicts))
            for name, src, t, en in conflicts:
                print('  %-16s aktif=%-34s %s  ->  grubun en yenisi %s' % (name, src, t, en))
            if not conflicts:
                print('  (yok)')
            if errors or conflicts:
                print('\nSONUC: ihlal/celiski var (exit 1). Tarih celiskileri karar bekler; sema ihlali duzeltilmeli.')
                sys.exit(1)
            print('\nSONUC: temiz.')
        if args.render:
            block = render(reg)
            if args.write:
                write_block(block)
                print('\nDEPO-BILGILERI.md: isaretli blok guncellendi (%d satir)' % (block.count('\n') + 1))
            else:
                print('\n--- URETILEN TABLO (yazilmadi) ---')
                print(block)


if __name__ == '__main__':
    main()
